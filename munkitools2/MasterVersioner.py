#!/usr/bin/python
#
#  Copyright (c) 2015, Facebook, Inc.
#  All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree. An additional grant
#  of patent rights can be found in the PATENTS file in the same directory.
"""See docstring for MasterVersioner class"""

# Disabling warnings for env members and imports that only affect recipe-
# specific processors.
# pylint: disable=e1101,f0401

from xml.dom import minidom

from autopkglib import Processor, ProcessorError

__all__ = ["MasterVersioner"]


class MasterVersioner(Processor):
  """Get version from a PackageInfo file in a distribution/bundle package"""
  description = __doc__
  input_variables = {
    "package_info_path": {
      "required": True,
      "description": ("Path to PackageInfo file inside a distribution",
                      "/bundle package.")
    }
  }
  output_variables = {
    "master_version": {
      "description": "Version returned from pkg-info field in PacakgeInfo."
    }
  }

  __doc__ = description

  def main(self):
    try:
      dom = minidom.parse(self.env["package_info_path"])
    except IOError as err:
      raise ProcessorError(err)
    pkgrefs = dom.getElementsByTagName('pkg-info')
    self.env["master_version"] = \
      pkgrefs[0].attributes['version'].value.encode('UTF-8')
    self.output("Found version %s" % self.env["master_version"])

if __name__ == "__main__":
  PROCESSOR = MasterVersioner()
  PROCESSOR.execute_shell()
