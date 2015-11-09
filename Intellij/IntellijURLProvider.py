#!/usr/bin/env python
#
# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#

import re
import urllib2

from autopkglib import Processor, ProcessorError


__all__ = ["IntellijURLProvider"]

intellij_version_url = 'http://www.jetbrains.com/js2/version.js'
re_intellij_version = re.compile(
    r'var versionIDEALong = "(?P<version>[0-9.]+)";', re.I)


class IntellijURLProvider(Processor):
  description = "Provides URL to the latest release of Intellij."
  input_variables = {
      "base_url": {
          "required": False,
          "description": "Default is 'http://www.jetbrains.com/js2/version.js'"
      },
  }
  output_variables = {
      "url": {
          "description": "URL to the latest release of Intellij",
      },
  }

  __doc__ = description

  def get_intellij_version(self, intellij_version_url):
      # Read HTML index.
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
      match = re_intellij_version.search(html)
      if not match:
          raise ProcessorError(
              "Couldn't find download URL in %s" % intellij_version_url
          )

      # Return pkg url.
      return match.group("version")

  def main(self):
    # Determine values.
    version_url = self.env.get('version_url', intellij_version_url)
    version = self.get_intellij_version(version_url)
    download_url = "http://download-cf.jetbrains.com/" \
        "idea/ideaIC-%s-custom-jdk-bundled.dmg" % version

    self.env["url"] = download_url
    self.output("URL: %s" % self.env["url"])

if __name__ == '__main__':
    processor = IntellijURLProvider()
    processor.execute_shell()
