# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 Red Hat
# Licensed under The MIT License (MIT)
# http://opensource.org/licenses/MIT
#
from pdc_client.runner import Runner
from pdc_client.test_helpers import CLITestCase


class BuildImageRttTestsTestCase(CLITestCase):
    def setUp(self):
        self.runner = Runner()
        self.runner.setup()
        self.detail = {
            "id": 3,
            "build_nvr": "EjaErg-1",
            "format": "vdi",
            "test_result": "passed"
        }

    def _setup_build_image_rtt_tests_detail(self, api):
        api.add_endpoint('build-image-rtt-tests', 'GET', [self.detail])

    def test_list_build_image_rtt_tests(self, api):
        api.add_endpoint('build-image-rtt-tests', 'GET', [
            {'id': x,
             'build_nvr': 'EjaErg-%s' % x,
             'format': 'vdi%s' % x,
             'test_result': 'passed'}
            for x in range(0, 25)
        ])
        with self.expect_output('list.txt'):
            self.runner.run(['build-image-rtt-tests', 'list'])
        self.assertEqual(api.calls['build-image-rtt-tests'],
                         [('GET', {'page': 1}), ('GET', {'page': 2})])

    def test_info(self, api):
        self._setup_build_image_rtt_tests_detail(api)
        api.add_endpoint('build-image-rtt-tests/EjaErg-1/vdi', 'GET', self.detail)
        with self.expect_output('build_image_rtt_tests.txt'):
            self.runner.run(['build-image-rtt-tests', 'info', 'EjaErg-1', 'vdi'])
        self.assertEqual(api.calls['build-image-rtt-tests/EjaErg-1/vdi'],
                         [('GET', {})])

    def test_update_rrt_tests(self, api):
        api.add_endpoint('build-image-rtt-tests', 'GET', [self.detail])
        api.add_endpoint('build-image-rtt-tests/EjaErg-1/vdi', 'GET', self.detail)
        api.add_endpoint('build-image-rtt-tests/EjaErg-1/vdi', 'PATCH',
                         {
                             "id": 3,
                             "build_nvr": "EjaErg-1",
                             "format": "vdi",
                             "test_result": "untested"
                         })
        with self.expect_output('build_image_rtt_tests.txt'):
            self.runner.run(['build-image-rtt-tests', 'update',
                             '--test-result', 'passed', 'EjaErg-1', 'vdi'])
        self.assertEqual(api.calls['build-image-rtt-tests/EjaErg-1/vdi'],
                         [('PATCH', {'test_result': 'passed'}), ('GET', {})])

    def test_detail_json(self, api):
        self._setup_build_image_rtt_tests_detail(api)
        api.add_endpoint('build-image-rtt-tests/EjaErg-1/vdi', 'GET', self.detail)
        with self.expect_output('detail.json', parse_json=True):
            self.runner.run(['--json', 'build-image-rtt-tests', 'info', 'EjaErg-1', 'vdi'])
