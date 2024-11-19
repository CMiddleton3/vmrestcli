import unittest
import requests
import json
from unittest.mock import patch, MagicMock, Mock
from vmrest import get_all_vms, power_on_off, display_vms
from vmware_server import *

class TestVMRest(unittest.TestCase):
    @patch("requests.get")
    def test_get_all_vms_success(self, mock_get):
        mock_response = Mock()
        mock_response.return_value.json.return_value = [{"id": "vm1", "path": "/path/to/vm1"}]
        mock_response.side_effect = requests.exceptions.ConnectionError("Connection failed")
        mock_response.return_value.status_code = 200

        mock_get = mock_response

        vms = get_all_vms()

    @patch("requests.put")
    @patch("vmrest.get_vm_power_state", return_value="poweredOff")
    def test_power_on_off_success(self, mock_power_state, mock_put):
        mock_put.return_value.json.return_value = {"power_state": "poweredOn"}
        mock_put.return_value.status_code = 200
        self.assertIsNone(power_on_off("vm1", "on"))
        mock_put.assert_called_once()

    @patch("vmrest.get_vm_name_by_ids", return_value="TestVM")
    @patch("vmrest.get_vm_power_state", return_value="poweredOn")
    def test_display_vms(self, mock_power_state, mock_name):
        vms = [{"id": "vm1", "path": "/path/to/vm1"}]
        with patch("builtins.print") as mock_print:
            display_vms(vms)
            mock_print.assert_any_call("\n1. VM Name: TestVM")
            mock_print.assert_any_call("   Power State: poweredOn")

if __name__ == "__main__":
    unittest.main()
