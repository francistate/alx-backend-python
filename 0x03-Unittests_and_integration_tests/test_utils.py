#!/usr/bin/env python3
"""Test cases for utils module"""
import unittest
from parameterized import parameterized
from utils import access_nested_map, get_json, memoize
from unittest.mock import patch, Mock
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestAccessNestedMap(unittest.TestCase):
    """Test class for access_nested_map function"""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Test that access_nested_map returns expected result"""
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",)),
        ({"a": 1}, ("a", "b")),
    ])
    def test_access_nested_map_exception(self, nested_map, path):
        """Test that key error is raised for invalid path"""
        # with self.assertRaises(KeyError):
        #     access_nested_map(nested_map, path)
        self.assertRaises(KeyError, access_nested_map, nested_map, path)


class TestGetJson(unittest.TestCase):
    """Test class for get_json function"""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch('utils.requests.get')
    def test_get_json(self, test_url, test_payload, mock_get):
        """Test that get_json returns expected results"""

        # configure the mock to return a response with the test payload
        mock_response = Mock()
        mock_response.json.return_value = test_payload
        mock_get.return_value = mock_response

        # call the function with the test URL
        result = get_json(test_url)

        # assert that the mock was called once with the correct URL
        mock_get.assert_called_once_with(test_url)
        # assert that the result matches the expected payload
        self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """Test class for memoize decorator caches method results"""

    def test_memoize(self):
        """Test that memoize caches method results"""

        class TestClass:
            """Test class to demonstrate memoization"""
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        test_object = TestClass()

        # patch the method to ensure it is called only once
        with patch.object(test_object, 'a_method',
                          return_value=42) as mock_method:
            # call the property multiple times
            self.assertEqual(test_object.a_property, 42)
            self.assertEqual(test_object.a_property, 42)
            mock_method.assert_called_once()


if __name__ == "__main__":
    unittest.main()
