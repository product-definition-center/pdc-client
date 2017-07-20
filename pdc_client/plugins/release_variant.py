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


class ReleaseVariantPlugin(PDCClientPlugin):
    def register(self):
        self.set_command('release-variant')

        # CRUD: CREATE
        create_parser = self.add_action('create', help='create new release_variant')
        self.add_release_variant_arguments(create_parser, required=True)
        create_parser.set_defaults(func=self.release_variant_create)

        # CRUD: READ one (info)
        info_parser = self.add_action('info', help='display details of a release_variant')
        info_parser.add_argument('release')
        info_parser.add_argument('uid')
        info_parser.set_defaults(func=self.release_variant_info, required=True)

        # CRUD: READ many (list)
        list_parser = self.add_action('list', help='list all release_variants')
        self.add_release_variant_arguments(list_parser)
        list_parser.set_defaults(func=self.release_variant_list)

        # CRUD: UPDATE
        update_parser = self.add_action('update', help='update an existing release_variant')
        update_parser.add_argument('release')
        update_parser.add_argument('uid')
        self.add_release_variant_arguments(update_parser)
        update_parser.set_defaults(func=self.release_variant_update)

        # CRUD: DELETE
        # not implemented

    def add_release_variant_arguments(self, parser, required=False):
        required_args = OrderedDict()
        required_args["release"] = {}
        required_args["uid"] = {}
        required_args["id"] = {}
        required_args["name"] = {}
        required_args["type"] = {}
        required_args["arch"] = {"action": "append", "dest": "arches"}
        optional_args = OrderedDict()
        add_create_update_args(parser, required_args, optional_args, required)

    def prep_for_print(self, record):
        result = OrderedDict()
        result["Release"] = record["release"]
        result["UID"] = record["uid"]
        result["ID"] = record["id"]
        result["Name"] = record["name"]
        result["Type"] = record["type"]
        result["Arches"] = ",".join(sorted(record["arches"]))
        return result

    def release_variant_create(self, args):
        data = self.get_release_variant_data(args)
        self.logger.debug('Creating release_variant with data {0}'.format(data))
        response = self.client["release-variants"]._(data)
        self.release_variant_info(args, response["release"], response['uid'])

    def release_variant_info(self, args, release=None, uid=None):
        release = release or args.release
        uid = uid or args.uid
        variant = self.client["release-variants"][release][uid]._()
        if args.json:
            print(json.dumps(variant))
            return
        fmt = '{0:20} {1}'
        for key, value in self.prep_for_print(variant).items():
            print(fmt.format(key, value))

    def release_variant_list(self, args):
        filters = {}
        for i in dir(args):
            if not i.startswith("data_"):
                continue
            key = i[6:]
            value = getattr(args, i)
            if value is not None:
                filters[key] = value

        # TODO: ordering doesn't seem to be working correctly (arg order has to be reversed)
        release_variants = self.client.get_paged(self.client["release-variants"]._, ordering=["variant_uid", "release"], **filters)

        if args.json:
            print(json.dumps(list(release_variants)))
            return

        fmt = '{0:35} {1:25} {2:25} {3:35} {4}'
        for num, release_variant in enumerate(release_variants):
            data = self.prep_for_print(release_variant)
            if num == 0:
                print(fmt.format(*data.keys()))
            print(fmt.format(*data.values()))

    def release_variant_update(self, args):
        data = self.get_release_variant_data(args)

        release = args.release
        uid = args.uid

        if data:
            self.logger.debug('Updating release_variant {0} {1} with data {2}'.format(release, uid, data))
            response = self.client["release-variants"][release][uid]._('PATCH', data)
            release = response['release']
            uid = response['uid']
        else:
            self.logger.info('No change required, not making a request')

        self.release_variant_info(args, release, uid)

    def get_release_variant_data(self, args):
        data = extract_arguments(args)
        return data


PLUGIN_CLASSES = [ReleaseVariantPlugin]
