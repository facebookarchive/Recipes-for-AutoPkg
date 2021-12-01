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
"""Get all Version information from Xcode."""


from collections import namedtuple

from autopkglib import Processor, ProcessorError


try:
    import objc
except ImportError:
    pass

__all__ = ["XcodeVersioner"]


class XcodeVersioner(Processor):
    """Break down a version number into its separate components."""

    description = __doc__
    input_variables = {
        "version": {
            "required": True,
            "description": (
                "CFBundleShortVersionString from an Xcode Info.plist. Produced by "
                "PlistReader."
            ),
        },
        "app_path": {
            "required": True,
            "description": (
                "Path to Xcode app to look up version information from the bundle."
            ),
        },
    }
    output_variables = {
        "major_version": {"description": "Major version of Xcode - i.e. Xcode 7, 8."},
        "minor_version": {
            "description": "Minor version of Xcode - i.e. Xcode X.1, X.2."
        },
        "patch_version": {
            "description": (
                "Patch version of Xcode - i.e. Xcode X.Y.0, X.Y.1. "
                "Patch version will be normalized to 0 if missing (i.e. 8.3 "
                "becomes 8.3.0)."
            )
        },
        "is_beta": {
            "description": ("Boolean that is true if this Xcode is a beta version.")
        },
        "beta_version": {"description": ("The beta number - 1, 2, 3, etc.")},
        "build_version": {"description": ("Build version of Xcode - e.g. 11B500")},
    }

    __doc__ = description

    def main(self):
        """Main."""
        main_version_string = self.env["version"]
        split_string = main_version_string.split(".")
        if len(split_string) < 2:
            raise ProcessorError(
                "Version string should be in format X.Y, unless Apple broke "
                "literally everything again."
            )
        self.env["major_version"] = str(split_string[0])
        self.output("Major version: %s" % self.env["major_version"])
        self.env["minor_version"] = str(split_string[1])
        self.output("Minor version: %s" % self.env["minor_version"])
        try:
            self.env["patch_version"] = split_string[2]
        except IndexError:
            self.output("Normalizing patch to 0")
            self.env["patch_version"] = str("0")
        self.output("Patch version: %s" % self.env["patch_version"])
        self.output("Build version: %s" % self.env["build_version"])
        if "beta_version" not in self.env:
            self.env["is_beta"] = False
            self.output("Not a beta version")
        else:
            self.output("Beta version: %s" % self.env["beta_version"])

if __name__ == "__main__":
    PROCESSOR = XcodeVersioner()
    PROCESSOR.execute_shell()
