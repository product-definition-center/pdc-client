# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 Red Hat
# Licensed under The MIT License (MIT)
# http://opensource.org/licenses/MIT
#
from pdc_client.test_helpers import CLITestCase
from pdc_client.runner import Runner
from copy import deepcopy


class ComposeImageRTTTestsTestCase(CLITestCase):
    def setUp(self):
        self.runner = Runner()
        self.runner.setup()

    def _setup_list(self, api):
        api.add_endpoint('compose-image-rtt-tests', 'GET', [
            {"arch": "x86_64",
             "compose": "RHEL-7.0-{0}".format(x),
             "variant": "Client",
             "test_result": "untested",
             "file_name": "RHEL-7.0-1-Client-x86_64-boot.iso"}
            for x in range(30)
        ])

    def _setup_detail(self, api):
        obj = {"arch": "x86_64",
               "compose": "RHEL-7.0-0",
               "variant": "Client",
               "test_result": "untested",
               "file_name": "RHEL-7.0-1-Client-x86_64-boot.iso"}
        api.add_endpoint("""compose-image-rtt-tests/RHEL-7.0-0/Client/x86_64/RHEL-7.0-1-Client-x86_64-boot.iso""",
                         'GET', obj)
        # PATCH test result to passed
        obj_update = deepcopy(obj)
        obj_update["test_result"] = "passed"
        api.add_endpoint("""compose-image-rtt-tests/RHEL-7.0-0/Client/x86_64/RHEL-7.0-1-Client-x86_64-boot.iso""",
                         'PATCH', obj_update)

    def test_list(self, api):
        self._setup_list(api)
        with self.expect_output('list_multi_page.txt'):
            self.runner.run(['compose-image-rtt-tests', 'list'])
        self.assertEqual(api.calls['compose-image-rtt-tests'],
                         [('GET', {'page': 1}),
                          ('GET', {'page': 2})])

    def test_info(self, api):
        self._setup_detail(api)
        with self.expect_output('detail.json', parse_json=True):
            self.runner.run(['--json', 'compose-image-rtt-tests', 'info', 'RHEL-7.0-0', 'Client',
                             'x86_64', 'RHEL-7.0-1-Client-x86_64-boot.iso'])
        self.assertEqual(
            api.calls['compose-image-rtt-tests/RHEL-7.0-0/Client/x86_64/RHEL-7.0-1-Client-x86_64-boot.iso'],
            [('GET', {})])

    def test_update(self, api):
        self._setup_detail(api)
        with self.expect_output('detail_for_patch.json', parse_json=True):
            self.runner.run(['--json', 'compose-image-rtt-tests', 'update', 'RHEL-7.0-0', 'Client',
                             'x86_64', 'RHEL-7.0-1-Client-x86_64-boot.iso', '--test-result', 'passed'])
        self.assertEqual(
            api.calls['compose-image-rtt-tests/RHEL-7.0-0/Client/x86_64/RHEL-7.0-1-Client-x86_64-boot.iso'],
            [('PATCH', {"test_result": "passed"})])
