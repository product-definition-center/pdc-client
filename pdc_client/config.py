#
# Copyright (c) 2018 Red Hat
# Licensed under The MIT License (MIT)
# http://opensource.org/licenses/MIT
#

import json
import logging
import os

CONFIG_URL_KEY_NAME = 'host'
CONFIG_INSECURE_KEY_NAME = 'insecure'
CONFIG_SSL_VERIFY_KEY_NAME = 'ssl-verify'
CONFIG_DEVELOP_KEY_NAME = 'develop'
CONFIG_TOKEN_KEY_NAME = 'token'

logger = logging.getLogger(__name__)


class ServerConfigError(Exception):
    """ Base class for ServerConfiguration exceptions. """
    pass


class ServerConfigNotFoundError(ServerConfigError):
    """ Server configuration is missing. """
    pass


class ServerConfigMissingUrlError(ServerConfigError):
    """ Server configuration is missing URL. """
    pass


class ServerConfigConflictError(ServerConfigError):
    """ Same server defined in multiple config files. """
    pass


def _read_config_dir(file_path):
    # get all json files in config directory and merge them
    data = {}
    if os.path.isdir(file_path):
        files_list = os.listdir(file_path)
        for file_name in files_list:
            if file_name.endswith('.json'):
                file_abspath = os.path.join(file_path, file_name)
                with open(file_abspath, 'r') as config_file:
                    config_dict = json.load(config_file)
                    same_key = set(data.keys()) & set(config_dict.keys())
                    if same_key:
                        message = "'{}' keys existed in both {} config files".format(
                            same_key, files_list)
                        raise ServerConfigConflictError(message)

                    data.update(config_dict)
    return data


def _read_config_file(file_path):
    data = {}
    if os.path.isfile(file_path):
        with open(file_path, 'r') as config_file:
            data = json.load(config_file)
    return data


def _default_server_configuration(server):
    if "://" not in server:
        message = "Failed to find configuration for server \"{}\"".format(server)
        raise ServerConfigNotFoundError(message)

    server_config = {CONFIG_URL_KEY_NAME: server}
    return ServerConfig(server_config)


class ServerConfigManager(object):
    """
    Provides configuration for given server name.

    Configuration is read from multiple files or directories in order they're
    passed to constructor. Files and directories are read lazily when needed
    and at most once (cached for later access).
    """
    def __init__(self, *paths):
        self.paths = iter(paths)
        self.config = {}

    def _read_next_config(self):
        path = next(self.paths)
        if os.path.isfile(path):
            return _read_config_file(path)
        return _read_config_dir(path)

    def get(self, server):
        """
        Returns ServerConfig instance with configuration given server.

        @raises ServerConfigConflictError:
            if configuration directory contains configuration for same server
            multiple times

        @raises ServerConfigMissingUrlError: if URL is not specified in the configuration
        """
        server_config = self.config.get(server)
        try:
            while server_config is None:
                new_config = self._read_next_config()
                server_config = new_config.get(server)
                new_config.update(self.config)
                self.config = new_config
        except StopIteration:
            return _default_server_configuration(server)

        if CONFIG_URL_KEY_NAME not in server_config:
            message = "'{}' must be specified in configuration for '{}'".format(
                CONFIG_URL_KEY_NAME, server)
            raise ServerConfigMissingUrlError(message)

        return ServerConfig(server_config)


class ServerConfig(object):
    def __init__(self, config):
        self.config = config

    def get(self, option_name, default_value=None):
        return self.config.get(option_name, default_value)

    def url(self):
        return self.config[CONFIG_URL_KEY_NAME]

    def ssl_verify(self):
        cfg_ssl_verify = self.config.get(CONFIG_SSL_VERIFY_KEY_NAME)
        if cfg_ssl_verify is not None:
            return cfg_ssl_verify

        insecure = self.config.get(CONFIG_INSECURE_KEY_NAME)
        if insecure is not None:
            message = "'{}' option is deprecated; please use '{}' instead".format(
                CONFIG_INSECURE_KEY_NAME, CONFIG_SSL_VERIFY_KEY_NAME)
            logger.warning(message)
            return not insecure

        return True

    def is_development(self):
        return self.config.get(CONFIG_DEVELOP_KEY_NAME, False)

    def token(self):
        return self.config.get(CONFIG_TOKEN_KEY_NAME)
