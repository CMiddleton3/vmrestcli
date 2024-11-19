import unittest
from unittest.mock import patch, MagicMock
from vmware_server import VMWareServer

class TestVMWareServer(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://127.0.0.1:8697"
        self.vmrest_exe = "/mnt/c/Program Files (x86)/VMware/VMware Workstation/vmrest.exe"
        self.vmrest_process = "vmrest.exe"
        self.vm_server = VMWareServer(self.base_url, self.vmrest_exe)
        self.vm_server.VMWARE_REST_PROCESS = "vmrest.exe"

    @patch("psutil.process_iter")
    def test_is_server_running_when_running(self, mock_process_iter):
        mock_process_iter.return_value = [MagicMock(info={"name": self.vmrest_process})]
        self.assertTrue(self.vm_server.is_server_running())

    @patch("psutil.process_iter")
    def test_is_server_running_when_not_running(self, mock_process_iter):
        mock_process_iter.return_value = []
        self.assertFalse(self.vm_server.is_server_running())

    @patch("requests.get")
    def test_is_server_running_check_rest_success(self, mock_get):
        mock_get.return_value.status_code = 200
        self.assertTrue(self.vm_server.is_server_running(check_rest=True))


    @patch("subprocess.Popen")
    @patch("vmware_server.VMWareServer.is_server_running", return_value=True)
    def test_start_server_success(self, mock_is_running, mock_popen):
        self.vm_server.state = VMWareServer.STOPPED
        self.assertTrue(self.vm_server.start_server())
        mock_popen.assert_called_once()

    @patch("subprocess.Popen", side_effect=FileNotFoundError)
    def test_start_server_executable_not_found(self, mock_popen):
        self.vm_server.state = VMWareServer.STOPPED
        with self.assertRaises(SystemExit):
            self.vm_server.start_server()

    @patch("psutil.process_iter")
    def test_stop_server_success(self, mock_process_iter):
        mock_proc = MagicMock(info={"name": self.vmrest_process})
        mock_proc.terminate = MagicMock()
        mock_proc.wait = MagicMock()
        mock_process_iter.return_value = [mock_proc]

        self.vm_server.state = VMWareServer.RUNNING
        self.assertFalse(self.vm_server.stop_server())

    @patch("psutil.process_iter")
    def test_stop_server_not_running(self, mock_process_iter):
        mock_process_iter.return_value = []
        self.vm_server.state = VMWareServer.STOPPED
        self.assertTrue(self.vm_server.stop_server())

if __name__ == "__main__":
    unittest.main()
