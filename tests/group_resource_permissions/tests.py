# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 Red Hat
# Licensed under The MIT License (MIT)
# http://opensource.org/licenses/MIT
#
from pdc_client.test_helpers import CLITestCase
from pdc_client.runner import Runner


class GroupResourcePermissionTestCase(CLITestCase):
    def setUp(self):
        self.runner = Runner()
        self.runner.setup()

    def _setup_list(self, api):
        api.add_endpoint('auth/group-resource-permissions', 'GET', [
            {
                "id": x,
                "group": "group" + str(x),
                "resource": "arches",
                "permission": "create"
            }

            for x in range(1, 30)
        ])

    def test_list(self, api):
        self._setup_list(api)
        with self.expect_output('list.txt'):
            self.runner.run(['group-resource-permissions', 'list', '--resource', 'arches'])
        self.assertEqual(api.calls['auth/group-resource-permissions'],
                         [('GET', {'page': 1, 'resource': 'arches'}),
                          ('GET', {'page': 2, 'resource': 'arches'})])

    def test_list_json(self, api):
        self._setup_list(api)
        with self.expect_output('list.json', parse_json=True):
            self.runner.run(['--json', 'group-resource-permissions', 'list', '--resource', 'arches'])
        self.assertEqual(api.calls['auth/group-resource-permissions'],
                         [('GET', {'page': 1, 'resource': 'arches'}),
                          ('GET', {'page': 2, 'resource': 'arches'})])

    def _setup_detail(self, api):
        obj = {
            "id": 1,
            "group": "engops",
            "resource": "arches",
            "permission": "create"
        }
        api.add_endpoint('auth/group-resource-permissions/1', 'GET', obj)
        api.add_endpoint('auth/group-resource-permissions/1', 'PATCH', obj)
        api.add_endpoint('auth/group-resource-permissions', 'POST', obj)
        api.add_endpoint('auth/group-resource-permissions/1', 'DELETE', {})

    def test_info(self, api):
        self._setup_detail(api)
        with self.expect_output('detail.txt'):
            self.runner.run(['group-resource-permissions', 'info', '1'])
        self.assertEqual(api.calls['auth/group-resource-permissions/1'], [('GET', {})])

    def test_info_json(self, api):
        self._setup_detail(api)
        with self.expect_output('detail.json', parse_json=True):
            self.runner.run(['--json', 'group-resource-permissions', 'info', '1'])
        self.assertEqual(api.calls['auth/group-resource-permissions/1'], [('GET', {})])

    def test_create(self, api):
        self._setup_detail(api)
        with self.expect_output('detail.txt'):
            self.runner.run(['group-resource-permissions', 'create',
                             '--group', 'engops',
                             '--resource', 'arches',
                             '--permission', 'create'
                             ])
        expected_data = {
            "group": "engops",
            "resource": "arches",
            "permission": "create"
        }
        self.assertEqual(api.calls['auth/group-resource-permissions'],
                         [('POST', expected_data)])
        self.assertEqual(api.calls['auth/group-resource-permissions/1'],
                         [('GET', {})])

    def test_update(self, api):
        self._setup_detail(api)
        with self.expect_output('detail.txt'):
            self.runner.run(['group-resource-permissions', 'update', '1',
                             '--group', 'engops',
                             '--resource', 'arches',
                             '--permission', 'create'])
        self.assertEqual(api.calls['auth/group-resource-permissions/1'],
                         [('PATCH', {'resource': 'arches',
                                     'permission': 'create',
                                     'group': 'engops'}),
                          ('GET', {})])

    def test_delete(self, api):
        self._setup_detail(api)
        self.runner.run(['group-resource-permissions', 'delete', '1'])
        self.assertEqual(api.calls['auth/group-resource-permissions/1'], [('DELETE', {})])
