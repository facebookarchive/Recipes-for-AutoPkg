#!/usr/bin/python
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.#
"""See docstring for AppleDataGatherer class"""


# Disabling warnings for env members and imports that only affect recipe-
# specific processors.
# pylint: disable=e1101,f0401

import os
from urllib import quote

from autopkglib import Processor, ProcessorError


__all__ = ["AppleDataGatherer"]


class AppleDataGatherer(Processor):
    """Gather Xcode-specific curl data payloads into a file on disk."""

    description = __doc__
    input_variables = {
        "apple_id": {
            "required": True,
            "description": ("AppleID that can log into the Apple dev portal."),
        },
        "password": {
            "required": True,
            "description": ("Password for AppleID that can log into Apple dev portal."),
        },
        "appID_key": {"required": True, "description": ("App ID key to log into.")},
    }
    output_variables = {"data_pathname": {"description": "Path to the data file."}}

    __doc__ = description

    def main(self):
        """Store the login data file."""
        appleIDstring = "appleId={}&".format(quote(self.env["apple_id"]))
        appIDKeystring = "appIdKey={}&".format(self.env["appID_key"])
        passwordstring = "accountPassword={}".format(self.env["password"])

        login_data = appleIDstring + appIDKeystring + passwordstring
        download_dir = os.path.join(self.env["RECIPE_CACHE_DIR"], "downloads")
        filename = "login_data"
        # create download_dir if needed
        if not os.path.exists(download_dir):
            try:
                os.makedirs(download_dir)
            except OSError as err:
                raise ProcessorError(
                    "Can't create %s: %s" % (download_dir, err.strerror)
                )
        self.output("Writing data to file")
        self.env["data_pathname"] = os.path.join(download_dir, filename)
        with open(self.env["data_pathname"], "w") as f:
            f.write(login_data)


if __name__ == "__main__":
    PROCESSOR = AppleDataGatherer()
    PROCESSOR.execute_shell()
