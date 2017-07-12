#!/usr/bin/python
"""Get all Version information from Xcode."""
#
#  Copyright (c) 2015, Facebook, Inc.
#  All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree. An additional grant
#  of patent rights can be found in the PATENTS file in the same directory.

# Disabling warnings for env members and imports that only affect recipe-
# specific processors.
# pylint: disable=e1101,f0401

from autopkglib import Processor, ProcessorError

__all__ = ["XcodeVersioner"]


class XcodeVersioner(Processor):
  """Break down a version number into its separate components."""

  description = __doc__
  input_variables = {
    "version": {
      "required": True,
      "description": (
        "CFBundleShortVersionString from an Xcode Info.plist. Produced by "
        "PlistReader."),
    },
  }
  output_variables = {
    "major_version": {
      "description": "Major version of Xcode - i.e. Xcode 7, 8."
    },
    "minor_version": {
      "description": "Minor version of Xcode - i.e. Xcode X.1, X.2."
    },
    "patch_version": {
      "description": (
        "Patch version of Xcode - i.e. Xcode X.Y.0, X.Y.1. "
        "Patch version will be normalized to 0 if missing (i.e. 8.3 "
        "becomes 8.3.0).")
    },
  }

  __doc__ = description

  def main(self):
    """Main."""
    main_version_string = self.env['version']
    split_string = main_version_string.split('.')
    if len(split_string) < 2:
      raise ProcessorError(
        'Version string should be in format X.Y, unless Apple broke '
        'literally everything again.')
    self.env['major_version'] = str(split_string[0])
    self.output('Major version: %s' % self.env['major_version'])
    self.env['minor_version'] = str(split_string[1])
    self.output('Minor version: %s' % self.env['minor_version'])
    try:
      self.env['patch_version'] = split_string[2]
    except IndexError:
      self.output('Normalizing patch to 0')
      self.env['patch_version'] = str('0')
    self.output('Patch version: %s' % self.env['patch_version'])


if __name__ == "__main__":
  PROCESSOR = XcodeVersioner()
  PROCESSOR.execute_shell()
