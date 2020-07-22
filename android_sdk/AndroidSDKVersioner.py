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

"""See docstring for AndroidSDKVersioner class."""

# Disabling warnings for env members and imports that only affect recipe-
# specific processors.
# pylint: disable=e1101,f0401

from __future__ import absolute_import

import urllib2
import xml.etree.cElementTree as ET

from autopkglib import Processor, ProcessorError

__all__ = ["AndroidSDKVersioner"]


class AndroidSDKVersioner(Processor):
    # pylint: disable=missing-docstring
    description = "Parse the XML file for the latest version of the SDK tools."
    input_variables = {
        "xml_file": {"required": True, "description": "Path or URL to XML file."}
    }
    output_variables = {
        "version": {"description": "Combined version of the SDK tools."}
    }

    __doc__ = description

    def main(self):
        if "http" in self.env["xml_file"]:
            try:
                tree = ET.ElementTree(file=urllib2.urlopen(self.env["xml_file"]))
            except urllib2.URLError as err:
                raise ProcessorError(err)
        else:
            try:
                tree = ET.ElementTree(file=self.env["xml_file"])
            except IOError as err:
                raise ProcessorError(err)
        root = tree.getroot()
        schema = root.tag.split("}")[0] + "}"
        match = root.findall("%s%s" % (schema, "tool"))
        revision = "%srevision" % schema
        result = ""
        try:
            major = match[-1].find(revision).find("%smajor" % schema).text
            minor = match[-1].find(revision).find("%sminor" % schema).text
            micro = match[-1].find(revision).find("%smicro" % schema).text
        except IndexError:
            raise ProcessorError("Version not found!")
        result = "%s.%s.%s" % (major, minor, micro)
        self.env["version"] = result
        self.output("Version: %s" % self.env["version"])


if __name__ == "__main__":
    PROCESSOR = AndroidSDKVersioner()
    PROCESSOR.execute_shell()
