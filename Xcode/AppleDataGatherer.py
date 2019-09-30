#!/usr/bin/python
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
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
            "required": False,
            "description": ("Password for AppleID that can log into Apple dev portal."),
        },
        "password_file": {
            "required": False,
            "description": (
                "A path to a file to read the password from. Using this will "
                "ignore the 'password' argument."
            ),
        },
        "appID_key": {"required": True, "description": ("App ID key to log into.")},
    }
    output_variables = {"data_pathname": {"description": "Path to the data file."}}

    __doc__ = description

    def main(self):
        """Store the login data file."""
        appleIDstring = "appleId={}&".format(quote(self.env["apple_id"]))
        appIDKeystring = "appIdKey={}&".format(self.env["appID_key"])
        if not self.env.get("password") and not self.env.get("password_file"):
            raise ProcessorError(
                "You must provide either a password, or a password_file argument."
            )
        password = self.env.get("password")
        if self.env.get("password_file"):
            with open(self.env["password_file"]) as f:
                password = f.read()
        passwordstring = "accountPassword={}".format(password)

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
