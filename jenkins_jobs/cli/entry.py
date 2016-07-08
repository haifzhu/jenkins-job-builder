#!/usr/bin/env python
# Copyright (C) 2015 Wayne Warren
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import io
import os
import logging
import platform
import sys

import yaml

from jenkins_jobs.cli.parser import create_parser
from jenkins_jobs import cmd
from jenkins_jobs.config import JJBConfig
from jenkins_jobs import utils
from jenkins_jobs import version

logger = logging.getLogger()


def __version__():
    return "Jenkins Job Builder version: %s" % \
        version.version_info.version_string()


class JenkinsJobs(object):
    """ This is the entry point class for the `jenkins-jobs` command line tool.
    While this class can be used programmatically by external users of the JJB
    API, the main goal here is to abstract the `jenkins_jobs` tool in a way
    that prevents test suites from caring overly much about various
    implementation details--for example, tests of subcommands must not have
    access to directly modify configuration objects, instead they must provide
    a fixture in the form of an .ini file that provides the configuration
    necessary for testing.

    External users of the JJB API may be interested in this class as an
    alternative to wrapping `jenkins_jobs` with a subprocess that execs it as a
    system command; instead, python scripts may be written that pass
    `jenkins_jobs` args directly to this class to allow programmatic setting of
    various command line parameters.
    """

    def __init__(self, args=None, **kwargs):
        if args is None:
            args = []
        self.parser = create_parser()
        self.options = self.parser.parse_args(args)

        self.jjb_config = JJBConfig(self.options.conf, **kwargs)

        if not self.options.command:
            self.parser.error("Must specify a 'command' to be performed")

        logger = logging.getLogger()
        if (self.options.log_level is not None):
            self.options.log_level = getattr(logging,
                                             self.options.log_level.upper(),
                                             logger.getEffectiveLevel())
            logger.setLevel(self.options.log_level)

        self._parse_additional()
        self.jjb_config.validate()

    def _parse_additional(self):
        for opt in ['ignore_cache', 'user', 'password',
                    'allow_empty_variables']:
            opt_val = getattr(self.options, opt, None)
            if opt_val is not None:
                setattr(self.jjb_config, opt, opt_val)

        if getattr(self.options, 'plugins_info_path', None) is not None:
            with io.open(self.options.plugins_info_path, 'r',
                         encoding='utf-8') as yaml_file:
                plugins_info = yaml.load(yaml_file)
            if not isinstance(plugins_info, list):
                self.parser.error("{0} must contain a Yaml list!".format(
                                  self.options.plugins_info_path))
            self.jjb_config.plugins_info = plugins_info

        if getattr(self.options, 'path', None):
            if hasattr(self.options.path, 'read'):
                logger.debug("Input file is stdin")
                if self.options.path.isatty():
                    if platform.system() == 'Windows':
                        key = 'CTRL+Z'
                    else:
                        key = 'CTRL+D'
                    logger.warn("Reading configuration from STDIN. "
                                "Press %s to end input.", key)
            else:
                # take list of paths
                self.options.path = self.options.path.split(os.pathsep)

                do_recurse = (getattr(self.options, 'recursive', False) or
                              self.jjb_config.recursive)

                excludes = ([e for elist in self.options.exclude
                             for e in elist.split(os.pathsep)] or
                            self.jjb_config.excludes)
                paths = []
                for path in self.options.path:
                    if do_recurse and os.path.isdir(path):
                        paths.extend(utils.recurse_path(path, excludes))
                    else:
                        paths.append(path)
                self.options.path = paths

    def execute(self):
        cmd.execute(self.options, self.jjb_config)


def main():
    argv = sys.argv[1:]
    jjb = JenkinsJobs(argv)
    jjb.execute()