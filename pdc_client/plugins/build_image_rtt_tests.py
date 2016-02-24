# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 Red Hat
# Licensed under The MIT License (MIT)
# http://opensource.org/licenses/MIT
#
import json

from pdc_client.plugin_helpers import (PDCClientPlugin,
                                       extract_arguments,
                                       add_parser_arguments)


def print_build_image_rtt_list(rtt_tests):
    fmt = '{0:<10} {1:40} {2:10} {3:6}'
    start_line = True
    for rtt_test in rtt_tests:
        if start_line:
            start_line = False
            print fmt.format('ID', 'BUILD_NVR', 'FORMAT', 'TEST_RESULT')
            print
        print fmt.format(rtt_test['id'],
                         rtt_test['build_nvr'],
                         rtt_test['format'],
                         rtt_test['test_result'])


class BuildImageRttTest(PDCClientPlugin):
    def register(self):
        self.set_command('build-image-rtt-tests')
        list_parser = self.add_action('list', help='list all build image rtt tests')
        add_parser_arguments(list_parser, {'build_nvr': {},
                                           'image_format': {},
                                           'test_result': {}},
                             group='Filtering')
        list_parser.set_defaults(func=self.list_build_image_rrt_tests)

        info_parser = self.add_action('info', help='display details of \
                                                   a build image rtt tests')
        info_parser.add_argument('build_nvr', metavar='BUILD_NVR')
        info_parser.add_argument('image_format', metavar='IMAGE_FORMAT')
        info_parser.set_defaults(func=self.build_image_rrt_tests_info)

        update_parser = self.add_action('update', help='Partial update an exist \
                                                       build image rtt tests by test_result \
                                                       which value choices from \
                                                       [passed, failed, untested]')
        update_parser.add_argument('build_nvr', metavar='BUILD_NVR')
        update_parser.add_argument('image_format', metavar='IMAGE_FORMAT')
        add_parser_arguments(update_parser, {'test_result': {'choices': ['passed', 'failed', 'untested']}})
        update_parser.set_defaults(func=self.build_image_rrt_tests_update)

    def list_build_image_rrt_tests(self, args):
        filters = extract_arguments(args)
        build_images_rrt = self.client.get_paged(self.client['build-image-rtt-tests']._, **filters)
        if args.json:
            print json.dumps(list(build_images_rrt))
            return
        if build_images_rrt:
            print_build_image_rtt_list(build_images_rrt)

    def build_image_rrt_tests_info(self, args):
        build_image_rtts = self.client['build-image-rtt-tests'][args.build_nvr][args.image_format]._()
        if args.json:
            print json.dumps(build_image_rtts)
            return
        fmt = '{0:20} {1}'
        print fmt.format('ID', build_image_rtts['id'])
        print fmt.format('BUILD_NVR', build_image_rtts['build_nvr'])
        print fmt.format('FORMAT', build_image_rtts['format'])
        print fmt.format('TEST_RESULT', build_image_rtts['test_result'])

    def build_image_rrt_tests_update(self, args):
        data = extract_arguments(args)
        if data:
            self.logger.debug('Updating global component %s and %s with data %r',
                              args.build_nvr, args.image_format, data)
            self.client['build-image-rtt-tests'][args.build_nvr][args.image_format]._ += data
        else:
            self.logger.debug('Empty data, skipping request')
        self.build_image_rrt_tests_info(args)

    def _get_build_image_rtt_id(self, build_nvr, image_format):
        results = self.client['build-image-rtt-tests']._(build_nvr=build_nvr, image_format=image_format)
        if not results['count']:
            return None
        return results['results'][0]['id']


PLUGIN_CLASSES = [BuildImageRttTest]
