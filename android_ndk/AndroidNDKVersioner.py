#!/usr/bin/python
#
# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
"""See docstring for AndroidNDKVersioner class"""

# Disabling warnings for env members and imports that only affect recipe-
# specific processors.
# pylint: disable=e1101,f0401

import subprocess
import os

from autopkglib import Processor, ProcessorError

__all__ = ["AndroidNDKVersioner"]


class AndroidNDKVersioner(Processor):
  # pylint: disable=missing-docstring
  description = ("Detect version of downloaded Android NDK based on URL.")
  input_variables = {
      "match": {
          "required": True,
          "description": "URL to parse for version info."
      },
      "localonly": {
          "required": False,
          "description": ("Use only",
                          " local file for version checking. Assumes",
                          " local file is %pathname%. Defaults to 0.")
      }
  }
  output_variables = {
      "version": {
          "description": "Version of download."
      }
  }

  __doc__ = description

  def main(self):
    uselocal = False
    if self.env.get("localonly"):
        uselocal = True
    if uselocal:
      # We use the local file only
      # Execute the file with argument "l" to get a list of the file
      os.chdir(os.path.dirname(self.env["pathname"]))
      cmd = ['./' + os.path.basename(self.env["pathname"]), 'l']
      proc = subprocess.Popen(cmd,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
      (out, err) = proc.communicate()
      if err:
        raise ProcessorError(err)
      # The top folder is the last line of output before the "footer",
      # and the footer is 3 lines long.
      # By parsing the 4th to last line and splitting on whitespace,
      # we can simply get the top folder name.
      self.env["version"] = \
          out.split('\n')[-4].split()[-1].split('-')[-1]
    else:
      # Assuming the URL is always of this structure:
      # .../android/ndk/android-ndk-r10e-darwin-x86_64.bin
      # Filename is always android-ndk-VERSION-darwin-x86_64.bin
      self.env["version"] = \
          self.env["match"].split('/')[-1].split('-')[2]

if __name__ == "__main__":
  PROCESSOR = AndroidNDKVersioner()
  PROCESSOR.execute_shell()
