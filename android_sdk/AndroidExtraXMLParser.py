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

"""See docstring for AndroidExtraXMLParser class."""

# Disabling warnings for env members and imports that only affect recipe-
# specific processors.
# pylint: disable=e1101,f0401

from __future__ import absolute_import, print_function

import urllib2
import xml.etree.cElementTree as ET

from autopkglib import Processor, ProcessorError

__all__ = ["AndroidExtraXMLParser"]


def get_element_children_dict(element, schema):
    result_dict = dict()
    tag = ""
    if len(element.getchildren()) >= 1:
        for child in element.getchildren():
            tag = child.tag.replace(schema, "")
            if not child.getchildren():
                result_dict[tag] = child.text
                # the tag name gets the value of the text
            else:
                # if there are children, each child needs to be converted into a dict
                templist = list()
                for newchild in child.getchildren():
                    templist.append(get_element_children_dict(newchild, schema))
                result_dict[tag] = templist
    else:
        # no grandchildren
        result_dict[element.tag.replace(schema, "")] = element.text
    return result_dict


def find_value_in_dict(thedict, key):
    """Iterate through a dict to find all matching keys, even if inside another
    dict."""
    resultlist = list()
    if key not in thedict:
        # it might be buried inside a dict as a value
        for value in thedict.values():
            if type(value) == list:
                templist = list()
                for newvalue in value:
                    result = find_value_in_dict(newvalue, key)
                    if result:
                        templist.append(result)
                if len(templist) == 1:
                    resultlist = templist[0]
                else:
                    resultlist.extend(templist)
    else:
        "Adding to dict 2 %s" % key
        resultlist.append(thedict[key])
    return resultlist


class AndroidExtraXMLParser(Processor):
    # pylint: disable=missing-docstring
    description = "Parse the addons XML file for a variable match."
    input_variables = {
        "xml_file": {"required": True, "description": "Path or URL to XML file."},
        "name": {"required": True, "description": "Item name to match."},
        "tags": {
            "required": True,
            "description": (
                "Dictionary of tags to search for, and variables to "
                "name them - {'vendor-display': 'VendorDisplay'"
            ),
        },
    }
    output_variables = {"found_value": {"description": "Result of found attribute."}}

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
        # Look for everything else
        match = root.findall("%s%s" % (schema, "extra"))
        # Now look through the records
        for record in match:
            result_dict = get_element_children_dict(record, schema)
            # We match records by name-display field
            if record.find("%sname-display" % schema).text != self.env["name"]:
                continue
            for key, outputVar in self.env["tags"].iteritems():
                print("Key: %s" % key)
                if key == "license":
                    # Look for license - it's a special case
                    match = root.findall("%s%s" % (schema, "license"))
                    self.env[self.env["tags"]["license"]] = (
                        match[-1].text.encode("ascii", "ignore").encode("string-escape")
                    )
                    self.output("Found license.")
                    continue
                if key == "uses-license":
                    self.env[self.env["tags"]["uses-license"]] = record.find(
                        "%s%s" % (schema, "uses-license")
                    ).attrib["ref"]
                    self.output(
                        "Found license-ref: %s"
                        % self.env[self.env["tags"]["uses-license"]]
                    )
                    continue
                # Look for revision - third special case
                if key == "revision":
                    major = find_value_in_dict(result_dict, "revision")[0][0].get(
                        "major", ""
                    )
                    minor = find_value_in_dict(result_dict, "revision")[0][1].get(
                        "minor", ""
                    )
                    micro = find_value_in_dict(result_dict, "revision")[0][2]["micro"]
                    self.env[self.env["tags"]["revision"]] = "%s.%s.%s" % (
                        major,
                        minor,
                        micro,
                    )
                    self.output("Revision: %s" % self.env[self.env["tags"]["revision"]])
                    continue
                value = find_value_in_dict(result_dict, key)
                print("Found value: %s" % value)


if __name__ == "__main__":
    PROCESSOR = AndroidExtraXMLParser()
    PROCESSOR.execute_shell()
