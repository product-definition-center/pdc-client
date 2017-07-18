# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Red Hat
# Licensed under The MIT License (MIT)
# http://opensource.org/licenses/MIT
#
from pdc_client.test_helpers import CLITestCase
from pdc_client.runner import Runner


class ProductVersionTestCase(CLITestCase):
    def setUp(self):
        self.runner = Runner()
        self.runner.setup()
        self.product_version_detail = {
            'product': 'test-product',
            'product_version_id': 'test-product-version-1',
            'short': 'test-product-version',
            'name': 'Test Product Version',
            'version': "1",
            'active': False,
        }

    def _setup_product_version_detail(self, api):
        api.add_endpoint('product-versions/test-product-version-1', 'GET', self.product_version_detail)

    def test_create(self, api):
        api.add_endpoint('product-versions', 'POST', self.product_version_detail)
        self._setup_product_version_detail(api)

        # compare stdout with data/info.txt
        with self.expect_output('info.txt'):
            # run the command
            self.runner.run([
                'product-version',
                'create',
                '--product', 'test-product',
                '--short', 'test-product-version',
                '--name', 'Test Product Version',
                '--version=1',
            ])

        # test api calls made by the command
        self.assertEqual(api.calls, {
            'product-versions': [
                ('POST', {
                    'product': 'test-product',
                    'short': 'test-product-version',
                    'name': 'Test Product Version',
                    'version': '1',
                }),
            ],
            'product-versions/test-product-version-1': [
                ('GET', {
                }),
            ],
        })

    def test_info(self, api):
        api.add_endpoint('product-versions/test-product-version-1', 'GET', self.product_version_detail)

        # compare stdout with data/info.txt
        with self.expect_output('info.txt'):
            self.runner.run([
                'product-version',
                'info',
                'test-product-version-1',
            ])

        # test api calls made by the command
        self.assertEqual(api.calls, {
            'product-versions/test-product-version-1': [
                ('GET', {
                }),
            ],
        })

    def test_list_all(self, api):
        api.add_endpoint('product-versions', 'GET', [self.product_version_detail])

        # compare stdout with data/list-all.txt
        with self.expect_output('list-all.txt'):
            # run the command
            self.runner.run([
                'product-version',
                'list',
                '--all',
            ])

        # test api calls made by the command
        self.assertEqual(api.calls, {
            'product-versions': [
                ('GET', {
                    'page': 1
                }),
            ],
        })

    def test_list_active(self, api):
        api.add_endpoint('product-versions', 'GET', [])

        # compare stdout with data/list-empty.txt
        with self.expect_output('list-empty.txt'):
            # run the command
            self.runner.run([
                'product-version',
                'list',
            ])

        # test api calls made by the command
        self.assertEqual(api.calls, {
            'product-versions': [
                ('GET', {
                    'active': True,
                    'page': 1
                }),
            ],
        })

    def test_list_inactive(self, api):
        api.add_endpoint('product-versions', 'GET', [self.product_version_detail])

        # compare stdout with data/list-all.txt
        with self.expect_output('list-all.txt'):
            # run the command
            self.runner.run([
                'product-version',
                'list',
                '--inactive',
            ])

        # test api calls made by the command
        self.assertEqual(api.calls, {
            'product-versions': [
                ('GET', {
                    'active': False,
                    'page': 1
                }),
            ],
        })

    def test_update(self, api):
        api.add_endpoint('product-versions/test-product-version-0.9', 'PATCH', self.product_version_detail)
        self._setup_product_version_detail(api)

        with self.expect_output('info.txt'):
            # run the command
            self.runner.run([
                'product-version',
                'update',
                'test-product-version-0.9',
                '--version', '1',
            ])

        # test api calls made by the command
        self.assertEqual(api.calls, {
            'product-versions/test-product-version-0.9': [
                ('PATCH', {
                    'version': '1',
                }),
            ],
            'product-versions/test-product-version-1': [
                ('GET', {
                }),
            ],
        })
