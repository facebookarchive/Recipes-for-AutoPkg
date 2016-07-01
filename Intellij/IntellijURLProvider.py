#!/usr/bin/env python
"""Intellij URL Provider."""
# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#

import urllib2
import xml.etree.cElementTree as ET

from autopkglib import Processor, ProcessorError


__all__ = ["IntellijURLProvider"]

intellij_version_url = 'https://www.jetbrains.com/updates/updates.xml'


class IntellijURLProvider(Processor):
  """Provide URL for latest Intellij IDEA build."""

  description = "Provides URL and version for the latest release of Intellij."
  input_variables = {
    "base_url": {
      "required": False,
      "description": ('Default is '
                      'https://www.jetbrains.com/updates/updates.xml'),
    },
    "edition": {
      "required": False,
      "description": ('Either "C" for "Community" or "U" for "Ultimate" '
                      'edition. Defaults to "C".')
    }
  }
  output_variables = {
    "url": {
      "description": "URL to the latest release of Intellij",
    }
  }

  __doc__ = description

  def get_intellij_version(self, intellij_version_url):
    """Retrieve version number from XML."""
    # Read XML
    try:
        req = urllib2.Request(intellij_version_url)
        f = urllib2.urlopen(req)
        html = f.read()
        f.close()
    except BaseException as e:
        raise ProcessorError(
          "Can't download %s: %s" % (
            intellij_version_url, e)
        )
    # Search for download link.
    root = ET.fromstring(html)
    # root[0][-1] is always the last IDEA release
    build = root[0][-1].find('build')
    version = build.attrib['version']
    # Return pkg url.
    return str(version)

  def main(self):
    """Main function."""
    # Determine values.
    version_url = self.env.get('version_url', intellij_version_url)
    version = self.get_intellij_version(version_url)
    download_url = (
      "https://download.jetbrains.com/idea/"
      "ideaI%s-%s.dmg" % (self.env.get('edition', 'C'), version)
    )

    self.env["url"] = download_url
    self.output("URL: %s" % self.env["url"])

if __name__ == '__main__':
    processor = IntellijURLProvider()
    processor.execute_shell()
