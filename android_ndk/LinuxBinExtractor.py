#!/usr/bin/python
#
# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
"""See docstring for LinuxBinExtractor class"""

# Disabling warnings for env members and imports that only affect recipe-
# specific processors.
# pylint: disable=e1101,f0401

import subprocess
import os
import stat

from autopkglib import Processor, ProcessorError

__all__ = ["LinuxBinExtractor"]


class LinuxBinExtractor(Processor):
  # pylint: disable=missing-docstring
  description = ("Invoke a Linux self-extracting .bin file.")
  input_variables = {
      "pathname": {
          "required": True,
          "description": ("Path to binary file.")
      },
      "output_dir": {
          "required": False,
          "description": "Desired output directory."
      }
  }
  output_variables = {
  }

  __doc__ = description

  def main(self):
    try:
      os.chmod(self.env["pathname"],
               os.stat(self.env["pathname"]).st_mode |
               stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    except OSError as err:
      raise ProcessorError(err)
    os.chdir(os.path.dirname(self.env["pathname"]))
    output_path = ""
    if self.env.get("output_dir"):
      output_path = self.env["output_dir"]
    cmd = ['./' + os.path.basename(self.env["pathname"]), '-o' +
           output_path]
    self.output("Cmd: %s" % cmd)
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    (out, err) = proc.communicate()
    if err:
      raise ProcessorError(err)

if __name__ == "__main__":
  PROCESSOR = LinuxBinExtractor()
  PROCESSOR.execute_shell()
