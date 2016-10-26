# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 Red Hat
# Licensed under The MIT License (MIT)
# http://opensource.org/licenses/MIT
#
from pdc_client.test_helpers import CLITestCase
from pdc_client.runner import Runner


class ComposeFullImportTestCase(CLITestCase):
    def setUp(self):
        self.runner = Runner()
        self.runner.setup()

    def _setup_detail(self, api):
        obj = {'set_locations': 1,
               'compose': 'Awesome-product-7.0-0',
               'imported images': 1,
               'imported rpms': 1}

        api.add_endpoint('rpc/compose-full-import',
                         'POST', obj)

    def test_create(self, api):
        self._setup_detail(api)
        composeinfo_path = self.data_file_abspath('composeinfo.json')
        image_manifest_path = self.data_file_abspath('image_manifest.json')
        rpm_manifest_path = self.data_file_abspath('rpm_manifest.json')

        with self.expect_output('detail.txt'):
            self.runner.run(['compose-full-import', 'create',
                             '--composeinfo', composeinfo_path,
                             '--image-manifest', image_manifest_path,
                             '--rpm-manifest', rpm_manifest_path,
                             '--release-id', 'rhel-7.3',
                             '--url', 'abc.com',
                             '--location', 'nay',
                             '--scheme', 'http'])
