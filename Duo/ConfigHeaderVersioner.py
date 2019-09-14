#!/usr/bin/python
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.#
"""See docstring for ConfigHeaderVersioner class."""

# Disabling warnings for env members and imports that only affect recipe-
# specific processors.
# pylint: disable=e1101,f0401

from __future__ import absolute_import, print_function

from autopkglib import Processor, ProcessorError

__all__ = ["ConfigHeaderVersioner"]


class ConfigHeaderVersioner(Processor):
    # pylint: disable=missing-docstring
    description = "Looks for a version key in a config.h header file."
    input_variables = {
        "header_file": {
            "required": True,
            "description": "Path to the config.h file in a Makefile directory.",
        },
        "version_key": {
            "required": False,
            "description": (
                "Key to look for for versioning. Defaults to PACKAGE_VERSION."
            ),
            "default": "PACKAGE_VERSION",
        },
    }
    output_variables = {"version": {"description": "Value of version key."}}

    __doc__ = description

    def main(self):
        print("Version key: %s" % self.env["version_key"])
        try:
            with open(self.env["header_file"], "rb") as f:
                for line in f:
                    if self.env["version_key"] in line:
                        version_line = line
                        break
                # If we get here, we didn't find the version key
                else:
                    raise ProcessorError("Version key not found in file!")
        except IOError as err:
            raise ProcessorError(err)
        self.output("Version line found: %s" % version_line)
        # The line is typically: #define PACKAGE_VERSION <version>
        self.env["version"] = version_line.split(" ")[2].rstrip().strip('"')
        self.output("Version found: %s" % self.env["version"])


if __name__ == "__main__":
    PROCESSOR = ConfigHeaderVersioner()
    PROCESSOR.execute_shell()
