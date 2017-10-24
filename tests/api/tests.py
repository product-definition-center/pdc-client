# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Red Hat
# Licensed under The MIT License (MIT)
# http://opensource.org/licenses/MIT
#
"""
Tests for pdc_client.PDCClient class.
"""

import json
import os
import time
import traceback

try:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
except ImportError:
    from http.server import BaseHTTPRequestHandler, HTTPServer

from threading import Thread

try:
    # Python 2.6 compatibility
    import unittest2 as unittest
except ImportError:
    import unittest

from beanbag import BeanBagException
from pdc_client import NoResultsError, PDCClient

SERVER_ENV_VAR_NAME = 'PDC_CLIENT_TEST_SERVER'
DEFAULT_SERVER = 'localhost'

PORT_ENV_VAR_NAME = 'PDC_CLIENT_TEST_SERVER_PORT'
DEFAULT_PORT = 8378

API_PATH = '/rest_api/v1'

HTTP_OK = 200
HTTP_NO_CONTENT = 204
HTTP_NOT_FOUND = 404
HTTP_INTERNAL_SERVER_ERROR = 500


def _paged_results(results, request):
    if request.get('page_size') == '-1':
        return HTTP_OK, results

    if request.get('page', '1') != '1':
        return HTTP_NOT_FOUND, {"detail": "Invalid page"}

    return HTTP_OK, {
        'count': len(results),
        'next': None,
        'previous': None,
        'results': results,
    }


class _MockPDCServerRequestHandler(BaseHTTPRequestHandler, object):
    class HttpNotFoundError(Exception):
        pass

    """
    Mocked PDC server.
    """
    data = {
        'products': {
            "epel": {
                "name": "EPEL",
                "short": "epel",
                "active": True,
                "product_versions": [
                    "epel-6",
                    "epel-7"
                ],
                "allowed_push_targets": []
            },
            "fedora": {
                "name": "Fedora",
                "short": "fedora",
                "active": True,
                "product_versions": [
                    "fedora-27",
                    "fedora-rawhide"
                ],
                "allowed_push_targets": []
            }
        },
        'cpes': {
            1: {
                "cpe": "cpe:/o:redhat:enterprise_linux:7::workstation",
                "description": "RHEL 7 Workstation",
                "id": 1
            }
        },
        'auth': {
            'token': {
                'obtain': {
                    'token': '1'
                }
            }
        }
    }
    last_comment = ''

    def _find_available_pk(self, data):
        """
        Return key not yet used in data.
        """
        if data:
            return max(data) + 1
        return 1

    def _data(self):
        content_length = int(self.headers['Content-Length'])
        if content_length == 0:
            return None
        raw_data = self.rfile.read(content_length)
        return json.loads(raw_data.decode())

    def _send_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        self.wfile.write(json.dumps(data).encode())

    def _get_data_item_and_request(self):
        if not self.path.startswith(API_PATH + '/'):
            raise self.HttpNotFoundError()

        data_path = self.path[len(API_PATH) + 1:]
        data_path_and_request = data_path.split('?', 1)
        data_path = data_path_and_request[0]

        if len(data_path_and_request) == 2:
            request_part = data_path_and_request[1]
            request_part = request_part.split('&')
            request = dict(key_value.split('=', 1) for key_value in request_part)
        else:
            request = {}

        path_components = data_path.split('/')
        item = self.data
        parent_item = None
        pk = None
        try:
            if not path_components[-1]:
                path_components.pop()
            for path_component in path_components:
                parent_item = item
                pk = path_component
                # If keys are numerical, omit using string as key.
                existing_pk = list(item.keys())[0]
                if isinstance(existing_pk, int):
                    pk = int(path_component)
                item = item[pk]
        except KeyError:
            raise self.HttpNotFoundError()

        return item, parent_item, pk, request

    def _do_GET(self, item, parent_item, pk, request):
        status_code = HTTP_OK
        if item == self.data['products'] and 'short' in request:
            short = request['short']
            status_code, data = _paged_results([item[short]], request)
        elif item in self.data.values():
            status_code, data = _paged_results(list(item.values()), request)
        else:
            data = item
        return status_code, data

    def _do_POST(self, item, parent_item, pk, request):
        data = self._data()
        pk = self._find_available_pk(item)
        data['id'] = pk
        item[pk] = data
        return HTTP_OK, data

    def _do_PATCH(self, item, parent_item, pk, request):
        data = self._data()
        _MockPDCServerRequestHandler.last_comment = self.headers.get('PDC-Change-Comment')
        item.update(data)
        return HTTP_OK, data

    def _do_PUT(self, item, parent_item, pk, request):
        data = self._data()
        if 'id' in item:
            data['id'] = pk
        parent_item[pk] = data
        return HTTP_OK, data

    def _do_DELETE(self, item, parent_item, pk, request):
        del parent_item[pk]
        return HTTP_NO_CONTENT, 'No content'

    def _do(self, method):
        try:
            item, parent_item, pk, request = self._get_data_item_and_request()
            status_code, data = method(item, parent_item, pk, request)
            self._send_response(status_code, data)
        except self.HttpNotFoundError:
            self._send_response(HTTP_NOT_FOUND, '')
        except Exception as e:
            traceback.print_exc()
            data = {'detail': str(e)}
            self._send_response(HTTP_INTERNAL_SERVER_ERROR, data)

    def do_GET(self):
        self._do(self._do_GET)

    def do_POST(self):
        self._do(self._do_POST)

    def do_PATCH(self):
        self._do(self._do_PATCH)

    def do_PUT(self):
        self._do(self._do_PUT)

    def do_DELETE(self):
        self._do(self._do_DELETE)

    def log_message(self, format, *args):
        """
        Omit printing on console.
        """
        pass

    # Workaround for 'Connection reset by peer' errors in Python 2.6.
    def handle(self):
        time.sleep(0.001)
        super(_MockPDCServerRequestHandler, self).handle()


class PDCClientTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        port_value = os.getenv(PORT_ENV_VAR_NAME)
        cls.port = int(port_value) if port_value else DEFAULT_PORT

        server_name_value = os.getenv(SERVER_ENV_VAR_NAME)
        cls.server_name = server_name_value if server_name_value else DEFAULT_SERVER

        cls.server = HTTPServer((cls.server_name, cls.port), _MockPDCServerRequestHandler)

        cls.server_thread = Thread(target=cls.server.serve_forever)
        cls.server_thread.setDaemon(True)
        cls.server_thread.start()

        cls.url = 'http://{server}:{port}{api_path}'.format(
            server=cls.server_name,
            port=cls.port,
            api_path=API_PATH,
        )

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        # Python 2.6 compatibility
        if not hasattr(PDCClientTestCase, 'url'):
            PDCClientTestCase.setUpClass()

        self.client = PDCClient(
            server=self.url,
            ssl_verify=False,
        )

    def test_get_attr(self):
        response = self.client.products()
        self.assertEqual(
            response.get('count'), len(_MockPDCServerRequestHandler.data['products']))

    def test_get_attr_not_found(self):
        with self.assertRaises(BeanBagException) as context:
            self.client.bad_api()

        self.assertEqual(
            context.exception.response.status_code, HTTP_NOT_FOUND)

    def test_get_item(self):
        response = self.client['products']()
        self.assertEqual(
            response.get('count'), len(_MockPDCServerRequestHandler.data['products']))

    def test_get_item_not_found(self):
        with self.assertRaises(BeanBagException) as context:
            self.client['bad-resource']()

        self.assertEqual(
            context.exception.response.status_code, HTTP_NOT_FOUND)

    def test_get_attr_attr(self):
        response = self.client.products.fedora()
        self.assertEqual(
            response, _MockPDCServerRequestHandler.data['products']['fedora'])

    def test_get_attr_attr_not_found(self):
        products = self.client.products

        with self.assertRaises(BeanBagException) as context:
            products.bad_id()

        self.assertEqual(
            context.exception.response.status_code, HTTP_NOT_FOUND)

    def test_get_item_item(self):
        response = self.client['products']['fedora']()
        self.assertEqual(
            response, _MockPDCServerRequestHandler.data['products']['fedora'])

    def test_get_item_item_not_found(self):
        products = self.client['products']

        with self.assertRaises(BeanBagException) as context:
            products['bad-resource']()

        self.assertEqual(
            context.exception.response.status_code, HTTP_NOT_FOUND)

    def test_patch_item(self):
        self.client.cpes[1] += {'description': 'TEST'}
        self.assertEqual(_MockPDCServerRequestHandler.data['cpes'][1]['description'], 'TEST')

        self.client['cpes'][1] += {'description': 'TEST2'}
        self.assertEqual(_MockPDCServerRequestHandler.data['cpes'][1]['description'], 'TEST2')

    def test_patch_attr(self):
        active = not _MockPDCServerRequestHandler.data['products']['epel']['active']
        self.client.products.epel += {'active': active}
        self.assertEqual(_MockPDCServerRequestHandler.data['products']['epel']['active'], active)

        active = not active
        self.client['products'].epel += {'active': active}
        self.assertEqual(_MockPDCServerRequestHandler.data['products']['epel']['active'], active)

    def test_put_item(self):
        new_data = {
            "cpe": "cpe:/o:redhat:enterprise_linux:6::workstation",
            "description": "RHEL 6 Workstation",
        }
        self.client.cpes[1] = new_data
        new_data['id'] = 1
        self.assertDictEqual(_MockPDCServerRequestHandler.data['cpes'][1], new_data)

    def test_put_attr(self):
        new_data = dict(_MockPDCServerRequestHandler.data['products']['epel'])
        new_data['active'] = not new_data['active']
        self.assertNotEqual(_MockPDCServerRequestHandler.data['products']['epel']['active'], new_data['active'])
        self.client.products.epel = new_data
        self.assertDictEqual(_MockPDCServerRequestHandler.data['products']['epel'], new_data)

    def test_post_and_delete(self):
        new_data = {
            "cpe": "cpe:/o:redhat:enterprise_linux:5::workstation",
            "description": "RHEL 5 Workstation",
        }

        self.assertEqual(len(_MockPDCServerRequestHandler.data['cpes']), 1)

        # post request (create)
        response = self.client.cpes(new_data)
        new_id = response['id']
        self.assertEqual(len(_MockPDCServerRequestHandler.data['cpes']), new_id)
        self.assertTrue(new_id in _MockPDCServerRequestHandler.data['cpes'])
        new_data['id'] = new_id
        self.assertDictEqual(_MockPDCServerRequestHandler.data['cpes'][new_id], new_data)

        # delete
        del self.client.cpes[new_id]
        self.assertEqual(len(_MockPDCServerRequestHandler.data['cpes']), 1)
        self.assertTrue(new_id not in _MockPDCServerRequestHandler.data['cpes'])

    def test_bad_delete(self):
        with self.assertRaises(AttributeError):
            del self.client['bad_resource']

        with self.assertRaises(AttributeError):
            del self.client.bad_resource

    def test_bad_put(self):
        with self.assertRaises(BeanBagException):
            self.client['bad_resource'] = {}

        with self.assertRaises(BeanBagException):
            self.client.bad_resource = {}

    def test_str(self):
        self.assertEqual(str(self.client.products.fedora), self.url + '/products/fedora')
        self.assertEqual(str(self.client), self.url + '/')
        self.assertEqual(str(self.client._), self.url + '/')
        self.assertEqual(str(self.client._._), self.url + '/')
        self.assertEqual(str(self.client.products), self.url + '/products')
        self.assertEqual(str(self.client.products._), self.url + '/products/')
        self.assertEqual(str(self.client._._.products._._), self.url + '/products/')

    def test_eq(self):
        self.assertEqual(self.client.products, self.client.products)
        self.assertEqual(self.client['products'], self.client['products'])
        self.assertEqual(self.client.products, self.client['products'])
        self.assertEqual(self.client.products.fedora, self.client['products']['fedora'])
        self.assertEqual(self.client._.products.fedora._, self.client['products/']['fedora/'])

    def test_set_comment(self):
        self.client.set_comment('TEST')
        self.client.cpes[1] += {'description': 'TEST'}
        self.assertEqual(_MockPDCServerRequestHandler.last_comment, 'TEST')

    def test_results(self):
        products = list(self.client.products.results())
        self.assertEqual(len(products), 2)

        products = list(self.client.products.results(short='fedora'))
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]['short'], 'fedora')

        with self.assertRaises(BeanBagException):
            list(self.client.bad_resource.results())

    def test_results_list(self):
        products = list(self.client.products.results(page_size=-1))
        self.assertEqual(len(products), 2)

        products = list(self.client.products.results(short='fedora'))
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]['short'], 'fedora')

        with self.assertRaises(BeanBagException):
            list(self.client.bad_resource.results())

    def test_no_results_error(self):
        with self.assertRaises(NoResultsError):
            list(self.client.products.fedora.results())

    def test_get_paged(self):
        products = list(self.client.get_paged(self.client.products))
        self.assertEqual(len(products), 2)

        products = list(self.client.get_paged(self.client.products, short='fedora'))
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]['short'], 'fedora')
