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

    def main(self):
        # Unsurprisingly, SQLDeveloper fails to include a useful version in
        # the app's Info.plist.  Instead, the actual version is buried deep
        # inside in a file called "version.properties". Thanks, Oracle.
        # You know, I was a having a pretty good day up until now...

        # this code stolen from Oscar de Groot's answer at:
        # https://stackoverflow.com/questions/2819696/parsing-properties-file-in-python
        def add_section_header(properties_file, header_name):
            yield '[{}]\n'.format(header_name)
            for line in properties_file:
                yield line

        relative_path = (
            "Contents/Resources/sqldeveloper/sqldeveloper/bin/version.properties"
        )
        file_path = os.path.join(self.env["app_path"], relative_path)
        # this code stolen from Oscar de Groot's answer at:
        # https://stackoverflow.com/questions/2819696/parsing-properties-file-in-python

        file = open(file_path, encoding="utf_8")
        cp = configparser.ConfigParser()
        try:
            cp.read_file(add_section_header(file, 'properties'), source=file_path)
        except IOError as err:
            raise ProcessorError(err)
        self.env["version"] = cp.get("properties", "ver_full")
        self.output("Version: %s" % self.env["version"])


if __name__ == "__main__":
    PROCESSOR = SQLDeveloperVersioner()
    PROCESSOR.execute_shell()
