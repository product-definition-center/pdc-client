# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Red Hat
# Licensed under The MIT License (MIT)
# http://opensource.org/licenses/MIT
#
from pdc_client.test_helpers import CLITestCase
from pdc_client.runner import Runner


class BaseProductTestCase(CLITestCase):
    def setUp(self):
        self.runner = Runner()
        self.runner.setup()
        self.base_product_detail = {
            'base_product_id': 'test-base-product-1',
            'short': 'test-base-product',
            'name': 'Test Base Product',
            'version': "1",
            'release_type': 'ga',
        }

    def _setup_base_product_detail(self, api):
        api.add_endpoint('base-products/test-base-product-1', 'GET', self.base_product_detail)

    def test_create(self, api):
        api.add_endpoint('base-products', 'POST', self.base_product_detail)
        self._setup_base_product_detail(api)

        # compare stdout with data/info.txt
        with self.expect_output('info.txt'):
            # run the command
            self.runner.run([
                'base-product',
                'create',
                '--short', 'test-base-product',
                '--name', 'Test Base Product',
                '--version', '1',
                '--type', 'ga',
            ])

        # test api calls made by the command
        self.assertEqual(api.calls, {
            'base-products': [
                ('POST', {
                    'short': 'test-base-product',
                    'name': 'Test Base Product',
                    'version': '1',
                    'release_type': 'ga',
                }),
            ],
            'base-products/test-base-product-1': [
                ('GET', {
                }),
            ],
        })

    def test_info(self, api):
        api.add_endpoint('base-products/test-base-product-1', 'GET', self.base_product_detail)

        # compare stdout with data/info.txt
        with self.expect_output('info.txt'):
           self.runner.run([
                'base-product',
                'info',
                'test-base-product-1',
            ])

        # test api calls made by the command
        self.assertEqual(api.calls, {
            'base-products/test-base-product-1': [
                ('GET', {
                }),
            ],
        })

    def test_list(self, api):
        api.add_endpoint('base-products', 'GET', [self.base_product_detail])

        # compare stdout with data/list-all.txt
        with self.expect_output('list-all.txt'):
            # run the command
            self.runner.run([
                'base-product',
                'list',
            ])

        # test api calls made by the command
        self.assertEqual(api.calls, {
            'base-products': [
                ('GET', {
                    'page': 1
                }),
            ],
        })


    def test_update(self, api):
        api.add_endpoint('base-products/test-base-product-0.9', 'PATCH', self.base_product_detail)
        self._setup_base_product_detail(api)

        with self.expect_output('info.txt'):
            # run the command
            self.runner.run([
                'base-product',
                'update',
                'test-base-product-0.9',
                '--version', '1',
            ])

        # test api calls made by the command
        self.assertEqual(api.calls, {
            'base-products/test-base-product-0.9': [
                ('PATCH', {
                    'version': '1',
                }),
            ],
            'base-products/test-base-product-1': [
                ('GET', {
                }),
            ],
        })
