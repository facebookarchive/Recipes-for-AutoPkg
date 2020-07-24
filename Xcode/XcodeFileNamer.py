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
"""Create a filename for Xcode based on version information."""

from autopkglib import Processor


__all__ = ["XcodeFileNamer"]


class XcodeFileNamer(Processor):
    """Create a filename for Xcode based on version information."""

    description = __doc__
    input_variables = {
        "should_produce_versioned_name": {
            "description": (
                "Whether or not we should produce a versioned name. "
                "If this is non-empty, it's evaluated as true."
            ),
            "required": True,
        },
        "major_version": {
            "description": "Major version of Xcode - i.e. Xcode 7, 8.",
            "required": True,
        },
        "minor_version": {
            "description": "Minor version of Xcode - i.e. Xcode X.1, X.2.",
            "required": True,
        },
        "patch_version": {
            "description": (
                "Patch version of Xcode - i.e. Xcode X.Y.0, X.Y.1. "
                "Patch version will be normalized to 0 if missing (i.e. 8.3 "
                "becomes 8.3.0)."
            ),
            "required": True,
        },
        "is_beta": {
            "description": ("Boolean that is true if this Xcode is a beta version."),
            "required": True,
        },
        "beta_version": {
            "description": (
                "The beta number - 1, 2, 3, etc. Only used if is_beta is True. "
                "Assumed to be 0 if not provided."
            ),
            "required": False,
        },
        "should_lowercase": {
            "description": (
                "If this value is non-empty, use a lower-case filename - xcode_X.Y.0_suffix.app."
            ),
            "required": False,
        },
        "suffix": {
            "description": (
                "Any additional suffix string to append to the name prior to the .app extension."
            ),
            "required": False,
        },
    }
    output_variables = {
        "xcode_filename": {"description": "Allow producing a versioned Xcode name."}
    }

    __doc__ = description

    def main(self):
        """Main."""
        if not self.env["should_produce_versioned_name"] and self.env["is_beta"]:
            # Default name for Xcode Beta
            self.env["xcode_filename"] = "Xcode-beta"
            return
        elif not self.env["should_produce_versioned_name"]:
            # Default name for Xcode
            self.env["xcode_filename"] = "Xcode"
            return
        # end up with xcode_10.2.0_beta_4 or xcode_10.2.1
        prefix = "Xcode"
        if self.env.get("should_lowercase"):
            prefix = "xcode"
        name = "{}_{}.{}.{}".format(
            prefix,
            self.env["major_version"],
            self.env["minor_version"],
            self.env["patch_version"],
        )
        if self.env["is_beta"]:
            name = name + "_beta_{}".format(self.env.get("beta_version", "0"))
        name += self.env.get("suffix", "")
        self.output("Xcode name: {}".format(name))
        self.env["xcode_filename"] = name


if __name__ == "__main__":
    PROCESSOR = XcodeFileNamer()
    PROCESSOR.execute_shell()
