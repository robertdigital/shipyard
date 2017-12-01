# Copyright 2017 AT&T Intellectual Property.  All other rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
from unittest.mock import MagicMock

from prettytable.prettytable import DEFAULT

import shipyard_client.cli.format_utils as format_utils


def test_cli_format_error_handler_bogus_json():
    """Tests the generic handler for shipyard error response if passed
    unrecognized json
    """
    resp = MagicMock()
    resp.json = MagicMock(return_value=json.loads('{"key": "value"}'))
    output = format_utils.cli_format_error_handler(resp)
    assert 'Error: Not specified' in output
    assert 'Reason: Not specified' in output


def test_cli_format_error_handler_broken_json():
    """Tests the generic handler for shipyard error response if passed
    unrecognized json
    """
    resp = MagicMock()
    resp.json.side_effect = ValueError("")
    resp.text = "Not JSON"
    output = format_utils.cli_format_error_handler(resp)
    assert 'Error: Unable to decode response. Value: Not JSON' in output


def test_cli_format_error_handler_no_messages():
    """Tests the generic handler for shipyard error response if passed
    json in the right format, but with no messages
    """
    resp_val = """
{
  "apiVersion": "v1.0",
  "status": "Failure",
  "metadata": {},
  "message": "Unauthenticated",
  "code": "401 Unauthorized",
  "details": {},
  "kind": "status",
  "reason": "Credentials are not established"
}
"""
    resp = MagicMock()
    resp.json = MagicMock(return_value=json.loads(resp_val))
    output = format_utils.cli_format_error_handler(resp)
    print(output)
    assert "Error: Unauthenticated" in output
    assert "Reason: Credentials are not established" in output


def test_cli_format_error_handler_messages():
    """Tests the generic handler for shipyard error response if passed
    a response with messages in the detail
    """
    resp_val = """
{
  "apiVersion": "v1.0",
  "status": "Failure",
  "metadata": {},
  "message": "Unauthenticated",
  "code": "401 Unauthorized",
  "details": {
      "messageList": [
          { "message":"Hello1", "error": false },
          { "message":"Hello2", "error": false },
          { "message":"Hello3", "error": true }
      ]
  },
  "kind": "status",
  "reason": "Credentials are not established"
}
"""
    resp = MagicMock()
    resp.json = MagicMock(return_value=json.loads(resp_val))
    output = format_utils.cli_format_error_handler(resp)
    assert "Error: Unauthenticated" in output
    assert "Reason: Credentials are not established" in output
    assert "- Error: Hello3" in output
    assert "- Info: Hello2" in output


def test_cli_format_error_handler_messages_broken():
    """Tests the generic handler for shipyard error response if passed
    a response with messages in the detail, but missing error or message
    elements
    """
    resp_val = """
{
  "apiVersion": "v1.0",
  "status": "Failure",
  "metadata": {},
  "message": "Unauthenticated",
  "code": "401 Unauthorized",
  "details": {
      "messageList": [
          { "message":"Hello1", "error": false },
          { "error": true },
          { "message":"Hello3" }
      ]
  },
  "kind": "status",
  "reason": "Credentials are not established"
}
"""
    resp = MagicMock()
    resp.json = MagicMock(return_value=json.loads(resp_val))
    output = format_utils.cli_format_error_handler(resp)
    assert "Error: Unauthenticated" in output
    assert "Reason: Credentials are not established" in output
    assert "- Error: None" in output
    assert "- Info: Hello3" in output


def test_table_factory():
    t = format_utils.table_factory()
    assert t.get_string() == ''


def test_table_factory_fields():
    t = format_utils.table_factory(field_names=['a', 'b', 'c'])
    t.add_row(['1', '2', '3'])
    assert 'a' in t.get_string()
    assert 'b' in t.get_string()
    assert 'c' in t.get_string()


def test_table_factory_fields_data():
    t = format_utils.table_factory(style=DEFAULT,
                                   field_names=['a', 'b', 'c'],
                                   rows=[['1', '2', '3'], ['4', '5', '6']])
    assert 'a' in t.get_string()
    assert 'b' in t.get_string()
    assert 'c' in t.get_string()
    assert '1' in t.get_string()
    assert '6' in t.get_string()