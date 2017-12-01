# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 Red Hat
# Licensed under The MIT License (MIT)
# http://opensource.org/licenses/MIT
#

from __future__ import print_function

import itertools
import json
import os
from os.path import expanduser, isfile, isdir
import sys
from subprocess import Popen, PIPE

import requests
import requests_kerberos
from beanbag import BeanBag, BeanBagException

GLOBAL_CONFIG_DIR = '/etc/pdc.d/'
USER_SPECIFIC_CONFIG_FILE = expanduser('~/.config/pdc/client_config.json')
CONFIG_URL_KEY_NAME = 'host'
CONFIG_INSECURE_KEY_NAME = 'insecure'
CONFIG_SSL_VERIFY_KEY_NAME = 'ssl-verify'
CONFIG_DEVELOP_KEY_NAME = 'develop'
CONFIG_TOKEN_KEY_NAME = 'token'
# PDC warning field in response header
PDC_WARNING_HEADER_NAME = 'pdc-warning'


def get_version():
    fdir = os.path.dirname(os.path.realpath(__file__))
    if isdir(os.path.join(fdir, '..', '.git')):
        # running from git, try to get info
        old_dir = os.getcwd()
        os.chdir(fdir)
        git = Popen(["git", "describe", "--tags"], stdout=PIPE)
        base_ver = git.communicate()[0].strip()
        git = Popen(["git", "rev-parse", "--short", "HEAD"], stdout=PIPE)
        hash = git.communicate()[0]
        os.chdir(old_dir)
        if sys.version_info[0] == 3:
            # Python 3 compatibility
            base_ver = base_ver.decode('utf-8')
            hash = hash.decode('utf-8')
        return base_ver + "-" + hash
    else:
        # not running from git, get info from pkg_resources
        import pkg_resources
        try:
            return pkg_resources.get_distribution("pdc_client").version
        except pkg_resources.DistributionNotFound:
            return 'unknown'


__version__ = get_version()


def _read_dir(file_path):
    # get all json files in /etc/pdc.d/ directory and merge them
    data = {}
    if isdir(file_path):
        files_list = os.listdir(file_path)
        for file_name in files_list:
            if file_name.endswith('.json'):
                file_abspath = os.path.join(file_path, file_name)
                with open(file_abspath, 'r') as config_file:
                    config_dict = json.load(config_file)
                    same_key = set(data.keys()) & set(config_dict.keys())
                    if same_key:
                        print("Error: '%s' keys existed in both %s config files" % (same_key, files_list))
                        sys.exit(1)
                    else:
                        data.update(config_dict)
    return data


def _read_file(file_path):
    data = {}
    if isfile(file_path):
        with open(file_path, 'r') as config_file:
            data = json.load(config_file)
    return data


def _is_page(response):
    return isinstance(response, dict) \
        and set(response.keys()) == set(['count', 'previous', 'results', 'next'])


def read_config_file(server_alias):
    result = _read_dir(GLOBAL_CONFIG_DIR).get(server_alias, {})
    result.update(_read_file(USER_SPECIFIC_CONFIG_FILE).get(server_alias, {}))
    return result


class NoResultsError(Exception):
    """ Exception for getting all pages of data
        Raise this NoResultsError if there is an unexpected data
        returned when get all pages of data by results() function.

        Data members:
             * response -- response object
    """
    def __init__(self, response):
        """Create a NoResultsError"""

        self.response = response

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.response)

    def __str__(self):
        msg = "Unexpected data here"
        if self.response:
            msg = "%s - response: %s" % (msg, str(self.response))
        return msg


class _SetAttributeWrapper(object):
    """
    Passes all __setattr__() calls to a client after _initialized is True.

    Attribute client must be defined in derived class.

    Set _initialized to True after all attributes for derived object are set.
    """
    _initialized = False
    client = None

    def __setattr__(self, name, value):
        if self._initialized:
            return self.client.__setattr__(name, value)
        return super(_SetAttributeWrapper, self).__setattr__(name, value)


