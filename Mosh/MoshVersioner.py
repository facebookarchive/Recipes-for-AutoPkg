#!/usr/bin/python
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
"""See docstring for MoshVersioner class"""

# Disabling warnings for env members and imports that only affect recipe-
# specific processors.
# pylint: disable=e1101,f0401

# The majority of this code is taken from MunkiCommon:
# https://github.com/munki/munki/blob/master/code/client/munkilib/munkicommon.py

from autopkglib import Processor, ProcessorError
import tempfile
import subprocess
import os
from xml.dom import minidom

__all__ = ["MoshVersioner"]


class MoshVersioner(Processor):
  # pylint: disable=missing-docstring
  description = ("Get version from Mosh download.")
  input_variables = {
      "pathname": {
          "required": True,
          "description": ("Path to downloaded package.")
      }
  }
  output_variables = {
      "version": {
          "description": ("Version info parsed, naively derived from the "
                          "package's name.")
      }
  }

  __doc__ = description

  def main(self):
    filepath = self.env["pathname"]
    pkgtmp = tempfile.mkdtemp()
    os.chdir(pkgtmp)
    cmd_extract = ['/usr/bin/xar', '-xf', filepath, 'Distribution']
    result = subprocess.call(cmd_extract)
    if result == 0:
      dom = minidom.parse(os.path.join(pkgtmp, 'Distribution'))
      pkgrefs = dom.getElementsByTagName('pkg-ref')
      unfixed = pkgrefs[1].attributes['version'].value.encode('UTF-8')
      # At this point, unfixed_version is typically "mosh-1.x.x"
      self.env["version"] = unfixed.lstrip('mosh-')
      self.output("Found version: %s" % self.env["version"])
    else:
      raise ProcessorError("An error occurred while extracting "
                           "Distribution file")


if __name__ == "__main__":
  PROCESSOR = MoshVersioner()
  PROCESSOR.execute_shell()
