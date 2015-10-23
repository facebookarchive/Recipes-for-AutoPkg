#!/usr/bin/python
#
#  Copyright (c) 2015, Facebook, Inc.
#  All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree. An additional grant
#  of patent rights can be found in the PATENTS file in the same directory.
"""See docstring for Rsync class"""

# Disabling warnings for env members and imports that only affect recipe-
# specific processors.
# pylint: disable=e1101,f0401

import subprocess

from autopkglib import Processor, ProcessorError

__all__ = ["Rsync"]


class Rsync(Processor):
  """Rsyncs a file/directory to another file/directory"""
  description = __doc__
  input_variables = {
    "source_path": {
      "required": True,
      "description": ("Path to file or directory to copy from.")
    },
    "destination_path": {
      "required": True,
      "description": ("Path to file or directory to copy to.")
    },
    "rsync_arguments": {
      "required": False,
      "description": ("Arguments passed to rsync directly.")
    },
    "rsync_path": {
      "required": False,
      "description": ("Custom path to rsync. Defaults to /usr/bin/rsync.")
    }
  }
  output_variables = {
  }

  __doc__ = description

  def main(self):
    rsync_location = self.env.get("rsync_path", "/usr/bin/rsync")
    rsync_args = self.env.get("rsync_arguments", "")
    cmd = [rsync_location, rsync_args, self.env["source_path"],
           self.env["destination_path"]]
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    (rout, rerr) = proc.communicate()
    if rerr:
        raise ProcessorError(rerr)
    self.output(rout)

if __name__ == "__main__":
  PROCESSOR = Rsync()
  PROCESSOR.execute_shell()