class PDCClient(object):
    """BeanBag wrapper specialized for PDC access.

    This class wraps general BeanBag.v1 objects, but provides easy-to-use
    interface that can use configuration files for specifying server
    connections. The authentication token is automatically retrieved (if
    needed).
    ::
            # Example: Get per page of release
            client = PDCClient(<server>)
            client.releases._()
            client["releases"]._()
            ...

            # Example: create one release data
            client["releases"]._(<dict data>)
            ...

            # Example: Iterate all pages of releases
            # Will raise NoResultsError with response when return unexpected result.
            try:
                for r in client["releases"].results():
                    ...
            except NoResultsError as e:
                # handle e.response ...
    """
    def __init__(self, server, token=None, develop=None, ssl_verify=None, page_size=None):
        """
        Create new pdc client instance.

        Once the class is instantiated, use it as you would use a regular
        BeanBag object. Please look at its documentation for how to use this
        class to perform requests.

        :param server:     Server API url or server name from configuration
        :param token:      An authentication token string of visiting pdc server
        :param develop:    This is use for dev mode
        :param ssl_verify: True for validating SSL certificates with system CA
                           store; False for no validation; path to CA file or
                           directory to use for validation otherwise
        :param page_size:  This is a number of data which is returned per page.
                           A -1 means that pdc server will return all the data in
                           one request.
        """
        self.page_size = page_size
        if not server:
            raise TypeError('Server must be specified')
        self.session = requests.Session()
        config = read_config_file(server)

        # Command line must *always* override configuration
        if config:
            try:
                url = config[CONFIG_URL_KEY_NAME]
            except KeyError:
                sys.stderr.write("'{}' must be specified in configuration for '{}'".format(
                    CONFIG_URL_KEY_NAME, server))
                sys.exit(1)

            if ssl_verify is None:
                cfg_ssl_verify = config.get(CONFIG_SSL_VERIFY_KEY_NAME)
                insecure = config.get(CONFIG_INSECURE_KEY_NAME)
                if insecure is not None:
                    sys.stderr.write("Warning: '{}' option is deprecated; please use '{}' "
                                     "instead\n".format(
                                         CONFIG_INSECURE_KEY_NAME, CONFIG_SSL_VERIFY_KEY_NAME))
                    ssl_verify = not insecure
                if cfg_ssl_verify is not None:
                    ssl_verify = cfg_ssl_verify
            if develop is None:
                develop = config.get(CONFIG_DEVELOP_KEY_NAME, develop)
            if token is None:
                token = config.get(CONFIG_TOKEN_KEY_NAME, token)
        else:
            url = server
            if ssl_verify is None:
                ssl_verify = True

        self.session.verify = ssl_verify

        if not develop:
            # For local environment, we don't need to require a token,
            # just access API directly.
            # REQUIRED, OPTIONAL, DISABLED
            self.session.auth = requests_kerberos.HTTPKerberosAuth(
                mutual_authentication=requests_kerberos.DISABLED)

        def decode(req):
            result = json.loads(req.text or req.content)
            if req.headers.get(PDC_WARNING_HEADER_NAME):
                sys.stderr.write("PDC warning: %s\n\n" % req.headers.get(PDC_WARNING_HEADER_NAME))
            return result

        content_type = "application/json"
        encode = json.dumps
        self.client = _BeanBagWrapper(BeanBag(url, session=self.session, fmt=(content_type, encode, decode)),
                                      page_size)
        if not develop:
            # For develop environment, we don't need to require a token
            if not token:
                token = self.obtain_token()
            self.session.headers["Authorization"] = "Token %s" % token

    def obtain_token(self):
        """
        Try to obtain token from all end-points that were ever used to serve the
        token. If the request returns 404 NOT FOUND, retry with older version of
        the URL.
        """
        token_end_points = ('token/obtain',
                            'obtain-token',
                            'obtain_token')
        for end_point in token_end_points:
            try:
                return self.auth[end_point]._(page_size=None)['token']
            except BeanBagException as e:
                if e.response.status_code != 404:
                    raise
        raise Exception('Could not obtain token from any known URL.')

    def get_paged(self, res, **kwargs):
        """
        This call is equivalent to ``res(**kwargs)``, only it retrieves all pages
        and returns the results joined into a single iterable. The advantage over
        retrieving everything at once is that the result can be consumed immediately.

        :param res:     what resource to connect to
        :param kwargs:  filters to be used
        ::
            # Example: Iterate over all active releases
            for release in client.get_paged(client['releases']._, active=True):
                ...

        This function is obsolete and not recommended.
        """
        if self.page_size is not None:
            kwargs['page_size'] = self.page_size
            if self.page_size <= 0:
                # If page_size <= 0, pagination will be disable.
                return res(**kwargs)

        def worker():
            kwargs['page'] = 1
            while True:
                response = res(**kwargs)
                yield response['results']
                if response['next']:
                    kwargs['page'] += 1
                else:
                    break
        return itertools.chain.from_iterable(worker())

    def __call__(self, *args, **kwargs):
        return self.client(*args, **kwargs)

    def __getattr__(self, name):
        """
            If the first attribute/endpoint with "-", just replace with "_"  in name
            ::
                # Example: get endpoint
                client = PDCClient(<server>)
                # Get the endpoint base-products/
                client.base_products._
                # Get the endpoint base-products/test_123/
                client.base_products.test_123._
                # Get the endpoint products/
                client.products._
        """
        if name != "_":
            name = name.replace("_", "-")
        return self.client.__getattr__(name)

    def __getitem__(self, *args, **kwargs):
        return self.client.__getitem__(*args, **kwargs)

    def __setitem__(self, name, value):
        return self.client.__setitem__(name, value)

    def __str__(self):
        return str(self.client)

    def set_comment(self, comment):
        """Set PDC Change comment to be stored on the server.

        Once you set the comment, it will be sent in all subsequent requests.

        :param comment:     what comment to send to the server
        :paramtype comment: string
        """
        self.session.headers["PDC-Change-Comment"] = comment


