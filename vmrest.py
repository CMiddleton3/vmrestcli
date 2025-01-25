"""
VMware REST API Module

This module provides a set of functions for interacting with the VMware REST server.
"""

import configparser
import argparse
import sys
import time
import platform
import debugpy
from pathlib import Path
import requests
from requests.auth import HTTPBasicAuth

from vmware_server import VMWareServer

# debugpy.breakpoint()

# Constants for default values
DEFAULT_BASE_URL = "http://127.0.0.1:8697"

if platform.system() == "Windows":
    DEFAULT_VMREST_EXE = r"C:\Program Files (x86)\VMware\VMware Workstation\vmrest.exe"
else:
    DEFAULT_VMREST_EXE = r"/mnt/c/Program Files (x86)/VMware/VMware Workstation/vmrest.exe"

# Load settings from vmworkstation.ini
config = configparser.ConfigParser()
config.read("vmworkstation.ini")

# Set defaults if not provided in the ini file.
BASE_URL = config.get("vmware", "base_url", fallback=DEFAULT_BASE_URL)
USERNAME = config.get("vmware", "username", fallback="")
PASSWORD = config.get("vmware", "password", fallback="")
VMWARE_REST_EXE = config.get("vmware", "vmrest_exe", fallback=DEFAULT_VMREST_EXE)


def display_title_bar() -> None:
    """
    Display the title bar for the VMware WorkStation Rest application.
    """
    title = "VMware WorkStation Rest"
    print("=" * len(title))
    print(title)
    print("=" * len(title))


def configure_vmworkstation_ini() -> None:
    """
    Configure the vmworkstation.ini file with user input.
    """
    print("Configure vmworkstation.ini file:")
    config["vmware"] = {}

    base_url = input(f"Enter base URL (Enter for Default: {DEFAULT_BASE_URL}): ").strip() or DEFAULT_BASE_URL
    config["vmware"]["base_url"] = base_url

    username = input("Enter username: ").strip()
    config["vmware"]["username"] = username

    password = input("Enter password: ").strip()
    config["vmware"]["password"] = password

    vmrest_exe = input(f"Enter path to vmrest.exe (Enter for Default: {DEFAULT_VMREST_EXE}): ").strip() or DEFAULT_VMREST_EXE
    config["vmware"]["vmrest_exe"] = vmrest_exe

    with open("vmworkstation.ini", "w") as configfile:
        config.write(configfile)
        print("Configuration saved to vmworkstation.ini")


