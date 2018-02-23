#
# Copyright (c) 2018 Red Hat
# Licensed under The MIT License (MIT)
# http://opensource.org/licenses/MIT
#
"""
Tests for PDC client configuration.
"""

import os

try:
    # Python 2.6 compatibility
    import unittest2 as unittest
except ImportError:
    import unittest

from pdc_client.config import (
    ServerConfigManager,
    ServerConfigMissingUrlError,
    ServerConfigNotFoundError,
    ServerConfigConflictError,
)


def fixture_path(file_name):
    fixtures_path = os.path.join(os.path.dirname(__file__), 'fixtures')
    path = os.path.join(fixtures_path, file_name)
    assert(os.path.exists(path))
    return path


class ServerConfigTestCase(unittest.TestCase):
    def test_read_config_file(self):
        configs = ServerConfigManager(fixture_path('config.json'))

        expected = {
            "host": "https://www.example.com/1/",
            "ssl-verify": False,
            "develop": True,
            "token": "TEST_TOKEN",
            "plugins": ["bindings.py"]
        }
        config = configs.get('test-pdc-server-1')
        self.assertEqual(config.config, expected)

        expected = {
            "host": "https://www.example.com/2/"
        }
        config = configs.get('test-pdc-server-2')
        self.assertEqual(config.config, expected)

    def test_read_config_dir(self):
        configs = ServerConfigManager(fixture_path('config.json'), fixture_path('configs'))

        expected = {
            "host": "https://www.example.com/1/",
            "ssl-verify": False,
            "develop": True,
            "token": "TEST_TOKEN",
            "plugins": ["bindings.py"]
        }
        config = configs.get('test-pdc-server-1')
        self.assertEqual(config.config, expected)

        expected = {
            "host": "https://www.example.com/4/"
        }
        config = configs.get('test-pdc-server-4')
        self.assertEqual(config.config, expected)

    def test_url(self):
        configs = ServerConfigManager(fixture_path('config.json'))

        config = configs.get('test-pdc-server-1')
        self.assertEqual(config.url(), 'https://www.example.com/1/')

        config = configs.get('test-pdc-server-2')
        self.assertEqual(config.url(), 'https://www.example.com/2/')

    def test_default_url(self):
        configs = ServerConfigManager()
        server = 'http://test-pdc-server-1'
        config = configs.get(server)
        self.assertEqual(config.url(), server)

    def test_missing_url(self):
        configs = ServerConfigManager(fixture_path('missing-url.json'))
        with self.assertRaises(ServerConfigMissingUrlError):
            configs.get('test-pdc-server-1')

    def test_ssl_verify(self):
        configs = ServerConfigManager(fixture_path('config.json'))
        config = configs.get('test-pdc-server-1')
        self.assertEqual(config.ssl_verify(), False)

    def test_default_ssl_verify(self):
        configs = ServerConfigManager(fixture_path('config.json'))

        config = configs.get('test-pdc-server-2')
        self.assertEqual(config.ssl_verify(), True)

        config = configs.get('http://test-pdc-server-3')
        self.assertEqual(config.ssl_verify(), True)

        config = configs.get('http://test-pdc-server-4')
        self.assertEqual(config.ssl_verify(), True)

    def test_develop(self):
        configs = ServerConfigManager(fixture_path('config.json'))
        config = configs.get('test-pdc-server-1')
        self.assertEqual(config.is_development(), True)

    def test_default_develop(self):
        configs = ServerConfigManager(fixture_path('config.json'))

        config = configs.get('test-pdc-server-2')
        self.assertEqual(config.is_development(), False)

        config = configs.get('http://test-pdc-server-3')
        self.assertEqual(config.is_development(), False)

        config = configs.get('http://test-pdc-server-4')
        self.assertEqual(config.is_development(), False)

    def test_token(self):
        configs = ServerConfigManager(fixture_path('config.json'))
        config = configs.get('test-pdc-server-1')
        self.assertEqual(config.token(), 'TEST_TOKEN')

    def test_default_token(self):
        configs = ServerConfigManager(fixture_path('config.json'))

        config = configs.get('test-pdc-server-2')
        self.assertEqual(config.token(), None)

        config = configs.get('http://test-pdc-server-3')
        self.assertEqual(config.token(), None)

        config = configs.get('http://test-pdc-server-4')
        self.assertEqual(config.token(), None)

    def test_same_server_in_multiple_configs(self):
        configs = ServerConfigManager(fixture_path('configs-same-server'))
        with self.assertRaises(ServerConfigConflictError):
            configs.get('test')

    def test_precendence(self):
        config1 = fixture_path('precedence/config1.json')
        config2 = fixture_path('precedence/config2.json')
        server = 'test-pdc-server'

        configs = ServerConfigManager(config1, config2)
        config = configs.get(server)
        self.assertEqual(config.url(), 'https://www.example.com/1/')

        configs = ServerConfigManager(config2, config1)
        config = configs.get(server)
        self.assertEqual(config.url(), 'https://www.example.com/2/')

    def test_get_config_value(self):
        configs = ServerConfigManager(fixture_path('config.json'))

        config = configs.get('test-pdc-server-1')
        self.assertEqual(config.get('host'), 'https://www.example.com/1/')

        config = configs.get('test-pdc-server-2')
        self.assertEqual(config.get('host'), 'https://www.example.com/2/')

        server = 'http://test-pdc-server-3'
        config = configs.get(server)
        self.assertEqual(config.get('host'), server)

    def test_get_default_value(self):
        configs = ServerConfigManager(fixture_path('config.json'))

        config = configs.get('test-pdc-server-2')
        self.assertEqual(config.get('develop', True), True)

        config = configs.get('http://test-pdc-server-3')
        self.assertEqual(config.get('develop', True), True)

        configs = ServerConfigManager()
        config = configs.get('http://test-pdc-server')
        self.assertEqual(config.get('develop', True), True)

    def test_get_bad_server(self):
        configs = ServerConfigManager(fixture_path('config.json'), fixture_path('configs'))
        with self.assertRaises(ServerConfigNotFoundError):
            configs.get('test-pdc-server')
