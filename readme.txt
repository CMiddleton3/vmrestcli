VMware Workstation REST Automation Tool
=======================================

This tool provides a user-friendly command-line interface and an interactive menu for using the VMware Workstation REST API to manage virtual machines (VMs). You can also configure, start, and stop VMs, and view VM networks using this tool.

The script interacts with the VMware Workstation REST API to fetch VM information and execute actions such as powering on/off specific VMs.

Requirements:
-------------
- Python 3.x
- VMware Workstation with the REST API feature installed
- VMware Workstation REST Server (`vmrest`) enabled!

USAGE EXAMPLES:
---------------

1. **Show all VMs:**
   This command will display all VMs and then quit.
   
   ```
   python3 vmrest.py --show-vms
   ``` 

2. **Show all VM IDs:**
   This command displays VM IDs and quits.

   ```
   python3 vmrest.py --show-vm-ids
   ```

3. **Show power state of a specific VM (by VM_ID):**
   Replace `VM_ID` with the actual VM ID.

   ```
   python3 vmrest.py --show-power-state VM_ID
   ```

4. **Power on a VM (by VM_ID):**
   Replace `VM_ID` with the actual VM ID.

   ```
   python3 vmrest.py --power-on VM_ID
   ```

5. **Power off a VM (by VM_ID):**
   Replace `VM_ID` with the actual VM ID.

   ```
   python3 vmrest.py --power-off VM_ID
   ```

6. **Show all VMware networks:**
   Display a list of all available networks and their configurations.

   ```
   python3 vmrest.py --show-net
   ```

7. **Start the VMware Workstation REST server:**
   You can start the VMware `vmrest` API server via the CLI. The path to the `vmrest` executable needs to be set in the `vmworkstation.ini`.

   ```
   python3 vmrest.py --start-server
   ```

7. **Stop the VMware Workstation REST server:**
   You can stop the VMware `vmrest` API server via the CLI. The path to the `vmrest` executable needs to be set in the `vmworkstation.ini`.

   ```
   python3 vmrest.py --start-server
   ```

9. **Configure vmworkstation.ini:**
   If configuration is needed (such as setting up a new base URL or path to `vmrest`, run the following command, and it will guide you through the process of configuring the `.ini` file:

   ```
   python3 vmrest.py --configure
   ```

USING THE INTERACTIVE MENU:
---------------------------
If you run the script without any flags, the interactive menu will launch. Here you can perform tasks interactively without passing arguments.

   ```
   python3 vmrest.py
   ```

SHELL SCRIPT TO EXECUTE:
------------------------
If you want to automate running this script, use the shell script `run_vmrest.sh` located in your project directory. Run the following command:

   ```
   ./run_vmrest.sh
   ```

NOTE: 
Please ensure you configure the `.ini` file correctly prior to usage. You can either configure it manually or skip the manual configuration by running the `--configure` option to guide you.