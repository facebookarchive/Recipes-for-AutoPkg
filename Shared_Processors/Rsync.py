#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  Copyright (c) 2015, Facebook, Inc.
#  All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree. An additional grant
#  of patent rights can be found in the PATENTS file in the same directory.
"""See docstring for Rsync class."""

from __future__ import absolute_import

import subprocess

from autopkglib import Processor, ProcessorError

__all__ = ["Rsync"]


class Rsync(Processor):
    """Rsyncs a path to another path."""

    description = __doc__
    input_variables = {
        "source_path": {
            "required": True,
            "description": ("Path to file or directory to copy from."),
        },
        "destination_path": {
            "required": True,
            "description": ("Path to file or directory to copy to."),
        },
        "rsync_arguments": {
            "required": False,
            "description": ("List of arguments passed to rsync directly."),
        },
        "rsync_path": {
            "required": False,
            "description": ("Custom path to rsync. Defaults to /usr/bin/rsync."),
        },
    }
    output_variables = {}

    __doc__ = description

    def main(self):
        rsync_location = self.env.get("rsync_path", "/usr/bin/rsync")
        rsync_args = self.env.get("rsync_arguments", [])
        if isinstance(rsync_args, basestring):
            raise ProcessorError("rsync_args must be a list!")
        cmd = [rsync_location]
        if rsync_args:
            cmd.extend(rsync_args)
        cmd.extend([self.env["source_path"], self.env["destination_path"]])
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (rout, rerr) = proc.communicate()
        if rerr:
            raise ProcessorError(rerr)
        self.output(rout)


if __name__ == "__main__":
    PROCESSOR = Rsync()
    PROCESSOR.execute_shell()
