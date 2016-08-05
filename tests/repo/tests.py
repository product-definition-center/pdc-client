# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 Red Hat
# Licensed under The MIT License (MIT)
# http://opensource.org/licenses/MIT
#
from pdc_client.test_helpers import CLITestCase
from pdc_client.runner import Runner


class RepoTestCase(CLITestCase):
    def setUp(self):
        self.runner = Runner()
        self.runner.setup()
        self.maxDiff = None

    def test_list_without_filters(self, api):
        with self.expect_failure():
            self.runner.run(['content-delivery-repo', 'list'])

    def _setup_list(self, api):
        api.add_endpoint('content-delivery-repos', 'GET', [
            {
                "arch": "x86_64",
                "content_category": "binary",
                "content_format": "iso",
                "id": x,
                "name": "rhel-x86_64-workstation-7-shadow",
                "product_id": x,
                "release_id": "rhel-7.1-updates",
                "repo_family": "dist",
                "service": "rhn",
                "shadow": True,
                "variant_uid": "Workstation"
            }

            for x in range(1, 30)
        ])

    def test_list(self, api):
        self._setup_list(api)
        with self.expect_output('list.txt'):
            self.runner.run(['content-delivery-repo', 'list', '--content-format', 'iso'])
        self.assertEqual(api.calls['content-delivery-repos'],
                         [('GET', {'page': 1, 'content_format': 'iso'}),
                          ('GET', {'page': 2, 'content_format': 'iso'})])

    def test_list_json(self, api):
        self._setup_list(api)
        with self.expect_output('list.json', parse_json=True):
            self.runner.run(['--json', 'content-delivery-repo', 'list', '--content-format', 'iso'])
        self.assertEqual(api.calls['content-delivery-repos'],
                         [('GET', {'page': 1, 'content_format': 'iso'}),
                          ('GET', {'page': 2, 'content_format': 'iso'})])

    def _setup_detail(self, api):
        obj = {
            "id": 1,
            "arch": "x86_64",
            "content_category": "binary",
            "content_format": "iso",
            "name": "rhel-x86_64-workstation-7-shadow",
            "product_id": 1,
            "release_id": "rhel-7.1-updates",
            "repo_family": "dist",
            "service": "rhn",
            "shadow": True,
            "variant_uid": "Workstation"
        }

        api.add_endpoint('content-delivery-repos/1', 'GET', obj)
        api.add_endpoint('content-delivery-repos/1', 'PATCH', obj)
        api.add_endpoint('content-delivery-repos', 'POST', obj)
        api.add_endpoint('content-delivery-repos/1', 'DELETE', {})

    def test_info(self, api):
        self._setup_detail(api)
        with self.expect_output('info.txt'):
            self.runner.run(['content-delivery-repo', 'info', '1'])
        self.assertEqual(api.calls['content-delivery-repos/1'], [('GET', {})])

    def test_info_json(self, api):
        self._setup_detail(api)
        with self.expect_output('info.json', parse_json=True):
            self.runner.run(['--json', 'content-delivery-repo', 'info', '1'])
        self.assertEqual(api.calls['content-delivery-repos/1'], [('GET', {})])

    def test_create(self, api):
        self._setup_detail(api)
        with self.expect_output('info.txt'):
            self.runner.run(['content-delivery-repo', 'create',
                             '--name', 'rhel-x86_64-workstation-7-shadow',
                             '--content-format', 'iso',
                             '--content-category', 'binary',
                             '--release-id', 'rhel-7.1-updates',
                             '--service', 'rhn',
                             '--repo-family', 'dist',
                             '--variant-uid', 'Workstation',
                             '--arch', 'x86_64',
                             '--product-id', '1',
                             '--shadow', 'true'])
        expected_data = {
            "arch": "x86_64",
            "content_category": "binary",
            "content_format": "iso",
            "name": "rhel-x86_64-workstation-7-shadow",
            "product_id": 1,
            "release_id": "rhel-7.1-updates",
            "repo_family": "dist",
            "service": "rhn",
            "shadow": 'true',
            "variant_uid": "Workstation"
        }
        self.assertEqual(api.calls['content-delivery-repos'],
                         [('POST', expected_data)])
        self.assertEqual(api.calls['content-delivery-repos/1'],
                         [('GET', {})])

    def test_update(self, api):
        self._setup_detail(api)
        with self.expect_output('info.txt'):
            self.runner.run(['content-delivery-repo', 'update', '1',
                             '--name', 'rhel-x86_64-workstation-7-shadow',
                             '--release-id', 'rhel-7.1-updates'])
        self.assertEqual(api.calls['content-delivery-repos/1'],
                         [('PATCH', {'name': 'rhel-x86_64-workstation-7-shadow',
                                     'release_id': 'rhel-7.1-updates'}),
                          ('GET', {})])

    def test_delete(self, api):
        self._setup_detail(api)
        self.runner.run(['content-delivery-repo', 'delete', '1'])
        self.assertEqual(api.calls['content-delivery-repos/1'], [('DELETE', {})])
