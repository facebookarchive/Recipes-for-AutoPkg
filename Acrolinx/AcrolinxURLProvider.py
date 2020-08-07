#!/usr/bin/env python3
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
"""See docstring for AcrolinxURLProvider class"""

from __future__ import absolute_import, division, print_function, unicode_literals

from autopkglib import ProcessorError
from autopkglib.URLGetter import URLGetter


__all__ = ["AcrolinxURLProvider"]

URL = "https://{}:{}@download.acrolinx.com:1443/api/deliverablePackages/575b1d0d401ae30b00e90f40/download/latest?preserve_credentials=true&proxy=true"


class AcrolinxURLProvider(URLGetter):
    """Provides a download URL for Acrolinx."""

    description = __doc__
    input_variables = {
        "username": {"required": True, "description": "Username for authentication."},
        "password": {"required": True, "description": "Password for authentication"},
    }
    output_variables = {"url": {"description": "Download URL for Acrolinx."}}

    def main(self):
        """Find the download URL"""
        username = self.env["username"]
        password = self.env["password"]
        url = URL.format(username, password)
        # Fetch the API data
        curl_cmd = self.prepare_curl_cmd()
        curl_cmd.extend(["--head", url])
        raw_headers = self.download_with_curl(curl_cmd)
        header = self.parse_headers(raw_headers)
        # Use semantic versioning for the version string, although historically this
        # hasn't been anything particularly problematic
        acrolinx_url = header.get("http_redirected")
        if not acrolinx_url:
            self.output(f"Header: {header}")
            raise ProcessorError(
                "Header did not contain an 'http_redirected' "
                "value containing the expected Acrolinx URL. Check your "
                "username and password."
            )
        self.output(f"Found URL: {acrolinx_url}")
        self.env["url"] = acrolinx_url


if __name__ == "__main__":
    PROCESSOR = AcrolinxURLProvider()
    PROCESSOR.execute_shell()
