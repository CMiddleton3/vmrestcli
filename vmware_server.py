import subprocess
import logging
import sys
import os
import time
import psutil
import requests

logging.basicConfig(level=logging.INFO)


class VMWareServer:
    RUNNING = "running"
    STOPPED = "stopped"

    def __init__(self, base_url, VMWARE_REST_EXE):
        self.VMWARE_REST_EXE = VMWARE_REST_EXE
        self.VMWARE_REST_PROCESS = "vmrest.exe"
        self.BASE_URL = base_url
        self.state = self.STOPPED if not self.is_server_running() else self.RUNNING

    def is_server_running(self, check_rest=False) -> bool:
        """Check if the VMware Workstation REST server is running."""
        try:
            # Check if the process is running
            logging.info("Checking VMware Workstation REST server Power State.")
            for proc in psutil.process_iter(["name"]):
                if proc.info["name"] == self.VMWARE_REST_PROCESS:
                    self.state = self.RUNNING
                    return True
        except Exception as e:
            print(f"Error checking server process: {e}")

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
        """Start the VMware Workstation REST server."""
        if self.state == self.RUNNING:
            print(f"VMware Workstation REST server is already running.")
            return True

        if not os.path.exists(self.VMWARE_REST_EXE):
            print(f"Error: Server executable not found: {self.VMWARE_REST_EXE}.")
            return False

        try:
            logging.info("Starting VMware Workstation REST server.")
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
        except Exception as e:
            print(f"Error starting server: {e}")
            return False

    def stop_server(self) -> bool:
        """Stop the VMware Workstation REST server."""
        if self.state == self.STOPPED:
            print(f"VMware Workstation REST server is not running.")
            return True

        try:
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
        except Exception as e:
            print(f"Error stopping server: {e}")
            return False
        self.state == self.STOPPED
        return False
