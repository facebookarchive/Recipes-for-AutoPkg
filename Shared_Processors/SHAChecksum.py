#!/usr/bin/python
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.#
"""See docstring for SHAChecksum class"""

# Disabling warnings for env members and imports that only affect recipe-
# specific processors.
# pylint: disable=e1101,f0401

from __future__ import absolute_import

import subprocess

from autopkglib import Processor, ProcessorError

__all__ = ["SHAChecksum"]


class SHAChecksum(Processor):
    """Calculate checksum for a file"""

    description = __doc__
    input_variables = {
        "source_file": {
            "required": True,
            "description": ("Path to file to calculate checksum on."),
        },
        "checksum_type": {
            "required": False,
            "description": (
                "Checksum type, will be passed directly to ",
                "shasum -a. See manpage for available options. " "Defaults to SHA1.",
            ),
        },
    }
    output_variables = {
        "checksum": {"description": "SHA checksum calculated from path."}
    }

    __doc__ = description

    def main(self):
        sha_args = self.env.get("checksum_type", None)
        cmd = ["/usr/bin/shasum"]
        if sha_args:
            cmd.append("-a")
            cmd.append(sha_args)
        cmd.append(self.env["source_file"])
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (shaout, shaerr) = proc.communicate()
        if shaerr:
            raise ProcessorError(shaerr)
        self.output(shaout)
        self.env["checksum"] = shaout.split()[0]


if __name__ == "__main__":
    PROCESSOR = SHAChecksum()
    PROCESSOR.execute_shell()
