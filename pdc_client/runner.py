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
from pdc_client.utils import pretty_print


# A list of paths to directories where plugins should be loaded from.
# The purpose of the plugins is to extend the default behaviour.
LOCAL_DIR = os.path.join(os.path.dirname(__file__), 'plugins')
INSTALLED_DIR = os.path.join('/usr/share/pdc-client', 'plugins')
PLUGIN_DIRS = [LOCAL_DIR] if not os.path.exists(INSTALLED_DIR) else [INSTALLED_DIR]

DEFAULT_PLUGINS = [
    'group_resource_permissions.py',
    'build_image_rtt_tests.py',
    'build_images.py',
    'component.py',
    'compose_image_rtt_tests.py',
    'compose.py',
    'compose_full_import.py',
    'compose_tree_locations.py',
    'contact.py',
    'image.py',
    'permission.py',
    'release.py',
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

        if server:
            config = pdc_client.read_config_file(server)
        if config and config.get(CONFIG_PLUGINS_KEY_NAME):
            plugins = config.get(CONFIG_PLUGINS_KEY_NAME)
            if not isinstance(plugins, list):
                raise TypeError('Plugins must be a list')
            plugins_set.update(set(plugins))

        for dir in PLUGIN_DIRS:
            self.logger.debug('Loading plugins from {0}'.format(dir))
            for name in os.listdir(dir):
                if not name.endswith('.py') or name not in plugins_set:
                    continue
                file, pathname, description = imp.find_module(name[:-3], [dir])
                plugin = imp.load_module(name[:-3], file, pathname, description)
                self.logger.debug('Loaded plugin {0}'.format(name[:-3]))
                self.raw_plugins.append(plugin)
                if hasattr(plugin, 'PLUGIN_CLASSES'):
                    for p in plugin.PLUGIN_CLASSES:
                        self.logger.debug('Instantiating {0}'.format(p.__name__))
                        self.plugins.append(p(self))

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

        self.parser.add_argument('-k', '--insecure', action='store_true',
                                 help='Disable SSL certificate verification')
        # ca-cert corresponds to requests session verify attribute:
        # http://docs.python-requests.org/en/master/user/advanced/#ssl-cert-verification
        self.parser.add_argument("--ca-cert", help="Path to CA certificate file or directory")

        self.parser.add_argument('--debug', action='store_true', help=argparse.SUPPRESS)
        self.parser.add_argument('--json', action='store_true',
                                 help='display output as JSON')
        self.parser.add_argument('--page-size', dest='page_size', type=int,
                                 help='change page size in response')
        self.parser.add_argument('--version', action='version',
                                 version='%(prog)s ' + pdc_client.__version__)

        subparsers = self.parser.add_subparsers(metavar='COMMAND')

        for plugin in self.plugins:
            plugin._before_register(subparsers)
            plugin.register()

        argcomplete.autocomplete(self.parser)

    def run(self, args=None):
        self.args = self.parser.parse_args(args=args)
        ssl_verify = self.args.ca_cert or not self.args.insecure
        if self.args.insecure:
            requests.packages.urllib3.disable_warnings(
                requests.packages.urllib3.exceptions.InsecureRequestWarning)
        self.client = pdc_client.PDCClient(self.args.server, page_size=self.args.page_size,
                                           ssl_verify=ssl_verify)
        try:
            self.args.func(self.args)
        except beanbag.BeanBagException as exc:
            self.print_error_header(exc)
            json = None
            try:
                json = exc.response.json()
                pretty_print(json, file=sys.stderr)
            except ValueError:
                # Response was not JSON
                print('Failed to parse error response.', file=sys.stderr)
            except TypeError as e:
                # Failed to pretty print.
                print('Failed to correctly display error message. Please file a bug.',
                      file=sys.stderr)
                self.logger.info(json, exc_info=e)
            sys.exit(1)

    def print_error_header(self, exc):
        if exc.response.status_code > 500:
            print('Internal server error. Please consider reporting a bug.',
                  file=sys.stderr)
        else:
            headers = {
                400: 'bad request data',
                401: 'unauthorized',
                404: 'not found',
                409: 'conflict',
            }
            print('Client error: {0}.'.format(headers.get(exc.response.status_code, 'unknown')),
                  file=sys.stderr)
