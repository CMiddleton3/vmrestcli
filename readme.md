# VMware Workstation REST Automation Tool

This Python-based CLI tool provides a way to manage VMware Workstation VMs via VMware's REST API. You can interact with VMware to manage virtual machines (VMs), view network configurations, and start/stop the VMware REST server easily.

The tool works both in **menu-driven** mode and through **command-line arguments**. It simplifies interacting with the VMware Workstation REST API and allows automation of common VM management tasks.

## Features

- View all VMs and their power states.
- View the power state of a specific VM using its VM ID.
- Power on or off VMs by providing the VM ID.
- View all network configurations from the VMware REST API.
- Start the VMware Workstation REST server (`vmrest`).
- Configure your `vmworkstation.ini` file interactively.
- Argument-based flags to run tasks automatically without interactive prompts.

## Requirements

- **Python 3.x**
- **VMware Workstation Pro** installed with the REST API feature (`vmrest`).
- **vmworkstation.ini** file for configuring API connection details (base URL, username, password, and executable path for `vmrest`).

## Install and Setup

1. Clone this repository to your local machine.

   ```bash
   git clone <your-repository-url>
   ```

2. Make sure **VMware Workstation Pro** is installed and its REST API (`vmrest`) is enabled.

3. Install required Python packages if needed:
   ```bash
   pip install requests
   ```

4. Configure your `vmworkstation.ini` file.

   Run the configuration tool for the first setup:

   ```bash
   python3 vmrest.py --configure
   ```

   *This will prompt you to set up:*
   - The base URL (default: `http://127.0.0.1:8697/api`)
   - Your VMware username
   - Your VMware password
   - The path to the `vmrest` executable (default: `/mnt/c/Program Files (x86)/VMware/VMware Workstation/vmrest.exe`)

---

## Usage

You can either run the tool as an interactive CLI menu or provide arguments at the command line to immediately trigger specific actions.

### Example Command-Line Usages

1. **Show all VMs:**
   ```bash
   python3 vmrest.py --show-vms
   ```

2. **Show all VM IDs:**
   ```bash
   python3 vmrest.py --show-vm-ids
   ```

3. **Show Power State of a Specific VM (by VM ID):**
   ```bash
   python3 vmrest.py --show-power-state <VM_ID>
   ```

4. **Power On a VM (by VM ID):**
   ```bash
   python3 vmrest.py --power-on <VM_ID>
   ```

5. **Power Off a VM (by VM ID):**
   ```bash
   python3 vmrest.py --power-off <VM_ID>
   ```

6. **Show all Networks:**
   ```bash
   python3 vmrest.py --show-net
   ```

7. **Start VMware Workstation REST API Server:**
   If you need to start the `vmrest` server manually:
   ```bash
   python3 vmrest.py --start-server
   ```

8. **Configure vmworkstation.ini:**
   ```bash
   python3 vmrest.py --configure
   ```

---

### Interactive Menu

If you run the script without an argument, it will launch an interactive menu where you can perform tasks manually.

```bash
python3 vmrest.py
```

The menu provides options such as:
- Show all VMs.
- Show all VM IDs.
- Show power state of a specific VM.
- Power on/off a VM.
- Start the VMware REST server.
- Quit

---

## Shell Script
To simplify running the script, a shell script (`run_vmrest.sh`) is provided. It ensures that the Python script is run using the correct environment.

```bash
./run_vmrest.sh --show-vms
```

This command runs the **Python** script with the `--show-vms` argument using the shell script.

---

## Configuration and Troubleshooting

1. **Rest API Connection Errors:**  
   Make sure that the REST API (`vmrest`) server is running on the given base URL and port (e.g., `http://127.0.0.1:8697/api`).

2. **Invalid `vmrest` Path:**  
   If you get an error indicating that `vmrest` cannot be found, reconfigure the `.ini` file using the `--configure` flag to set the correct executable path.

3. **Invalid Credentials:**  
   Ensure that the correct **username** and **password** are provided, and these values match those required by the VMware Workstation REST API.

---

## License

This project is licensed under the MIT License.
```

---