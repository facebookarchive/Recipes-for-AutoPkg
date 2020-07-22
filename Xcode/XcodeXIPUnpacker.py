#!/usr/bin/python
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Unpack an Xcode XIP."""

import os
import subprocess

from autopkglib import Processor, ProcessorError


__all__ = ["XcodeXIPUnpacker"]


class XcodeXIPUnpacker(Processor):
    """Unpack a XIP file from Apple."""

    description = "Unpack an Apple XIP file."
    input_variables = {
        "PKG": {"required": True, "description": "Path to an Xcode .xip file."},
        "output_path": {
            "required": False,
            "description": (
                "Path to unpack the contents. Defaults to "
                "%RECIPE_CACHE_DIR%/%NAME%_unpack."
            ),
        },
    }
    output_variables = {}

    __doc__ = description

    def main(self):
        """Main."""
        xip_path = self.env["PKG"]
        if self.env.get("output_path"):
            output = self.env["output_path"]
        else:
            output = os.path.join(
                self.env["RECIPE_CACHE_DIR"], self.env["NAME"] + "_unpack"
            )
        if not os.path.isdir(output):
            os.makedirs(output)

        self.output(
            "Extracting xip archive, please be patient, this could take a long time..."
        )
        os.chdir(output)
        cmd = ["/usr/bin/xip", "--expand", xip_path]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = proc.communicate()
        if err:
            raise ProcessorError(err)
        self.output("Finished xip unpack.")


if __name__ == "__main__":
    processor = XcodeXIPUnpacker()
    processor.execute_shell()
