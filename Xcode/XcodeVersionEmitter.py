#!/usr/bin/python
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
"""Get all Version information from Xcode."""

import os.path

try:
    # python 2
    from urlparse import urlsplit
except ImportError:
    from urllib.parse import urlsplit

from autopkglib import Processor


__all__ = ["XcodeVersionEmitter"]


class XcodeVersionEmitter(Processor):
    """Output a version number based on the URL. Skipped by default."""

    description = __doc__
    input_variables = {
        "dont_skip": {
            "required": False,
            "default": False,
            "description": ("If this evaluates as truthy, do not skip this step."),
        },
        "url": {"required": True, "description": ("URL to parse the version from.")},
        "output_filepath": {
            "required": True,
            "description": ("Path to a file to create."),
        },
    }
    output_variables = {
        "derived_filename": {"description": "The derived filename to emit."}
    }

    __doc__ = description

    def main(self):
        """Main."""
        if not self.env["dont_skip"]:
            self.output("dont_skip is false, so skipping this Processor.")
            return
        url = self.env["url"]
        url_split_object = urlsplit(url)
        # "https://download.developer.apple.com/Developer_Tools/Xcode_10.2.1/Xcode_10.2.1.xip"  # noqa
        # "https://developer.apple.com//services-account/download?path=/Developer_Tools/Xcode_11_Beta_2/Xcode_11_Beta_2.xip"  # noqa
        filename = os.path.splitext(os.path.basename(url_split_object.path))[0].lower()
        self.output("Derived filename: {}".format(filename))
        self.env["derived_filename"] = filename
        destination = os.path.expandvars(self.env["output_filepath"])
        with open(destination, "w") as f:
            f.write(filename)
            self.output("Derived filename written to disk at {}".format(destination))


if __name__ == "__main__":
    PROCESSOR = XcodeVersionEmitter()
    PROCESSOR.execute_shell()
