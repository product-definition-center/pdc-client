# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 Red Hat
# Licensed under The MIT License (MIT)
# http://opensource.org/licenses/MIT
#
import json

from pdc_client.plugin_helpers import (PDCClientPlugin,
                                       extract_arguments,
                                       add_parser_arguments,
                                       add_create_update_args)


class ComposeTreeLocationsPlugin(PDCClientPlugin):
    def register(self):
        self.set_command('compose-tree-locations')

        list_parser = self.add_action('list', help='list all compose-variant-arch \
                                                    relevant to location')
        add_parser_arguments(list_parser, {'compose': {},
                                           'variant': {},
                                           'arch': {},
                                           'location': {},
                                           'scheme': {}},
                             group='Filtering')
        list_parser.set_defaults(func=self.compose_tree_location_list)

        info_parser = self.add_action('info', help='display details of a compose-variant-arch \
                                                    relevant to a location')
        self._add_common_arguments(info_parser)
        info_parser.set_defaults(func=self.compose_tree_location_info)

        help_text = 'update an existing compose-tree-locations\'s fields scheme, synced-content and url'
        update_parser = self.add_action('update', help=help_text)
        self._add_common_arguments(update_parser)
        add_parser_arguments(update_parser, {'scheme': {},
                                             'url': {},
                                             'synced_content': {'nargs': '*', 'choices': ['binary', 'debug',
                                                                                          'source']}})
        update_parser.set_defaults(func=self.compose_tree_location_update)

        create_parser = self.add_action('create', help='create a new compose-variant-arch relevant to a location')
        self.add_compose_tree_location_arguments(create_parser, required=True)
        create_parser.set_defaults(func=self.compose_tree_location_create)

        delete_parser = self.add_action('delete', help='delete a compose-variant-arch relevant to a location')
        self._add_common_arguments(delete_parser)
        delete_parser.set_defaults(func=self.compose_tree_location_delete)

    def _add_common_arguments(self, parser):
        parser.add_argument('compose_id', metavar='COMPOSE_ID')
        parser.add_argument('variant_uid', metavar='VARIANT_UID')
        parser.add_argument('arch', metavar='ARCH')
        parser.add_argument('location', metavar='LOCATION')
        parser.add_argument('scheme', metavar='SCHEME')

    def add_compose_tree_location_arguments(self, parser, required=False):
        required_args = {
            'compose': {},
            'variant': {},
            'arch': {},
            'location': {},
            'scheme': {},
            'synced_content': {'nargs': '*', 'choices': ['binary', 'debug', 'source']},
            'url': {}}
        optional_args = {}
        add_create_update_args(parser, required_args, optional_args, required)

    def _display_compose_tree_location_info(self, args, compose_tree_location_info):
        if args.json:
            print json.dumps(compose_tree_location_info)
            return
        fmt = '{0:20} {1}'
        print fmt.format('Compose', compose_tree_location_info['compose'])
        print fmt.format('Variant', compose_tree_location_info['variant'])
        print fmt.format('Arch', compose_tree_location_info['arch'])
        print fmt.format('Location', compose_tree_location_info['location'])
        print fmt.format('Scheme', compose_tree_location_info['scheme'])
        print fmt.format('Synced Content', compose_tree_location_info['synced_content'])
        print fmt.format('Url', compose_tree_location_info['url'])

    def compose_tree_location_list(self, args):
        filters = extract_arguments(args)
        compose_tree_locations = self.client.get_paged(self.client['compose-tree-locations']._, **filters)
        if args.json:
            print json.dumps(list(compose_tree_locations))
            return
        fmt = '{0:<50} {1:20} {2:10} {3:10} {4:10} {5:40} {6}'
        if compose_tree_locations:
            print fmt.format(
                'Compose',
                'Variant',
                'Arch',
                'Location',
                'Scheme',
                'Synced Content',
                'Url')
            print
            for compose_tree_location in compose_tree_locations:
                print fmt.format(
                    compose_tree_location['compose'],
                    compose_tree_location['variant'],
                    compose_tree_location['arch'],
                    compose_tree_location['location'],
                    compose_tree_location['scheme'],
                    compose_tree_location['synced_content'],
                    compose_tree_location['url'])

    def compose_tree_location_info(self, args):
        compose_tree_location_info =\
            self.client['compose-tree-locations'][args.compose_id][args.variant_uid][args.arch][args.location][args.scheme]._()
        self._display_compose_tree_location_info(args, compose_tree_location_info)

    def compose_tree_location_update(self, args):
        data = extract_arguments(args)
        compose_tree_location_info =\
            self.client['compose-tree-locations'][args.compose_id][args.variant_uid][args.arch][args.location][args.scheme]._('PATCH', data)
        self._display_compose_tree_location_info(args, compose_tree_location_info)

    def compose_tree_location_create(self, args):
        data = extract_arguments(args)
        response = self.client['compose-tree-locations']._(data)
        self._display_compose_tree_location_info(args, response)

    def compose_tree_location_delete(self, args):
        data = extract_arguments(args)
        self.client['compose-tree-locations'][args.compose_id][args.variant_uid][args.arch][args.location][args.scheme]\
            ._("DELETE", data)

PLUGIN_CLASSES = [ComposeTreeLocationsPlugin]
