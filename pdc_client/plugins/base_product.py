# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Red Hat
# Licensed under The MIT License (MIT)
# http://opensource.org/licenses/MIT
#

from __future__ import print_function

import json
from collections import OrderedDict

from pdc_client.plugin_helpers import (PDCClientPlugin,
                                       extract_arguments,
                                       add_create_update_args)


class BaseProductPlugin(PDCClientPlugin):
    command = 'base-product'

    def register(self):
        self.set_command()

        # CRUD: CREATE
        create_parser = self.add_action('create', help='create new base product')
        self.add_base_product_arguments(create_parser, required=True)
        create_parser.set_defaults(func=self.base_product_create)

        # CRUD: READ one (info)
        info_parser = self.add_action('info', help='display details of a base product')
        info_parser.add_argument('base_product_id')
        info_parser.set_defaults(func=self.base_product_info)

        # CRUD: READ many (list)
        list_parser = self.add_action('list', help='list all products')
        list_parser.add_argument('--inactive', action='store_true',
                                 help='show only inactive products')
        list_parser.add_argument('--all', action='store_true',
                                 help='show both active and inactive products')
        list_parser.set_defaults(func=self.base_product_list)

        # CRUD: UPDATE
        update_parser = self.add_action('update', help='update an existing base product')
        update_parser.add_argument('base_product_id')
        self.add_base_product_arguments(update_parser)
        update_parser.set_defaults(func=self.base_product_update)

        # CRUD: DELETE
        # not implemented

    def add_base_product_arguments(self, parser, required=False):
        required_args = {
            'short': {},
            'name': {},
            'version': {},
            'type': {"dest": "release_type"},
        }
        optional_args = {
        }
        add_create_update_args(parser, required_args, optional_args, required)

    def prep_for_print(self, record):
        result = OrderedDict()
        result["Base Product ID"] = record["base_product_id"]
        result["Short Name"] = record["short"]
        result["Name"] = record["name"]
        result["Version"] = record["version"]
        result["Type"] = record["release_type"]
        return result

    def base_product_create(self, args):
        data = self.get_base_product_data(args)
        self.logger.debug('Creating base product with data {0}'.format(data))
        response = self.client["base-products"]._(data)
        self.base_product_info(args, response['base_product_id'])

    def base_product_info(self, args, base_product_id=None):
        base_product_id = base_product_id or args.base_product_id
        base_product = self.client["base-products"][base_product_id]._()

        fmt = '{0:20} {1}'
        for key, value in self.prep_for_print(base_product).items():
            print(fmt.format(key, value))

    def base_product_list(self, args):
        filters = {}

        base_products = self.client.get_paged(self.client["base-products"]._, **filters)
        if args.json:
            print(json.dumps(list(base_products)))
            return

        fmt = '{0:30} {1:20} {2:35} {3:10} {4}'
        for num, base_product in enumerate(base_products):
            data = self.prep_for_print(base_product)
            if num == 0:
                print(fmt.format(*data.keys()))
            print(fmt.format(*data.values()))

    def base_product_update(self, args):
        data = self.get_base_product_data(args)

        base_product_id = args.base_product_id
        if data:
            self.logger.debug('Updating base product {0} with data {1}'.format(base_product_id, data))
            response = self.client["base-products"][base_product_id]._('PATCH', data)
            base_product_id = response['base_product_id']
        else:
            self.logger.info('No change required, not making a request')

        self.base_product_info(args, base_product_id)

    def get_base_product_data(self, args):
        data = extract_arguments(args)
        return data


PLUGIN_CLASSES = [BaseProductPlugin]
