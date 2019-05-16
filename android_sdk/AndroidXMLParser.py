#!/usr/bin/python
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.#
"""See docstring for AndroidXMLParser class"""

# Disabling warnings for env members and imports that only affect recipe-
# specific processors.
# pylint: disable=e1101,f0401

import xml.etree.cElementTree as ET
import urllib2

from autopkglib import Processor, ProcessorError

__all__ = ["AndroidXMLParser"]


class AndroidXMLParser(Processor):
  # pylint: disable=missing-docstring
  description = ("Parse the provided XML file for a variable match.")
  input_variables = {
    "xml_file": {
      "required": True,
      "description": "Path or URL to XML file."
    },
    "namespace": {
      "required": True,
      "description": "Namespace to search for to find a tag inside."
    },
    "tags": {
      "required": True,
      "description": ("Dictionary of tags to search for, and variables to "
                      "name them - {'vendor-display': 'VendorDisplay'")
    }
  }
  output_variables = {
    "xml_output_variables": {
      "description": ("Output variables per 'tags' supplied as input. Note "
                      "that this output variable is used as both a "
                      "placeholder for documentation and for auditing "
                      "purposes. One should use the actual named output "
                      "variables as given as values to 'plist_keys' to refer"
                      "to the output of this processor.")
    }
  }

  __doc__ = description

  def main(self):
    if 'http' in self.env['xml_file']:
      try:
        tree = ET.ElementTree(file=urllib2.urlopen(self.env['xml_file']))
      except urllib2.URLError as err:
        raise ProcessorError(err)
    else:
      try:
        tree = ET.ElementTree(file=self.env['xml_file'])
      except IOError as err:
        raise ProcessorError(err)
    root = tree.getroot()
    schema = root.tag.split('}')[0] + '}'
    match = root.findall('%s%s' % (schema, self.env['namespace']))
    for key, outputVar in self.env['tags'].iteritems():
      for item in match[-1]:
        if item.tag.replace(schema, '') == key:
          self.env[outputVar] = item.text
          self.output("Found %s as %s" % (key, self.env[outputVar]))
          break
      if key == 'uses-license' and ('license' in self.env['tags'].keys()):
        # Special case since the license isn't a traditional key
        license_ref = item.attrib['ref']
        self.output("Found license ref: %s" % license_ref)
        self.env[outputVar] = license_ref
        self.env[self.env['tags']['license']] = \
          root[0].text.encode('ascii', 'ignore').encode('string-escape')
      if key == 'url':
        # It's easy to find the URL here, the structure is always the same
        archives = '%sarchives' % schema
        archive = '%sarchive' % schema
        url = '%surl' % schema
        # Look for a host os
        host_os = '%shost-os' % schema
        archive_list = match[-1].find(archives).findall(archive)
        for arch in archive_list:
          if arch.find(host_os) is not None:
            # If there's a "host-os" in the archive
            if 'macosx' in arch.find(host_os).text:
              # Look for a Mac version
              self.env[outputVar] = \
                arch.find(url).text.encode('ascii', 'ignore')
              # self.output("Found %s as %s" % (key, self.env[outputVar]))
              break
        else:
          # No host os was provided, so assume they're not platform specific
          # So we return the first item
          self.env[outputVar] = \
            match[-1].find(archives).find(archive).find(url).text
          self.output("Found: %s" % self.env[outputVar])

if __name__ == "__main__":
  PROCESSOR = AndroidXMLParser()
  PROCESSOR.execute_shell()