class _BeanBagWrapper(_SetAttributeWrapper):
    """
       Wrapper of BeanBag's attributes and items.

       This class wraps attributes and items of Beanbag to let page_size of
       PDCClient's constructor work.
    """

    def __init__(self, client, page_size):
        self.client = client
        self.page_size = page_size

        self._initialized = True

    def __call__(self, *args, **kwargs):
        if 'page_size' not in kwargs:
            kwargs['page_size'] = self.page_size
        return self.client(*args, **kwargs)

    def __getattr__(self, name):
        return _BeanBagWrapper(self.client.__getattr__(name), self.page_size)

    def __delattr__(self, name):
        return self.client.__delattr__(name)

    def __getitem__(self, *args, **kwargs):
        return _BeanBagWrapper(self.client.__getitem__(*args, **kwargs), self.page_size)

    def __setitem__(self, name, value):
        return self.client.__setitem__(name, value)

    def __delitem__(self, name):
        return self.client.__delitem__(name)

    def __iadd__(self, value):
        return self.client.__iadd__(value)

    def __eq__(self, other):
        return self.client == other.client

    def __str__(self):
        return str(self.client)

    def results(self, *args, **kwargs):
        """
           Return an iterator with all pages of data.
           Return NoResultsError with response if there is unexpected data.
        """
        def worker():
            kwargs['page'] = 1
            while True:
                response = self.client(*args, **kwargs)
                if isinstance(response, list):
                    yield response
                    break
                elif _is_page(response):
                    yield response['results']
                    if response['next']:
                        kwargs['page'] += 1
                    else:
                        break
                else:
                    raise NoResultsError(response)

        return itertools.chain.from_iterable(worker())


class PDCClientWithPage(PDCClient):
    """
    PDCClient wrapper specialized for setting page in get_paged function.
    """
    def __init__(self, server, token=None, develop=None, ssl_verify=None, page_size=None, page=None):
        """
        Create new client instance with page prarameter.
        Other params are all used for base class.
        :param page:  the page number of the data.
        """
        super(PDCClientWithPage, self).__init__(server, token, develop, ssl_verify, page_size)
        self.page = page

    def get_paged(self, res, **kwargs):
        """
        Re-write the ge_paged here, and add the self.page check.
        This call is equivalent to ``res(**kwargs)``, if there is no self.page
        parameter,only it retrieves all pages and returns the results joined into
        a single iterable. The advantage over retrieving everything at once is that
        the result can be consumed immediately.

        :param res:     what resource to connect to
        :param kwargs:  filters to be used

        ::

            # Example: Iterate over all active releases
            for release in client.get_paged(client['releases']._, active=True):
                ...

        If there is a self.page parameter here, just return that page's data with the
        self.page_size.
        """
        if self.page_size is not None:
            kwargs['page_size'] = self.page_size
            if self.page_size <= 0:
                # If page_size <= 0, pagination will be disable.
                return res(**kwargs)

        if self.page is not None:
            kwargs['page'] = self.page
            allinfo = res(**kwargs)
            return allinfo['results']

        def worker():
            kwargs['page'] = 1
            while True:
                response = res(**kwargs)
                yield response['results']
                if response['next']:
                    kwargs['page'] += 1
                else:
                    break
        return itertools.chain.from_iterable(worker())
