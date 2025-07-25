#!/usr/bin/env python3
"""Test cases for client module"""
import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


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

    def test_public_repos_url(self):
        """Test that _public_repos_url returns expected URL"""
        # known payload with repos_url
        known_payload = {
            "repos_url": "https://api.github.com/orgs/google/repos"
        }

        # use patch as context manager to mock the org property
        with patch.object(GithubOrgClient, 'org',
                          new_callable=lambda: known_payload) as mock_org:
            client = GithubOrgClient("google")
            result = client._public_repos_url

            # verify the result matches the repos_url from mocked payload
            self.assertEqual(result, known_payload["repos_url"])

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test that public_repos returns expected list of repos"""
        # mock payload that get_json will return
        mock_repos_payload = [
            {"name": "episodes.dart", "license": {"key": "bsd-3-clause"}},
            {"name": "cpp-netlib", "license": {"key": "bsl-1.0"}},
            {"name": "dagger", "license": {"key": "apache-2.0"}}
        ]

        mock_get_json.return_value = mock_repos_payload

        # mock the _public_repos_url property
        test_repos_url = "https://api.github.com/orgs/google/repos"
        with patch.object(GithubOrgClient,
                          '_public_repos_url',
                          new_callable=lambda:
                          test_repos_url) as mock_repos_url:
            client = GithubOrgClient("google")
            result = client.public_repos()
            # expected list of repo names
            expected_repos = ["episodes.dart", "cpp-netlib", "dagger"]

            # verify the result matches expected repo names
            self.assertEqual(result, expected_repos)

            # verify get_json was called once with the repos URL
            mock_get_json.assert_called_once_with(test_repos_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test that has_license returns expected boolean result"""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    TEST_PAYLOAD
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test class for GithubOrgClient"""

    @classmethod
    def setUpClass(cls):
        """Set up class fixtures"""
        def side_effect(url):
            """Mock side effect function for requests.get"""
            mock_response = Mock()
            if url == cls.org_payload["repos_url"]:
                mock_response.json.return_value = cls.repos_payload
            else:
                mock_response.json.return_value = cls.org_payload
            return mock_response

        # start patcher
        cls.get_patcher = patch('requests.get', side_effect=side_effect)
        cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """Tear down class fixtures"""
        cls.get_patcher.stop()


if __name__ == "__main__":
    unittest.main()
