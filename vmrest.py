import requests
from requests.auth import HTTPBasicAuth
import configparser
import argparse
import subprocess
import sys

# Load settings from vmworkstation.ini
config = configparser.ConfigParser()
config.read('vmworkstation.ini')

# Set defaults if not provided in the ini file.
BASE_URL = config.get('vmware', 'base_url', fallback='http://127.0.0.1:8697/api')
USERNAME = config.get('vmware', 'username', fallback='')
PASSWORD = config.get('vmware', 'password', fallback='')
VMWARE_REST_EXE = config.get('vmware', 'vmrest_exe', fallback=r'/mnt/c/Program Files (x86)/VMware/VMware Workstation/vmrest.exe')

def display_title_bar():
    title = "VMware WorkStation Rest"
    print("=" * len(title))
    print(title)
    print("=" * len(title))

def configure_vmworkstation_ini():
    print("Configure vmworkstation.ini file:")
    config['vmware'] = {}
    
    default_base_url = 'http://127.0.0.1:8697/api'
    base_url = input(f"Enter base URL (Default: {default_base_url}): ").strip() or default_base_url
    config['vmware']['base_url'] = base_url

    username = input("Enter username: ").strip()
    while not username:
        username = input("Username cannot be empty. Enter username: ").strip()
    config['vmware']['username'] = username

    password = input("Enter password: ").strip()
    while not password:
        password = input("Password cannot be empty. Enter password: ").strip()
    config['vmware']['password'] = password

    default_vmrest_exe = r"/mnt/c/Program Files (x86)/VMware/VMware Workstation/vmrest.exe"
    vmrest_exe = input(f"Enter VMware REST Server executable path (Default: {default_vmrest_exe}): ").strip() or default_vmrest_exe
    config['vmware']['vmrest_exe'] = vmrest_exe
    
    with open('vmworkstation.ini', 'w') as configfile:
        config.write(configfile)
    
    print("Configuration updated successfully.")

def start_server():
    try:
        print(f"Starting VMware WorkStation REST server: {VMWARE_REST_EXE}")
        subprocess.Popen([VMWARE_REST_EXE]) 
    except FileNotFoundError as e:
        print(f"Error: VMware Workstation REST server executable not found at {VMWARE_REST_EXE}.")
        sys.exit(1)
    
    try:
        requests.get(BASE_URL, timeout=5)
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to VMware workstation REST server.")
        sys.exit(1)

def get_all_vms():
    headers = {'Accept': 'application/vnd.vmware.vmw.rest-v1+json'}
    try:
        response = requests.get(BASE_URL+"/vms", headers=headers, auth=HTTPBasicAuth(USERNAME, PASSWORD))
        response.raise_for_status()
        return response.json() 
    except requests.exceptions.RequestException as e:
        print(f"Error fetching VMs: {e}")
        return []

def display_vms(vms):
    if not vms:
        print("No VMs available.")
        return

    for i, vm in enumerate(vms, start=1):
        vm_id = vm.get("id")
        vm_path = vm.get("path")
        print(f"\n{i}. VM Path: {vm_path}")
        print(f"   VM ID: {vm_id}")
        
        power_url = f"{BASE_URL}/vms/{vm_id}/power"
        try:
            power_response = requests.get(power_url, headers={'Accept': 'application/vnd.vmware.vmw.rest-v1+json'}, auth=HTTPBasicAuth(USERNAME, PASSWORD))
            power_response.raise_for_status()
            power_state = power_response.json().get("power_state", "Unknown")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching power state for VM {vm_id}: {e}")
            power_state = "Error"

        print(f"   Power State: {power_state}")

def get_vm_power_state(vm_id):
    try:
        power_url = f"{BASE_URL}/vms/{vm_id}/power"
        headers = {'Accept': 'application/vnd.vmware.vmw.rest-v1+json'}
        power_response = requests.get(power_url, headers=headers, auth=HTTPBasicAuth(USERNAME, PASSWORD))
        power_response.raise_for_status()
        return power_response.json().get("power_state", "Unknown")
    except requests.RequestException as e:
        print(f"Error fetching power state for VM {vm_id}: {e}")
        return "Unknown"