def get_all_vms():
    """
    Retrieves a list of all virtual machines available in the VMware REST server.
    
    Returns:
        dict: A dictionary containing information about each virtual machine, including its ID and name.
    """
    headers = {"Accept": "application/vnd.vmware.vmw.rest-v1+json"}
    try:
        response = requests.get(
            BASE_URL + "/api/vms",
            headers=headers,
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching VMs: {e}")
        return []


def show_all_vm_ids():
    """
    Displays a list of unique IDs for all virtual machines available in the VMware REST server.
    
    Returns:
        str: A comma-separated list of virtual machine IDs.
    """
    vms = get_all_vms()
    print()
    for vm in vms:
        vm_name = get_vm_name_by_ids(vm.get("id"))
        print(f"VM Name {vm_name} VM Path: {vm.get('path')}, VM ID: {vm.get('id')}")
    return vms


def get_vm_name_by_ids(vm_id):
    """
    Retrieves the name of a specific virtual machine based on its ID.

    Args:
        vm_id (str): The ID of the virtual machine to retrieve its name for.

    Returns:
        str: The name of the virtual machine associated with the specified ID.
    """
    vms = get_all_vms()
    for vm in vms:
        if vm.get("id") == vm_id:
            # Extract the file name
            vm_path = vm.get("path")
            vm_path = vm_path.replace("\\", "/")
            windows_path = Path(vm_path)
            vm_name = windows_path.name

            # Remove the hyphen and the '.vmx' extension
            vm_name = vm_name.replace("-", " ").replace(".vmx", "").capitalize()

            return vm_name


def get_vm_info(vm_id):
    """
    Retrieves information about a specific virtual machine.

    Args:
        vm_id (str): The ID of the virtual machine to retrieve information for.

    Returns:
        dict: A dictionary containing information about the virtual machine, including its name, working directory, and guest OS.
    """
    config_param = ["guestOS", "displayName", "workingDir", "guestInfo.detailed.data"]

    for param in config_param:
        MAX_OUTPUT_LENGTH = 120
        ip_url = f"{BASE_URL}/api/vms/{vm_id}/params/{param}"
        headers = {"Accept": "application/vnd.vmware.vmw.rest-v1+json"}
        try:
            param_response = requests.get(
                ip_url, headers=headers, auth=HTTPBasicAuth(USERNAME, PASSWORD),
                timeout=60
            )
            param_response.raise_for_status()
            param_results = param_response.json()
            print(
                f"   {param.capitalize()} : {param_results.get('value', 'Unknown')[:MAX_OUTPUT_LENGTH]}"
            )
        except requests.exceptions.RequestException as e:
            print(f"Error fetching config param {param} for {vm_id}: {e}")


def get_vm_ip(vm_id):
    """
    Retrieves the IP address of the current guest operating system in the VMware REST server.

    Returns:
        str: The IP address of the guest operating system.
    """
    ip_url = f"{BASE_URL}/api/vms/{vm_id}/ip"
    headers = {"Accept": "application/vnd.vmware.vmw.rest-v1+json"}
    try:
        ip_response = requests.get(
            ip_url, headers=headers, auth=HTTPBasicAuth(USERNAME, PASSWORD),
            timeout=60
        )
        ip_response.raise_for_status()
        ip_address = ip_response.json().get("ip", "Unknown")
        print(f"   IP Address: {ip_address}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching IP address for VM {vm_id}: {e}")


def get_vm_mac(vm_id):
    """
    Retrieves the MAC address of the current network interface in the VMware REST server.

    Returns:
        str: The MAC address of the network interface.
    """
    nic_url = f"{BASE_URL}/api/vms/{vm_id}/nic"
    headers = {"Accept": "application/vnd.vmware.vmw.rest-v1+json"}
    try:
        nic_response = requests.get(
            nic_url, headers=headers, auth=HTTPBasicAuth(USERNAME, PASSWORD),
            timeout=60
        )
        nic_response.raise_for_status()
        nics = nic_response.json().get("nics", [])
        for nic in nics:
            mac_address = nic.get("macAddress", "Unknown")
            print(f"   MAC Address (NIC {nic.get('index', 'Unknown')}): {mac_address}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching MAC address for VM {vm_id}: {e}")


def get_vm_setting(vm_id):
    """
    Retrieves a specific setting for a virtual machine based on its ID and parameter name.

    Args:
        param (str): The name of the setting to retrieve.

    Returns:
        str: The value of the specified setting.
    """
    settings_url = f"{BASE_URL}/api/vms/{vm_id}"
    headers = {"Accept": "application/vnd.vmware.vmw.rest-v1+json"}
    try:
        settings_response = requests.get(
            settings_url, headers=headers, auth=HTTPBasicAuth(USERNAME, PASSWORD),
            timeout=60
        )
        settings_response.raise_for_status()
        settings = settings_response.json()
        processors = settings.get("cpu", {}).get("processors", "Unknown")
        memory = settings.get("memory", "Unknown")
        print(f"   Processors: {processors}")
        print(f"   Memory: {memory} MB")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching settings for VM {vm_id}: {e}")


def display_vms(vms, show_all_info=False):
    """
    Retrieves and displays information about a list of virtual machines. Information displayed includes the machine's name, path, ID, power state, IP address (if applicable), MAC addresses for each network interface (if applicable), processors, memory usage, CPU cores, guest OS type, display name, working directory, current snapshot status, and any additional custom settings available in VMware.
    If all_info is True it will also retrieve information about the virtual machine's hardware configuration such as host bus adapter count and model (if applicable), network adapters connected to each interface for both Ethernet/LAN & Fibre Channel, connection status of various devices like CD-ROM drive(s)
    Args:
        vms (list): A list containing information about available virtual machines. Each entry is a dictionary with keys including 'id', 'path', and other VM-related info.
        show_all_info (bool): If True, displays more detailed hardware configuration of each VM in addition to the standard vm details displayed by default. Defaults to False.
    Returns:
        None
    """
    if not vms:
        print("No VMs available.")
        return

    for i, vm in enumerate(vms, start=1):
        vm_id = vm.get("id")
        vm_path = vm.get("path")
        vm_name = get_vm_name_by_ids(vm_id)
        print(f"\n{i}. VM Name: {vm_name}")
        print(f"   VM Path: {vm_path}")
        print(f"   VM ID: {vm_id}")

        power_state = get_vm_power_state(vm_id)
        print(f"   Power State: {power_state}")

        if power_state == "poweredOn":
            get_vm_ip(vm_id)
            get_vm_mac(vm_id)
            get_vm_setting(vm_id)

        if show_all_info:
            get_vm_info(vm_id)
    time.sleep(3)


def get_vm_power_state(vm_id):
    """
    Retrieves the power state of the current guest operating system in the VMware REST server.

    Returns:
        str: The power state of the guest operating system ("on" or "off").
    """
    try:
        power_url = f"{BASE_URL}/api/vms/{vm_id}/power"
        headers = {
            "Accept": "application/vnd.vmware.vmw.rest-v1+json",
            "Content-Type": "application/vnd.vmware.vmw.rest-v1+json",
        }
        power_response = requests.get(
            power_url, headers=headers, auth=HTTPBasicAuth(USERNAME, PASSWORD),
            timeout=60
        )
        power_response.raise_for_status()
        return power_response.json().get("power_state", "Unknown")
    except requests.RequestException as e:
        print(f"Error fetching power state for VM {vm_id}: {e}")
        return "Unknown"


def power_on_off(vm_id, action):
    """
    Powers on or off a virtual machine based on the specified action.

    Args:
        vm_id (str): The ID of the virtual machine to power.
        action (str): The action to perform ("on" or "off").

    Returns:
        bool: True if the action was successful, False otherwise.
    """
    url = f"{BASE_URL}/api/vms/{vm_id}/power"
    headers = {
        "Accept": "application/vnd.vmware.vmw.rest-v1+json",
        "Content-Type": "application/vnd.vmware.vmw.rest-v1+json",
    }
    payload = action
    vm_name = get_vm_name_by_ids(vm_id)

    if action == "on" and get_vm_power_state(vm_id) == "poweredOn":
        print(f"VM {vm_name} {vm_id} is Already Powered On!")
        return False

    if action == "off" and get_vm_power_state(vm_id) == "poweredOff":
        print(f"VM {vm_name} {vm_id} is Already Powered Off!")
        return False

    try:
        response = requests.put(
            url, headers=headers, data=payload, auth=HTTPBasicAuth(USERNAME, PASSWORD),
            timeout=60
        )
        response.raise_for_status()
        power_state = response.json().get("power_state", "Unknown")
        # vm_name = get_vm_name_by_ids(vm_id)
        print(f"VM {vm_name} {vm_id} is now {power_state}.")
    except requests.exceptions.RequestException as e:
        print(f"Error changing power state for VM {vm_id}: {e}")


def get_all_networks():
    """
    Retrieves a list of all network interfaces available in the VMware REST server.

    Returns:
        dict: A dictionary containing information about each network interface, including its ID and name.
    """
    network_url = f"{BASE_URL}/api/vmnet"
    headers = {"Accept": "application/vnd.vmware.vmw.rest-v1+json"}
    try:
        response = requests.get(
            network_url, headers=headers, auth=HTTPBasicAuth(USERNAME, PASSWORD),
            timeout=60
        )
        response.raise_for_status()
        return response.json().get("vmnets", [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching networks: {e}")
        return []


def display_networks(networks):
    if not networks:
        print("No networks available.")
        return

    for i, net in enumerate(networks, start=1):
        print(f"\n{i}. Network Name: {net.get('name', 'Unknown')}")
        print(f"   Type: {net.get('type', 'Unknown')}")
        print(f"   DHCP: {net.get('dhcp', 'Unknown')}")
        print(f"   Subnet: {net.get('subnet', 'Unknown')}")
        print(f"   Mask: {net.get('mask', 'Unknown')}")


def menu(vmware_server):
    while True:
        print("\nMenu:")
        print("1. Show All VMs")
        print("2. Show Power State for VM by ID")
        print("3. Power On VM by ID")
        print("4. Power Off VM by ID")
        print("5. Show All Networks")
        print("6. Start VMware REST Server")
        print("7. Stop VMware REST Server")
        print("8. Configure VMare REST Server Username & Password")
        print("q. Quit")

        choice = input("Enter your choice: ").strip().lower()

        if choice == "1":
            vms = get_all_vms()
            if vms:
                display_vms(vms)
            else:
                print("No VMs found or error retrieving VMs.")

        elif choice == "2":
            show_all_vm_ids()
            print()
            vm_id = input("Enter VM ID: ").strip()
            print()
            power_state = get_vm_power_state(vm_id)
            vm_name = get_vm_name_by_ids(vm_id)
            print(f"Power state of {vm_name} VM {vm_id}: {power_state}")

        elif choice == "3":
            show_all_vm_ids()
            print()
            vm_id = input("Enter VM ID to power on: ").strip()
            print()
            power_on_off(vm_id, "on")
            print()

        elif choice == "4":
            show_all_vm_ids()
            print()
            vm_id = input("Enter VM ID to power off: ").strip()
            print()
            power_on_off(vm_id, "off")
            print()

        elif choice == "5":
            networks = get_all_networks()
            display_networks(networks)

        elif choice == "6":
            vmware_server.start_server()

        elif choice == "7":
            vmware_server.stop_server()
            
        elif choice == "8":
            vmware_server.configure_vmware_server()
            configure_vmworkstation_ini()


        elif choice in ["q", "Q"]:
            print("Exiting program.")
            break

        else:
            print("Invalid choice, please try again.")


def main():
    parser = argparse.ArgumentParser(description="VMware Workstation REST Interface")

    parser.add_argument("--show-vms", action="store_true", help="Show all VMs and quit")
    parser.add_argument(
        "--show-vms-ids", action="store_true", help="Show all VMs IDS and quit"
    )
    parser.add_argument(
        "--show-net", action="store_true", help="Show all networks and quit"
    )
    parser.add_argument(
        "--show-power-state",
        type=str,
        metavar="VM_ID",
        help="Show the current power state of a VM (requires VM_ID)",
    )
    parser.add_argument(
        "--power-on", type=str, metavar="VM_ID", help="Power on the VM (requires VM_ID)"
    )
    parser.add_argument(
        "--power-off",
        type=str,
        metavar="VM_ID",
        help="Power off the VM (requires VM_ID)",
    )
    parser.add_argument(
        "--start-server", action="store_true", help="Start the VMware REST server"
    )
    parser.add_argument(
        "--stop-server", action="store_true", help="Stop the VMware REST server"
    )
    parser.add_argument(
        "--go-live",
        action="store_true",
        help="Starts the VMware REST Server before running command",
    )
    parser.add_argument(
        "--go-off",
        action="store_true",
        help="Stop the VMware REST server after running a command",
    )
    parser.add_argument(
        "--configure", action="store_true", help="Configure vmworkstation.ini file"
    )

    args = parser.parse_args()

    vmware_server = VMWareServer(BASE_URL, VMWARE_REST_EXE)

    if args.configure:
        configure_vmworkstation_ini()
        sys.exit(0)

    display_title_bar()

    if args.start_server:
        vmware_server.start_server()
        sys.exit(0)

    if args.stop_server:
        vmware_server.stop_server()
        sys.exit(0)

    if args.show_vms:
        if args.go_live:
            vmware_server.start_server()
        vms = get_all_vms()
        display_vms(vms, show_all_info=True)
        if args.go_off:
            vmware_server.stop_server()
        sys.exit(0)

    if args.show_vms_ids:
        if args.go_live:
            vmware_server.start_server()
        vms = show_all_vm_ids()
        display_vms(vms, show_all_info=True)
        if args.go_off:
            vmware_server.stop_server()
        sys.exit(0)

    if args.show_power_state:
        power_state = get_vm_power_state(args.show_power_state)
        print(f"Power state of VM {args.show_power_state}: {power_state}")
        sys.exit(0)

    if args.power_on:
        if args.go_live:
            vmware_server.start_server()

        power_on_off(args.power_on, "on")

        if args.go_off:
            vmware_server.stop_server()
        sys.exit(0)

    if args.power_off:
        if args.go_live:
            vmware_server.start_server()

        power_on_off(args.power_off, "off")

        if args.go_off:
            vmware_server.stop_server()

        sys.exit(0)

    if args.show_net:
        networks = get_all_networks()
        display_networks(networks)
        sys.exit(0)

    menu(vmware_server)


if __name__ == "__main__":
    main()
