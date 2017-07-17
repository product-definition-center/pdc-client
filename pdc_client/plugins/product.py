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


class ProductPlugin(PDCClientPlugin):
    def register(self):
        self.set_command('product')

        # CRUD: CREATE
        create_parser = self.add_action('create', help='create new product')
        self.add_product_arguments(create_parser, required=True)
        create_parser.set_defaults(func=self.product_create)

        # CRUD: READ one (info)
        info_parser = self.add_action('info', help='display details of a product')
        info_parser.add_argument('short', metavar="SHORT")
        info_parser.set_defaults(func=self.product_info)

        # CRUD: READ many (list)
        list_parser = self.add_action('list', help='list all products')
        list_parser.add_argument('--inactive', action='store_true',
                                 help='show only inactive products')
        list_parser.add_argument('--all', action='store_true',
                                 help='show both active and inactive products')
        list_parser.set_defaults(func=self.product_list)

        # CRUD: UPDATE
        update_parser = self.add_action('update', help='update an existing product')
        update_parser.add_argument('short', metavar='SHORT')
        self.add_product_arguments(update_parser)
        update_parser.set_defaults(func=self.product_update)

        # CRUD: DELETE
        # not implemented

    def add_product_arguments(self, parser, required=False):
        required_args = {
            'short': {},
            'name': {},
        }
        optional_args = {
        }
        add_create_update_args(parser, required_args, optional_args, required)

    def prep_for_print(self, record):
        result = OrderedDict()
        result["Short Name"] = record["short"]
        result["Name"] = record["name"]
        result["Active"] = record["active"] and "yes" or "no"
        return result

    def product_create(self, args):
        data = self.get_product_data(args)
        self.logger.debug('Creating product with data {0}'.format(data))
        response = self.client.products._(data)
        self.product_info(args, response['short'])

    def product_info(self, args, short=None):
        short = short or args.short
        product = self.client.products[short]._()
        if args.json:
            print(json.dumps(product))
            return

        fmt = '{0:20} {1}'
        for key, value in self.prep_for_print(product).items():
            print(fmt.format(key, value))

    def product_list(self, args):
        filters = {}
        if args.inactive:
            filters['active'] = False
        elif not args.all:
            filters['active'] = True

        products = self.client.get_paged(self.client["products"]._, **filters)

        if args.json:
            print(json.dumps(list(products)))
            return

        fmt = '{0:25} {1:35} {2}'
        for num, product in enumerate(products):
            data = self.prep_for_print(product)
            if num == 0:
                print(fmt.format(*data.keys()))
            print(fmt.format(*data.values()))

    def product_update(self, args):
        data = self.get_product_data(args)

        if data:
            self.logger.debug('Updating product {0} with data {1}'.format(args.short, data))
            response = self.client.products[args.short]._('PATCH', data)
            short = response['short']
        else:
            self.logger.info('No change required, not making a request')

        self.product_info(args, short)

    def get_product_data(self, args):
        data = extract_arguments(args)
        return data


PLUGIN_CLASSES = [ProductPlugin]
