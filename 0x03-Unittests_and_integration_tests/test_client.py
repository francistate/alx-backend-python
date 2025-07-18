#!/usr/bin/env python3
"""Test cases for client module"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import unittest
from unittest.mock import patch
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
   """Test class for GithubOrgClient"""

   @parameterized.expand([
       ("google",),
       ("abc",),
   ])
   @patch('client.get_json')
   def test_org(self, org_name, mock_get_json):
       """Test that GithubOrgClient.org returns correct value"""
       # configure mock to return a test payload
       test_payload = {"login": org_name, "id": 12345}
       mock_get_json.return_value = test_payload
       
       # create client and call org method
       client = GithubOrgClient(org_name)
       result = client.org
       
       # verify get_json was called with correct URL
       expected_url = f"https://api.github.com/orgs/{org_name}"
       mock_get_json.assert_called_once_with(expected_url)
       
       # verify result matches mock return value
       self.assertEqual(result, test_payload)


if __name__ == "__main__":
   unittest.main()