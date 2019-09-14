#!/usr/bin/python
"""Return version for Android NDK."""
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
# Disabling warnings for env members and imports that only affect recipe-
# specific processors.
# pylint: disable=e1101,f0401

from __future__ import absolute_import

import os
import shlex

from autopkglib import Processor, ProcessorError

__all__ = ["AndroidNDKVersioner"]


class AndroidNDKVersioner(Processor):
  """Return version for Android NDK."""

  description = ("Detect version of downloaded Android NDK based on "
                 "source.properties.")
  input_variables = {
    "properties_path": {
      "required": True,
      "description": "File to parse for version info."
    },
  }
  output_variables = {
    "release_num": {
      "description": "Release of download."
    },
    "version": {
      "description": "Version of download."
    }
  }

  def main(self):
    """Main."""
    path = self.env.get('properties_path')
    if not os.path.isfile(path):
      raise ProcessorError("%s doesn't exist!" % path)
    with open(path, 'rb') as f:
      data = f.read()
    split_data = shlex.split(data)
    # Version is defined in the files
    version = split_data[split_data.index('Pkg.Revision') + 2]
    self.env['version'] = version.split()[-1]
    # Release is just based on filename
    self.env['release_num'] = os.path.basename(
      os.path.dirname(path)
    ).split('-')[-1]

if __name__ == "__main__":
  PROCESSOR = AndroidNDKVersioner()
  PROCESSOR.execute_shell()
