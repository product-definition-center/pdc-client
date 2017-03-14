# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Red Hat
# Licensed under The MIT License (MIT)
# http://opensource.org/licenses/MIT
#

from __future__ import print_function

import json
try:
    from collections import OrderedDict
except ImportError:
    # Python 2.6 needs this back-port
    from ordereddict import OrderedDict

from pdc_client.plugin_helpers import (PDCClientPlugin,
                                       extract_arguments,
                                       add_create_update_args)


class ProductVersionPlugin(PDCClientPlugin):
    def register(self):
        self.set_command('product-version')

        # CRUD: CREATE
        create_parser = self.add_action('create', help='create new product_version')
        self.add_product_version_arguments(create_parser, required=True)
        create_parser.set_defaults(func=self.product_version_create)

        # CRUD: READ one (info)
        info_parser = self.add_action('info', help='display details of a product_version')
        info_parser.add_argument('product_version_id', metavar="PRODUCT_VERSION_ID")
        info_parser.set_defaults(func=self.product_version_info)

        # CRUD: READ many (list)
        list_parser = self.add_action('list', help='list all product_versions')
        list_parser.add_argument('--inactive', action='store_true',
                                 help='show only inactive product_versions')
        list_parser.add_argument('--all', action='store_true',
                                 help='show both active and inactive product_versions')
        list_parser.set_defaults(func=self.product_version_list)

        # CRUD: UPDATE
        update_parser = self.add_action('update', help='update an existing product_version')
        update_parser.add_argument('product_version_id')
        self.add_product_version_arguments(update_parser)
        update_parser.set_defaults(func=self.product_version_update)

        # CRUD: DELETE
        # not implemented

    def add_product_version_arguments(self, parser, required=False):
        required_args = {
            'short': {},
            'name': {},
            'version': {},
            'product': {},
        }
        optional_args = {
        }
        add_create_update_args(parser, required_args, optional_args, required)

    def prep_for_print(self, record):
        result = OrderedDict()
        result["Product Version ID"] = record["product_version_id"]
        result["Short Name"] = record["short"]
        result["Name"] = record["name"]
        result["Product"] = record["product"]
        result["Active"] = record["active"] and "yes" or "no"
        return result

    def product_version_create(self, args):
        data = self.get_product_version_data(args)
        self.logger.debug('Creating product_version with data {0}'.format(data))
        response = self.client["product-versions"]._(data)
        self.product_version_info(args, response['product_version_id'])

    def product_version_info(self, args, product_version_id=None):
        product_version_id = product_version_id or args.product_version_id
        product_version = self.client["product-versions"][product_version_id]._()
        if args.json:
            print(json.dumps(product_version))
            return

        fmt = '{0:20} {1}'
        for key, value in self.prep_for_print(product_version).items():
            print(fmt.format(key, value))

    def product_version_list(self, args):
        filters = {}
        if args.inactive:
            filters['active'] = False
        elif not args.all:
            filters['active'] = True

        product_versions = self.client.get_paged(self.client["product-versions"]._, **filters)

        if args.json:
            print(self.to_json(list(product_versions)))
            return

        fmt = '{0:25} {1:25} {2:35} {3:15} {4}'
        for num, product_version in enumerate(product_versions):
            data = self.prep_for_print(product_version)
            if num == 0:
                print(fmt.format(*data.keys()))
            print(fmt.format(*data.values()))

    def product_version_update(self, args):
        data = self.get_product_version_data(args)

        if data:
            self.logger.debug('Updating product_version {0} with data {1}'.format(args.product_version_id, data))
            response = self.client["product-versions"][args.product_version_id]._('PATCH', data)
            product_version_id = response['product_version_id']
        else:
            self.logger.info('No change required, not making a request')

        self.product_version_info(args, product_version_id)

    def get_product_version_data(self, args):
        data = extract_arguments(args)
        return data


PLUGIN_CLASSES = [ProductVersionPlugin]