def power_on_off(vm_id, action):
    url = f"{BASE_URL}/vms/{vm_id}/power"
    headers = {
        'Content-Type': 'application/vnd.vmware.vmw.rest-v1+json',
        'Accept': 'application/vnd.vmware.vmw.rest-v1+json'
    }
    payload = action

    try:
        response = requests.put(url, headers=headers, data=payload, auth=HTTPBasicAuth(USERNAME, PASSWORD))
        response.raise_for_status()
        power_state = response.json().get("power_state", "Unknown")
        print(f"VM {vm_id} is now {power_state}.")
    except requests.exceptions.RequestException as e:
        print(f"Error changing power state for VM {vm_id}: {e}")

def show_all_vm_ids():
    vms = get_all_vms()
    for vm in vms:
        print(f"VM Path: {vm.get('path')}, VM ID: {vm.get('id')}")

def menu():
    while True:
        print("\nMenu:")
        print("1. Show All VMs")
        print("2. Show All VM IDs")
        print("3. Show Power State for VM by ID")
        print("4. Power On VM by ID")
        print("5. Power Off VM by ID")
        print("6. Show All Networks")
        print("7. Start VMware REST Server")
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

        elif choice == "3":
            vm_id = input("Enter VM ID: ").strip()
            power_state = get_vm_power_state(vm_id)
            print(f"Power state of VM {vm_id}: {power_state}")
        
        elif choice == "4":
            vm_id = input("Enter VM ID to power on: ").strip()
            power_on_off(vm_id, "on")
        
        elif choice == "5":
            vm_id = input("Enter VM ID to power off: ").strip()
            power_on_off(vm_id, "off")
        
        elif choice == "6":
            networks = get_all_networks()
            display_networks(networks)
        
        elif choice == "7":
            start_server()
        
        elif choice in ["q", "Q"]:
            print("Exiting program.")
            break
        
        else:
            print("Invalid choice, please try again.")

def main():
    parser = argparse.ArgumentParser(description='VMware Workstation REST Interface')
    
    parser.add_argument('--show-vms', action='store_true', help='Show all VMs and quit')
    parser.add_argument('--show-vm-ids', action='store_true', help='Show all VM IDs and paths then quit')
    parser.add_argument('--show-power-state', type=str, metavar='VM_ID', help='Show the current power state of a VM (requires VM_ID)')
    parser.add_argument('--power-on', type=str, metavar='VM_ID', help='Power on the VM (requires VM_ID)')
    parser.add_argument('--power-off', type=str, metavar='VM_ID', help='Power off the VM (requires VM_ID)')
    parser.add_argument('--show-net', action='store_true', help='Show all networks and quit')
    parser.add_argument('--start-server', action='store_true', help='Start the VMware REST server')
    parser.add_argument('--configure', action='store_true', help='Configure vmworkstation.ini file')

    args = parser.parse_args()

    if args.configure:
        configure_vmworkstation_ini()
        sys.exit(0)

    display_title_bar()

    if args.start_server:
        start_server()

    if args.show_vms:
        vms = get_all_vms()
        display_vms(vms)
        sys.exit(0)

    if args.show_vm_ids:
        show_all_vm_ids()
        sys.exit(0)

    if args.show_power_state:
        power_state = get_vm_power_state(args.show_power_state)
        print(f"Power state of VM {args.show_power_state}: {power_state}")
        sys.exit(0)

    if args.power_on:
        power_on_off(args.power_on, "on")
        sys.exit(0)

    if args.power_off:
        power_on_off(args.power_off, "off")
        sys.exit(0)

    if args.show_net:
        networks = get_all_networks()
        display_networks(networks)
        sys.exit(0)

    menu()

def get_all_networks():
    network_url = f"{BASE_URL}/vmnet"
    headers = {'Accept': 'application/vnd.vmware.vmw.rest-v1+json'}
    try:
        response = requests.get(network_url, headers=headers, auth=HTTPBasicAuth(USERNAME, PASSWORD))
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

if __name__ == "__main__":
    main()