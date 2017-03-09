# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Red Hat
# Licensed under The MIT License (MIT)
# http://opensource.org/licenses/MIT
#
from pdc_client.test_helpers import CLITestCase
from pdc_client.runner import Runner


class ProductVersionTestCase(CLITestCase):
    def setUp(self):
        self.runner = Runner()
        self.runner.setup()
        self.release_variant_detail = {
            'release': 'test-release-1.0',
            'uid': 'Server',
            'id': 'Server',
            'name': 'Server Variant',
            'type': 'variant',
            'arches': ['ppc64', 's390x', 'x86_64'],
        }
        self.maxDiff = None

    def _setup_release_variant_detail(self, api):
        api.add_endpoint('release-variants/test-release-1.0/Server', 'GET', self.release_variant_detail)

    def test_create(self, api):
        api.add_endpoint('release-variants', 'POST', self.release_variant_detail)
        self._setup_release_variant_detail(api)

        # compare stdout with data/info.txt
        with self.expect_output('info.txt'):
            # run the command
            self.runner.run([
                'release-variant',
                'create',
                '--release', 'test-release-1.0',
                '--uid', 'Server',
                '--id', 'Server',
                '--name', 'Server Variant',
                '--type', 'variant',
                '--arch', 'ppc64',
                '--arch', 's390x',
                '--arch', 'x86_64',
            ])

        # test api calls made by the command
        self.assertEqual(api.calls, {
            'release-variants': [
                ('POST', self.release_variant_detail),
            ],
            'release-variants/test-release-1.0/Server': [
                ('GET', {
                }),
            ],
        })

    def test_info(self, api):
        self._setup_release_variant_detail(api)

        # compare stdout with data/info.txt
        with self.expect_output('info.txt'):
           self.runner.run([
                'release-variant',
                'info',
                'test-release-1.0',
                'Server',
            ])

        # test api calls made by the command
        self.assertEqual(api.calls, {
            'release-variants/test-release-1.0/Server': [
                ('GET', {
                }),
            ],
        })

    def test_list_all(self, api):
        api.add_endpoint('release-variants', 'GET', [self.release_variant_detail])

        # compare stdout with data/list-all.txt
        with self.expect_output('list-all.txt'):
            # run the command
            self.runner.run([
                'release-variant',
                'list',
            ])

        # test api calls made by the command
        self.assertEqual(api.calls, {
            'release-variants': [
                ('GET', {
                    'ordering': ['variant_uid', 'release'],
                    'page': 1,
                }),
            ],
        })

    def test_list_release(self, api):
        api.add_endpoint('release-variants', 'GET', [self.release_variant_detail])

        # compare stdout with data/list-all.txt
        with self.expect_output('list-all.txt'):
            # run the command
            self.runner.run([
                'release-variant',
                'list',
                '--release', 'test-release-1.0',
            ])

        # test api calls made by the command
        self.assertEqual(api.calls, {
            'release-variants': [
                ('GET', {
                    'release': 'test-release-1.0',
                    'ordering': ['variant_uid', 'release'],
                    'page': 1,
                }),
            ],
        })

    def test_update(self, api):
        api.add_endpoint('release-variants/test-release-1.0/Server', 'PATCH', self.release_variant_detail)
        self._setup_release_variant_detail(api)

        with self.expect_output('info.txt'):
            # run the command
            self.runner.run([
                'release-variant',
                'update',
                'test-release-1.0',
                'Server',
                '--name', 'NewName',
            ])

        # test api calls made by the command
        self.assertEqual(api.calls, {
            'release-variants/test-release-1.0/Server': [
                ('PATCH', {
                    'name': 'NewName',
                }),
                ('GET', {
                }),
            ],
        })

    def test_update_uid(self, api):
        api.add_endpoint('release-variants/test-release-1.0/FooVariant', 'PATCH', self.release_variant_detail)
        self._setup_release_variant_detail(api)

        with self.expect_output('info.txt'):
            # run the command
            self.runner.run([
                'release-variant',
                'update',
                'test-release-1.0',
                'FooVariant',
                '--uid', 'Server',
            ])

        # test api calls made by the command
        self.assertEqual(api.calls, {
            'release-variants/test-release-1.0/FooVariant': [
                ('PATCH', {
                    'uid': 'Server',
                }),
            ],
            'release-variants/test-release-1.0/Server': [
                ('GET', {
                }),
            ],
        })
