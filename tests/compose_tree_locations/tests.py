# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 Red Hat
# Licensed under The MIT License (MIT)
# http://opensource.org/licenses/MIT
#
from pdc_client.test_helpers import CLITestCase
from pdc_client.runner import Runner
from copy import deepcopy


class ComposeTreeLocationsTestCase(CLITestCase):
    def setUp(self):
        self.runner = Runner()
        self.runner.setup()
        self.compose_tree_location_detail = {"arch": "x86_64",
                                             "compose": "Awesome-product-7.0-0",
                                             "variant": "Server",
                                             "location": "NAY",
                                             "scheme": "http",
                                             "synced_content": "debug",
                                             "url": "http://example.com"}

    def _setup_list(self, api):
        api.add_endpoint('compose-tree-locations', 'GET', [
            {"arch": "x86_64",
             "compose": "Awesome-product-7.0-{0}".format(x),
             "variant": "Server",
             "location": "NAY",
             "scheme": "http",
             "synced_content": "debug",
             "url": "http://example.com"}
            for x in range(30)
        ])

    def _setup_detail(self, api):
        obj = {"arch": "x86_64",
               "compose": "Awesome-product-7.0-0",
               "variant": "Server",
               "location": "NAY",
               "scheme": "http",
               "synced_content": "debug",
               "url": "http://example.com"}
        api.add_endpoint('compose-tree-locations/Awesome-product-7.0-0/Server/x86_64/NAY/https',
                         'GET', obj)
        # PATCH test result to passed
        obj_update = deepcopy(obj)
        obj_update["scheme"] = "https"
        obj_update["url"] = "https://example1.com"
        obj_update["synced_content"] = "source"
        api.add_endpoint('compose-tree-locations/Awesome-product-7.0-0/Server/x86_64/NAY/https',
                         'PATCH', obj_update)

    def test_list(self, api):
        self._setup_list(api)
        with self.expect_output('list_multi_page.txt'):
            self.runner.run(['compose-tree-locations', 'list'])
        self.assertEqual(api.calls['compose-tree-locations'],
                         [('GET', {'page': 1}),
                          ('GET', {'page': 2})])

    def test_info(self, api):
        self._setup_detail(api)
        with self.expect_output('detail.txt'):
            self.runner.run(['compose-tree-locations', 'info', 'Awesome-product-7.0-0', 'Server',
                             'x86_64', 'NAY', 'https'])
        self.assertEqual(
            api.calls['compose-tree-locations/Awesome-product-7.0-0/Server/x86_64/NAY/https'],
            [('GET', {})])

    def test_info_json(self, api):
        self._setup_detail(api)
        with self.expect_output('detail.json', parse_json=True):
            self.runner.run(['--json', 'compose-tree-locations', 'info', 'Awesome-product-7.0-0', 'Server',
                             'x86_64', 'NAY', 'https'])
        self.assertEqual(
            api.calls['compose-tree-locations/Awesome-product-7.0-0/Server/x86_64/NAY/https'],
            [('GET', {})])

    def test_update(self, api):
        self._setup_detail(api)
        with self.expect_output('detail_for_patch.txt'):
            self.runner.run(['compose-tree-locations', 'update', 'Awesome-product-7.0-0', 'Server', 'x86_64', 'NAY',
                             'https', '--scheme', 'http', '--synced-content', 'source',
                             '--url', 'https://example1.com'])
        self.assertEqual(api.calls, {'compose-tree-locations/Awesome-product-7.0-0/Server/x86_64/NAY/https':
                                     [('PATCH', {'scheme': 'http',
                                                 'synced_content': ['source'],
                                                 'url': 'https://example1.com'})]})

    def test_create(self, api):
        obj = {'arch': 'x86_64',
               'compose': 'Awesome-product-7.0-0',
               'variant': 'Server',
               'location': 'NAY',
               'scheme': 'http',
               'synced_content': 'debug',
               'url': 'http://example.com'}

        api.add_endpoint('compose-tree-locations', 'POST', obj)
        with self.expect_output('detail.txt'):
            self.runner.run(['compose-tree-locations', 'create', '--compose', 'Awesome-product-7.0-0', '--variant',
                             'Server', '--arch', 'x86_64', '--location', 'NAY', '--scheme', 'http', '--synced-content',
                             'debug', '--url', 'http://example.com'])
        self.assertEqual(api.calls, {'compose-tree-locations': [('POST', {'compose': 'Awesome-product-7.0-0',
                                                                          'variant': 'Server', 'arch': 'x86_64',
                                                                          'location': 'NAY', 'scheme': 'http',
                                                                          'synced_content': ['debug'],
                                                                          'url': 'http://example.com'})]})

    def test_create_multi_synced_contents(self, api):
        obj = {'arch': 'x86_64',
               'compose': 'Awesome-product-7.0-0',
               'variant': 'Server',
               'location': 'NAY',
               'scheme': 'http',
               'synced_content': 'debug source binary',
               'url': 'http://example.com'}

        api.add_endpoint('compose-tree-locations', 'POST', obj)
        with self.expect_output('detail_multi_synced_contents.txt'):
            self.runner.run(['compose-tree-locations', 'create', '--compose', 'Awesome-product-7.0-0', '--variant',
                             'Server', '--arch', 'x86_64', '--location', 'NAY', '--scheme', 'http', '--synced-content',
                             'debug', 'source', 'binary', '--url', 'http://example.com'])
        self.assertEqual(api.calls, {'compose-tree-locations': [('POST', {'compose': 'Awesome-product-7.0-0',
                                                                          'variant': 'Server', 'arch': 'x86_64',
                                                                          'location': 'NAY', 'scheme': 'http',
                                                                          'synced_content': ['debug', 'source', 'binary'],
                                                                          'url': 'http://example.com'})]})

    def test_delete(self, api):
        api.add_endpoint('compose-tree-locations/Awesome-product-7.0-0/Server/x86_64/NAY/https',
                         'DELETE', None)
        with self.expect_output('empty.txt'):
            self.runner.run(['compose-tree-locations', 'delete', 'Awesome-product-7.0-0', 'Server', 'x86_64', 'NAY',
                             'https'])
        self.assertEqual(api.calls, {'compose-tree-locations/Awesome-product-7.0-0/Server/x86_64/NAY/https':
                                     [('DELETE', {})]})
