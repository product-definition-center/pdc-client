# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 Red Hat
# Licensed under The MIT License (MIT)
# http://opensource.org/licenses/MIT
#

from __future__ import print_function

import sys
import argparse
import beanbag
import requests
import os
import os.path
import logging
import imp
import json

# The client supports Bash completion if argcomplete Python package is
# installed. To enable it, run this in your terminal (assuming pdc is somewhere
# on path).
#
#     eval "$(register-python-argcomplete pdc)"
#
# This is only a temporary solution, when the client is packaged, a completion
# file should be shipped with it and installed to /etc/bash_completion.d/.
try:
    import argcomplete
except ImportError:
    class argcomplete(object):
        @classmethod
        def autocomplete(*args):
            pass

import pdc_client


# Default path to plugins. This line will be replaced when installing with real
# install plugin path (usually '/usr/share/pdc-client/plugins').
DEFAULT_PLUGIN_DIR = os.path.join(os.path.dirname(__file__), 'plugins')

# A list of paths to directories where plugins should be loaded from.
# The purpose of the plugins is to extend the default behaviour.
PLUGIN_DIRS = [path for path in
               os.getenv('PDC_CLIENT_PLUGIN_PATH', '').split(':')
               if path]
if not PLUGIN_DIRS:
    PLUGIN_DIRS = [DEFAULT_PLUGIN_DIR]

DEFAULT_PLUGINS = [
    'base_product.py',
    'build_image_rtt_tests.py',
    'build_images.py',
    'component.py',
    'compose_image_rtt_tests.py',
    'compose.py',
    'compose_full_import.py',
    'compose_tree_locations.py',
    'contact.py',
    'group_resource_permissions.py',
    'image.py',
    'permission.py',
    'product.py',
    'product_version.py',
    'release.py',
    'release_variant.py',
    'repo.py',
    'rpm.py'
]

CONFIG_PLUGINS_KEY_NAME = 'plugins'


class Runner(object):
    def __init__(self):
        self.raw_plugins = []
        self.plugins = []
        self.logger = logging.getLogger('pdc')

    def load_plugins(self):
        config = None
        server = None
        idx_s, idx_server = (None, None)
        plugins_set = set(DEFAULT_PLUGINS)
        args = sys.argv[1:]
        try:
            idx_s = args.index('-s')
        except (ValueError, IndexError):
            pass
        try:
            idx_server = args.index('--server')
        except (ValueError, IndexError):
            pass
        try:
            server = args[max(idx_s, idx_server) + 1]
        except TypeError:
            pass

        if server is not None:
            try:
                config = pdc_client.server_configuration(server)
            except pdc_client.config.ServerConfigError as e:
                self.logger.error(e)
                sys.exit(1)

        if config:
            plugins = config.get(CONFIG_PLUGINS_KEY_NAME, [])
            if not isinstance(plugins, list):
                raise TypeError('Plugins must be a list')
            plugins_set.update(set(plugins))

        for dir in PLUGIN_DIRS:
            self.logger.debug('Loading plugins from {0}'.format(dir))
            for name in os.listdir(dir):
                if not name.endswith('.py') or name not in plugins_set:
                    continue
                try:
                    module_name = name[:-3]
                    file, pathname, description = imp.find_module(module_name, [dir])
                    plugin = imp.load_module(module_name, file, pathname, description)
                    self.logger.debug('Loaded plugin {0}'.format(module_name))
                    self.raw_plugins.append(plugin)
                    if hasattr(plugin, 'PLUGIN_CLASSES'):
                        for p in plugin.PLUGIN_CLASSES:
                            self.logger.debug('Instantiating {0}'.format(p.__name__))
                            self.plugins.append(p(self))
                except Exception as e:
                    self.logger.error('Failed to load plugin "{0}": {1}'.format(module_name, e))
                finally:
                    if file:
                        file.close()

    def run_hook(self, hook, *args, **kwargs):
        """
        Loop over all plugins and invoke function `hook` with `args` and
        `kwargs` in each of them. If the plugin does not have the function, it
        is skipped.
        """
        for plugin in self.raw_plugins:
            if hasattr(plugin, hook):
                self.logger.debug('Calling hook {0} in plugin {1}'.format(hook, plugin.__name__))
                getattr(plugin, hook)(*args, **kwargs)

    def setup(self):
        self.load_plugins()

        self.parser = argparse.ArgumentParser(description='PDC Client')
        self.parser.add_argument('-s', '--server', default='stage',
                                 help='API URL or shortcut from config file')

        ssl_group = self.parser.add_mutually_exclusive_group()
        ssl_group.add_argument('-k', '--insecure', action='store_true',
                               help='Disable SSL certificate verification')
        # ca-cert corresponds to requests session verify attribute:
        # http://docs.python-requests.org/en/master/user/advanced/#ssl-cert-verification
        ssl_group.add_argument("--ca-cert", help="Path to CA certificate file or directory")

        self.parser.add_argument('--debug', action='store_true', help=argparse.SUPPRESS)
        self.parser.add_argument('--json', action='store_true',
                                 help='display output as JSON')
        self.parser.add_argument('--page-size', dest='page_size', type=int,
                                 help='change page size in response, -1 means that get all pages of data in one request')
        self.parser.add_argument('--page', dest='page', type=int,
                                 help='change page in response')
        self.parser.add_argument('--version', action='version',
                                 version='%(prog)s ' + pdc_client.__version__)

        subparsers = self.parser.add_subparsers(metavar='COMMAND')
        subparsers.required = True

        for plugin in sorted(self.plugins):
            plugin._before_register(subparsers)
            plugin.register()

        argcomplete.autocomplete(self.parser)

    def run(self, args=None):
        self.args = self.parser.parse_args(args=args)
        if self.args.insecure:
            requests.packages.urllib3.disable_warnings(
                requests.packages.urllib3.exceptions.InsecureRequestWarning)
            ssl_verify = False
        elif self.args.ca_cert:
            ssl_verify = self.args.ca_cert
        else:
            ssl_verify = None

        try:
            self.client = pdc_client.PDCClientWithPage(self.args.server, page_size=self.args.page_size, ssl_verify=ssl_verify, page=self.args.page)
        except pdc_client.config.ServerConfigError as e:
            self.logger.error(e)
            sys.exit(1)

        try:
            self.args.func(self.args)
        except beanbag.BeanBagException as ex:
            print("Server returned following error: [{0}] {1}".format(ex.response.status_code, ex.response.reason), file=sys.stderr)
            print("Details: ", end='', file=sys.stderr)
            try:
                data = ex.response.json()
                if len(data) == 1 and 'detail' in data:
                    print(data['detail'], file=sys.stderr)
                else:
                    print("", file=sys.stderr)
                    json.dump(data, sys.stderr, indent=2,
                              sort_keys=True, separators=(",", ": "))
            except Exception:
                # response was not JSON
                print('Failed to parse error response.', file=sys.stderr)
            sys.exit(1)
