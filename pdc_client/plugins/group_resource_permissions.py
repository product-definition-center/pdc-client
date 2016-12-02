# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 Red Hat
# Licensed under The MIT License (MIT)
# http://opensource.org/licenses/MIT
#

from __future__ import print_function

import json

from pdc_client.plugin_helpers import (PDCClientPlugin,
                                       extract_arguments,
                                       add_parser_arguments,
                                       add_create_update_args)


class GroupResourcePermissionsPlugin(PDCClientPlugin):
    def register(self):
        self.set_command('group-resource-permissions')
        list_parser = self.add_action('list', help='list all groups and their resource permissions')
        add_parser_arguments(list_parser, {'resource': {},
                                           'permission': {},
                                           'group': {}},
                             group='Filtering')
        list_parser.set_defaults(func=self.list_group_resource_permission)

        info_parser = self.add_action('info', help='display details about a group resource permission')
        info_parser.add_argument('id', metavar='ID')
        info_parser.set_defaults(func=self.group_resource_permission_info)

        update_parser = self.add_action('update', help='update an existing group resource permission')
        update_parser.add_argument('id', metavar='ID')
        self.add_update_argument(update_parser, required=True)
        update_parser.set_defaults(func=self.group_resource_permission_update)

        create_parser = self.add_action('create', help='grant a resource permission to a group')
        self.add_create_argument(create_parser, required=True)
        create_parser.set_defaults(func=self.group_resource_permission_create)

        delete_parser = self.add_action('delete', help='revoke a resource permission from a group')
        delete_parser.add_argument('id', metavar='ID')
        delete_parser.set_defaults(func=self.group_resource_permission_delete)

    def add_create_argument(self, parser, required=True):
        required_args = {'resource': {}, 'permission': {}, 'group': {}}
        add_create_update_args(parser, required_args, {}, required)

    def add_update_argument(self, parser, required=True):
        optional_args = {'resource': {}, 'permission': {}, 'group': {}}
        add_create_update_args(parser, {}, optional_args, required)

    def print_group_resource_permissions(self, args):
        fmt = '{0:<5} {1:20} {2:90} {3}'
        start_line = True
        for obj in args:
            if start_line:
                start_line = False
                print(fmt.format('ID', 'Group', 'Resource', 'Permission'))
                print()
            print(fmt.format(obj['id'], obj['group'], obj['resource'], obj['permission']))

    def list_group_resource_permission(self, args):
        filters = extract_arguments(args)
        results = self.client.get_paged(self.client['auth/group-resource-permissions']._, **filters)
        if args.json:
            print(json.dumps(list(results)))
            return

        self.print_group_resource_permissions(results)

    def group_resource_permission_info(self, args, id=None):
        obj_id = id or args.id
        results = self.client['auth/group-resource-permissions'][obj_id]._()
        if args.json:
            print(json.dumps(results))
            return
        fmt = '{0:20} {1}'
        print(fmt.format('ID', results['id']))
        print(fmt.format('Resource', results['resource']))
        print(fmt.format('Permission', results['permission']))
        print(fmt.format('Group', results['group']))

    def group_resource_permission_update(self, args):
        data = extract_arguments(args)
        if data:
            self.logger.debug('Updating group resource permission %s with data %r', args.id, data)
            self.client['auth/group-resource-permissions'][args.id]._ += data
        else:
            self.logger.debug('Empty data, skipping request')
        self.group_resource_permission_info(args)

    def group_resource_permission_create(self, args):
        data = extract_arguments(args)
        self.logger.debug('Creating group resource permission with data %r', data)
        response = self.client['auth/group-resource-permissions']._(data)
        self.group_resource_permission_info(args, response['id'])

    def group_resource_permission_delete(self, args):
        data = extract_arguments(args)
        self.logger.debug('Deleting : group resource permission %s', args.id)
        self.client['auth/group-resource-permissions'][args.id]._("DELETE", data)


PLUGIN_CLASSES = [GroupResourcePermissionsPlugin]
