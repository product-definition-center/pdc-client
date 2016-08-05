# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 Red Hat
# Licensed under The MIT License (MIT)
# http://opensource.org/licenses/MIT
#
from pdc_client.test_helpers import CLITestCase
from pdc_client.runner import Runner


class PermissionTestCase(CLITestCase):
    def setUp(self):
        self.runner = Runner()
        self.runner.setup()

    def _setup_list(self, api):
        api.add_endpoint('auth/current-user', 'GET',
                         {'permissions': ['perms-{0}'.format(x) for x in range(10)]})

    def test_list(self, api):
        self._setup_list(api)
        with self.expect_output('list.txt'):
            self.runner.run(['permission', 'list'])
        self.assertEqual(api.calls['auth/current-user'],
                         [('GET', {})])

    def test_list_json(self, api):
        self._setup_list(api)
        with self.expect_output('list.json', parse_json=True):
            self.runner.run(['--json', 'permission', 'list'])
        self.assertEqual(api.calls['auth/current-user'], [('GET', {})])
