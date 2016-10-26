# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 Red Hat
# Licensed under The MIT License (MIT)
# http://opensource.org/licenses/MIT
#

from __future__ import print_function

import json
import sys
import os

from pdc_client.plugin_helpers import PDCClientPlugin, add_create_update_args, extract_arguments


class ComposeFullImportPlugin(PDCClientPlugin):
    def register(self):
        self.set_command('compose-full-import')
        create_parser = self.add_action('create', help='Import RPMs, images, create new compose and set compose tree location',
                                        description='The composeinfo, rpm_manifest and image_manifest values ' +
                                                    'should be actual JSON representation of composeinfo, ' +
                                                    'rpm manifest and image manifest, as stored in ' +
                                                    'composeinfo.json, rpm-manifest.json and image-manifest.json files. ' +
                                                    'location, url, scheme are used to set compose tree location.')
        self.add_compose_full_import_arguments(create_parser, required=True)
        create_parser.set_defaults(func=self.compose_full_import_create)

    def add_compose_full_import_arguments(self, parser, required=False):
        required_args = {
            'release_id': {'type': str},
            'composeinfo': {},
            'rpm_manifest': {},
            'image_manifest': {},
            'location': {'type': str},
            'url': {'type': str},
            'scheme': {'type': str}}
        optional_args = {}
        add_create_update_args(parser, required_args, optional_args, required)

    def _display_compose_import_info(self, args, compose_import_info):
        if args.json:
            print(json.dumps(compose_import_info))
            return
        fmt = '{0:20} {1}'
        print(fmt.format('Compose', compose_import_info['compose']))
        print(fmt.format('Imported Images', compose_import_info['imported images']))
        print(fmt.format('Imported Rpms', compose_import_info['imported rpms']))
        print(fmt.format('Set_locations', compose_import_info['set_locations']))

    def compose_full_import_create(self, args):
        parser_args = self._get_value_from_json(args)
        data = extract_arguments(parser_args)
        response = self.client['rpc/compose-full-import']._(data)
        self._display_compose_import_info(parser_args, response)

    def _get_value_from_json(self, args):
        args.data__composeinfo = self._read_json_file(args.data__composeinfo)
        args.data__image_manifest = self._read_json_file(args.data__image_manifest)
        args.data__rpm_manifest = self._read_json_file(args.data__rpm_manifest)
        return args

    def _read_json_file(self, path):
        if os.path.isfile(path):
            with open(path, 'r') as f:
                data = json.load(f)
        else:
            print("Error: '%s' file can't find, please verify it" % path)
            sys.exit(1)
        return data


PLUGIN_CLASSES = [ComposeFullImportPlugin]
