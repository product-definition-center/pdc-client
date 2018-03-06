#
# Copyright (c) 2018 Red Hat
# Licensed under The MIT License (MIT)
# http://opensource.org/licenses/MIT
#
"""
Tests for pdc_client.test_helpers.MockAPI class.
"""

import copy
import mock
import unittest

from pdc_client.test_helpers import MockAPI


class MockAPITestCase(unittest.TestCase):
    products = [
        {
            "name": "EPEL",
            "short": "epel",
            "active": True,
            "product_versions": [
                "epel-6",
                "epel-7"
            ],
            "allowed_push_targets": []
        },
        {
            "name": "Fedora",
            "short": "fedora",
            "active": True,
            "product_versions": [
                "fedora-27",
                "fedora-rawhide"
            ],
            "allowed_push_targets": []
        }
    ]

    def setUp(self):
        # Mock the PDC client
        self.client = MockAPI()
        pdc_patcher = mock.patch('pdc_client.PDCClient', return_value=self.client)
        pdc_patcher.start()

        products = copy.deepcopy(self.products)
        epel = products[0]
        fedora = products[1]

        self.client.add_endpoint('products', 'GET', {
            'count': len(products),
            'next': None,
            'previous': None,
            'results': products
        })

        self.client.add_endpoint('products/epel', 'GET', epel)
        self.client.add_endpoint('products/epel', 'PATCH', epel)
        self.client.add_endpoint('products/fedora', 'GET', fedora)
        self.client.add_endpoint('products/fedora', 'PATCH', fedora)

    def test_get_item(self):
        response = self.client['products']._()
        self.assertEqual(response.get('count'), len(self.products))

        response = self.client['products']['epel']._()
        self.assertEqual(response, self.products[0])

        response = self.client['products']['fedora']._()
        self.assertEqual(response, self.products[1])

    def test_get_item_with_trailing_slash(self):
        response = self.client['products/']()
        self.assertEqual(response.get('count'), len(self.products))

        response = self.client['products/epel/']()
        self.assertEqual(response, self.products[0])

        response = self.client['products/fedora/']()
        self.assertEqual(response, self.products[1])

        response = self.client['products']['fedora/']()
        self.assertEqual(response, self.products[1])

    def test_get_attr(self):
        response = self.client.products._()
        self.assertEqual(response.get('count'), len(self.products))

        response = self.client.products.epel._()
        self.assertEqual(response, self.products[0])

        response = self.client.products.fedora._()
        self.assertEqual(response, self.products[1])

    def test_patch(self):
        self.client.products.epel._ += {'name': 'TEST'}
        self.assertEqual(self.client.calls, {'products/epel': [('PATCH', {'name': 'TEST'})]})
