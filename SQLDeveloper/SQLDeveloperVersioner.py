#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""See docstring for SQLDeveloperVersioner class."""

from __future__ import absolute_import

import configparser
from distutils.command.config import config
import os.path

from autopkglib import Processor, ProcessorError

__all__ = ["SQLDeveloperVersioner"]

class SQLDeveloperVersioner(Processor):
    # pylint: disable=missing-docstring
    description = "Read the version.properties file inside the SQLDeveloper.app."
    input_variables = {
        "app_path": {
            "required": True,
            "description": "Path to app to find the version.properties file in.",
        }
    }
    output_variables = {"version": {"description": "Actual version of app."}}

    __doc__ = description

    # this code stolen directly from https://stackoverflow.com/a/8555776
    def add_section_header(self, properties_file, header_name="properties"):
        # configparser.ConfigParser requires at least one section header in a properties file.
        # Our properties file doesn't have one, so add a header to it on the fly.
        yield '[{}]\n'.format(header_name)
        for line in properties_file:
            yield line


    def main(self):
        # Unsurprisingly, SQLDeveloper fails to include a useful version in
        # the app's Info.plist.  Instead, the actual version is buried deep
        # inside in a file called "version.properties". Thanks, Oracle.
        # You know, I was a having a pretty good day up until now...
        relative_path = (
            "Contents/Resources/sqldeveloper/sqldeveloper/bin/version.properties"
        )
        file_path = os.path.join(self.env["app_path"], relative_path)

        with open(file_path, encoding="utf_8") as fopen:
            cp = configparser.SafeConfigParser()
            try:
                cp.read_file(self.add_section_header(fopen), source=file_path)
            except IOError as err:
                raise ProcessorError(err)
            self.output(cp.sections())
            self.env["version"] = cp["properties"]["ver_full"]
            self.output("Version: %s" % self.env["version"])


if __name__ == "__main__":
    PROCESSOR = SQLDeveloperVersioner()
    PROCESSOR.execute_shell()
