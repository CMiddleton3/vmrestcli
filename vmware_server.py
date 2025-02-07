"""
Manages the lifecycle of the VMware Workstation REST server.

Provides methods to start, stop, check if running and configure the server.

"""
import subprocess
import logging
import sys
import os
import platform
import time
import psutil
import requests

logging.basicConfig(level=logging.INFO)


class VMWareServer:
    """
    Manages the lifecycle of the VMware Workstation REST server.

    Provides methods to start, stop, check if running and configure the server.

    Attributes:
    state (str): Current state of the server (e.g., STARTING, RUNNING, STOPPED)
    VMWARE_REST_EXE (str): Path to the VMware Workstation REST executable
    is_server_running (method): Checks if the server is currently running

    Methods:
    start_server(): Starts the VMware Workstation REST server.
    stop_server(): Stops the VMware Workstation REST server.
    is_server_running(): Checks if the VMware Workstation REST server is running.
    configure_vmware_server(): Configures the VMware Workstation REST server (not implemented in this example).
    """
    RUNNING = "running"
    STOPPED = "stopped"

    def __init__(self, base_url, VMWARE_REST_EXE):
        self.VMWARE_REST_EXE = VMWARE_REST_EXE
        self.VMWARE_REST_PROCESS = "vmrest.exe"
        self.BASE_URL = base_url
        self.state = self.STOPPED if not self.is_server_running() else self.RUNNING

    def configure_vmware_server(self):
        """
        Configure the VMware Workstation REST server.

        This method checks if the server executable exists in the specified location. If it does, the server is started with the -C option.
        If the executable does not exist or an error occurs during startup, an error message is printed and False is returned.

        Returns:
            bool: True if the server was successfully configured, False otherwise.
        """
        if not os.path.exists(self.VMWARE_REST_EXE):
            print(f"Error: Server executable not found: {self.VMWARE_REST_EXE}.")
            return False
        try:
            subprocess.run([self.VMWARE_REST_EXE,"-C"],text=True,check=False)
        except FileNotFoundError:
            print(f"Error: Server executable not found: {self.VMWARE_REST_EXE}.")
            return False
        except subprocess.SubprocessError as e:
            print(f"Error starting server: {e}")
            return False


    def is_server_running(self, check_rest=False) -> bool:
        """
        Check if the VMware Workstation REST server is running.

        This method checks the current state of the server and returns True if it's running, False otherwise.

        Returns:
            bool: True if the server is running, False otherwise.
        """      
        # Check if the process is running
        logging.info("Checking VMware Workstation REST server Power State.")
        for proc in psutil.process_iter(["name"]):
            if proc.info["name"] == self.VMWARE_REST_PROCESS:
                self.state = self.RUNNING
                return True
        # Optionally check if the REST API is reachable
        if check_rest:
            try:
                response = requests.get(self.BASE_URL, timeout=5)
                if response.status_code == 200:
                    self.state = self.RUNNING
                    return True

            except requests.exceptions.ConnectionError as e:
                print(f"Error checking server using REST: {e}")

        self.state = self.STOPPED
        return False

    def start_server(self) -> bool:
        """
        Starts the VMware Workstation REST server.

        This method checks if the server executable exists in the specified location. If it does, the server is started with the -C option.
        If the executable does not exist or an error occurs during startup, an error message is printed and False is returned.

        Returns:
        bool: True if the server was successfully started, False otherwise.
        """
        if self.state == self.RUNNING:
            print("VMware Workstation REST server is already running.")
            return True

        if not os.path.exists(self.VMWARE_REST_EXE):
            print(f"Error: Server executable not found: {self.VMWARE_REST_EXE}.")
            return False

        try:
            logging.info("Starting VMware Workstation REST server.")
            
            if platform.system() == "Windows":
                # Start the server in a new process group to allow for termination
                self.process = subprocess.Popen(
                    [self.VMWARE_REST_EXE],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                )
            else:
                subprocess.Popen(
                    [self.VMWARE_REST_EXE],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    preexec_fn=os.setpgrp,
                )
            time.sleep(3)  # Allow the server time to start

            if self.is_server_running(check_rest=True):
                print("VMware Workstation REST server started successfully.")
                self.state = self.RUNNING
                return True
            else:
                print("Failed to start VMware Workstation REST server.")
                return False

        except FileNotFoundError:
            print(f"Error: Server executable not found: {self.VMWARE_REST_EXE}.")
            sys.exit(1)
        except subprocess.SubprocessError as e:
            print(f"Error starting server: {e}")
            return False

    def stop_server(self) -> bool:
        """
        Stop the VMware Workstation REST server.

        This method checks if the server is already stopped, and returns True if it is.
        If the server is not stopped, an error message is printed indicating that the server is not running.

        Returns:
            bool: True if the server was successfully stopped, False otherwise.
        """
        if self.state == self.STOPPED:
            print("VMware Workstation REST server is not running.")
            return True

        logging.info("Stopping VMware Workstation REST server.")
        for proc in psutil.process_iter(["pid", "name"]):
            if proc.info["name"] == self.VMWARE_REST_PROCESS:
                print(
                    f"Terminating process {proc.info['name']} (PID {proc.info['pid']})..."
                )
                proc.terminate()
                proc.wait()  # Wait for process to terminate
                time.sleep(3)  # Allow time for the termination

                if not self.is_server_running():
                    print("VMware Workstation REST server stopped successfully.")
                    self.state = self.STOPPED
                    return True
        print(f"No running process found for {self.VMWARE_REST_PROCESS}.")
        return False
    