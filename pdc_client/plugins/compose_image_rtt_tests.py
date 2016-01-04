# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 Red Hat
# Licensed under The MIT License (MIT)
# http://opensource.org/licenses/MIT
#
import json

from pdc_client.plugin_helpers import PDCClientPlugin, add_parser_arguments, extract_arguments


class ComposeImageRTTTestsPlugin(PDCClientPlugin):
    def register(self):
        self.set_command('compose-image-rtt-tests')
        list_parser = self.add_action('list', help='list all compose image rtt tests')
        add_parser_arguments(list_parser, {'compose': {},
                                           'variant': {},
                                           'arch': {},
                                           'file_name': {},
                                           'test_result': {}},
                             group='Filtering')
        list_parser.set_defaults(func=self.list_compose_image_rtt_tests)

        info_parser = self.add_action('info', help='display details of a compose image RTT test')
        self._add_common_arguments(info_parser)
        info_parser.set_defaults(func=self.compose_image_rtt_test_info)

        help_text = 'update an existing compose image\'s RTT test result (untested, passed or failed)'
        update_parser = self.add_action('update', help=help_text)
        self._add_common_arguments(update_parser)
        add_parser_arguments(update_parser, {'test_result': {'choices': ['passed', 'failed', 'untested']}})
        update_parser.set_defaults(func=self.compose_image_rtt_test_update)

    def _add_common_arguments(self, parser):
        parser.add_argument('compose_id', metavar='COMPOSE_ID')
        parser.add_argument('variant_uid', metavar='VARIANT_UID')
        parser.add_argument('arch', metavar='ARCH')
        parser.add_argument('file_name', metavar='FILE_NAME')

    def _print_compose_image_rtt_test_list(self, rtt_tests):
        if rtt_tests:
            print '{0:<50} {1:20} {2:10} {3:70} {4}\n'.format(
                'Compose',
                'Variant',
                'Arch',
                'File Name',
                'Test Result')
            for test in rtt_tests:
                print '{0:<50} {1:20} {2:10} {3:70} {4}'.format(
                    test['compose'],
                    test['variant'],
                    test['arch'],
                    test['file_name'],
                    test['test_result'])

    def list_compose_image_rtt_tests(self, args):
        filters = extract_arguments(args)
        rtt_tests = self.client.get_paged(self.client['compose-image-rtt-tests']._, **filters)
        if args.json:
            print json.dumps(list(rtt_tests))
            return
        self._print_compose_image_rtt_test_list(rtt_tests)

    def _display_test_info_detail(self, args, test_info):
        if args.json:
            print json.dumps(test_info)
            return
        fmt = '{0:20} {1}'
        print fmt.format('Compose', test_info['compose'])
        print fmt.format('Variant', test_info['variant'])
        print fmt.format('Arch', test_info['arch'])
        print fmt.format('File Name', test_info['file_name'])
        print fmt.format('Test Result', test_info['test_result'])

    def compose_image_rtt_test_info(self, args):
        test_info =\
            self.client['compose-image-rtt-tests'][args.compose_id][args.variant_uid][args.arch][args.file_name]._()
        self._display_test_info_detail(args, test_info)

    def compose_image_rtt_test_update(self, args):
        patch_data = extract_arguments(args)
        self.client['compose-image-rtt-tests'][args.compose_id][args.variant_uid][args.arch][args.file_name]._ += \
            patch_data
        data = {'compose': args.compose_id,
                'variant': args.variant_uid,
                'arch': args.arch,
                'file_name': args.file_name}
        data.update(patch_data)
        self._display_test_info_detail(args, data)


PLUGIN_CLASSES = [ComposeImageRTTTestsPlugin]
