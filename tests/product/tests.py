# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Red Hat
# Licensed under The MIT License (MIT)
# http://opensource.org/licenses/MIT
#
from pdc_client.test_helpers import CLITestCase
from pdc_client.runner import Runner


class ProductTestCase(CLITestCase):
    def setUp(self):
        self.runner = Runner()
        self.runner.setup()
        self.product_detail = {
            'short': 'test-product',
            'name': 'Test Product',
            'active': False,
        }

    def _setup_product_detail(self, api):
        api.add_endpoint('products/test-product', 'GET', self.product_detail)

    def test_create(self, api):
        api.add_endpoint('products', 'POST', self.product_detail)
        self._setup_product_detail(api)

        # compare stdout with data/info.txt
        with self.expect_output('info.txt'):
            # run the command
            self.runner.run([
                'product',
                'create',
                '--short', 'test-product',
                '--name', 'Test Product',
            ])

        # test api calls made by the command
        self.assertEqual(api.calls, {
            'products': [
                ('POST', {
                    'short': 'test-product',
                    'name': 'Test Product',
                }),
            ],
            'products/test-product': [
                ('GET', {
                }),
            ],
        })

    def test_info(self, api):
        api.add_endpoint('products/test-product', 'GET', self.product_detail)

        # compare stdout with data/info.txt
        with self.expect_output('info.txt'):
            self.runner.run([
                'product',
                'info',
                'test-product',
            ])

        # test api calls made by the command
        self.assertEqual(api.calls, {
            'products/test-product': [
                ('GET', {
                }),
            ],
        })

    def test_list_all(self, api):
        api.add_endpoint('products', 'GET', [self.product_detail])

        # compare stdout with data/list-all.txt
        with self.expect_output('list-all.txt'):
            # run the command
            self.runner.run([
                'product',
                'list',
                '--all',
            ])

        # test api calls made by the command
        self.assertEqual(api.calls, {
            'products': [
                ('GET', {
                    'page': 1
                }),
            ],
        })

    def test_list_active(self, api):
        api.add_endpoint('products', 'GET', [])

        # compare stdout with data/list-empty.txt
        with self.expect_output('list-empty.txt'):
            # run the command
            self.runner.run([
                'product',
                'list',
            ])

        # test api calls made by the command
        self.assertEqual(api.calls, {
            'products': [
                ('GET', {
                    'active': True,
                    'page': 1
                }),
            ],
        })

    def test_list_inactive(self, api):
        api.add_endpoint('products', 'GET', [self.product_detail])

        # compare stdout with data/list-all.txt
        with self.expect_output('list-all.txt'):
            # run the command
            self.runner.run([
                'product',
                'list',
                '--inactive',
            ])

        # test api calls made by the command
        self.assertEqual(api.calls, {
            'products': [
                ('GET', {
                    'active': False,
                    'page': 1
                }),
            ],
        })

    def test_update(self, api):
        api.add_endpoint('products/old-test-product', 'PATCH', self.product_detail)
        self._setup_product_detail(api)

        with self.expect_output('info.txt'):
            # run the command
            self.runner.run([
                'product',
                'update',
                'old-test-product',
                '--short', 'test-product',
            ])

        # test api calls made by the command
        self.assertEqual(api.calls, {
            'products/old-test-product': [
                ('PATCH', {
                    'short': 'test-product',
                }),
            ],
            'products/test-product': [
                ('GET', {
                }),
            ],
        })
