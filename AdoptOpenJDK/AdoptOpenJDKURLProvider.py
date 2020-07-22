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
"""See docstring for AdoptOpenJDKURLProvider class"""

from __future__ import absolute_import, division, print_function, unicode_literals

import json

from autopkglib import ProcessorError
from autopkglib.URLGetter import URLGetter


try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin


__all__ = ["AdoptOpenJDKURLProvider"]

URL = "https://api.adoptopenjdk.net/v2/info/releases/"


class AdoptOpenJDKURLProvider(URLGetter):
    """Provides a version and dmg download for the AdoptOpenJDK."""

    description = __doc__
    input_variables = {
        "jdk_version": {"required": True, "description": "Version of JDK to fetch."},
        "jdk_type": {
            "required": False,
            "description": "Fetch 'jdk', or 'jre'. Defaults to 'jdk'.",
        },
        "jvm_type": {
            "required": False,
            "description": (
                "Fetch a 'hotspot' or 'openj9' JVM target. Defaults to 'hotspot'."
            ),
        },
        "binary_type": {
            "required": False,
            "description": "Fetch a 'pkg' or 'tgz' download. Defaults to 'pkg'.",
        },
        "release": {
            "required": False,
            "description": "Fetch a specific release. Defaults to 'latest'.",
        },
    }
    output_variables = {
        "version": {"description": "Version of the product."},
        "url": {"description": "Download URL."},
        "checksum": {"description": "Checksum of the targeted product."},
    }

    def get_checksum(self, checksum_url, binary_type):
        """Get the expected checksum for the release."""
        checksum_data = self.download(checksum_url, text=True)
        return checksum_data.split()[0]

    def main(self):
        """Find the download URL"""
        jvm_type = self.env.get("jvm_type", "hotspot")
        if jvm_type not in ["hotspot", "openj9"]:
            raise ProcessorError("jvm_type can only be 'hotspot' or 'openj9'")
        jdk_type = self.env.get("jdk_type", "jdk")
        if jdk_type not in ["jdk", "jre"]:
            raise ProcessorError("jdk_type can only be 'jdk' or 'jre'")
        binary_type = self.env.get("binary_type", "pkg")
        if binary_type not in ["pkg", "tgz"]:
            raise ProcessorError("jdk_type can only be 'pkg' or 'tgz'")
        release = self.env.get("release", "latest")
        queries = "?os=mac&openjdk_impl={}&type={}&release={}".format(
            jvm_type, jdk_type, release
        )
        # Fetch the API data
        query_suffix = urljoin("openjdk{}".format(self.env["jdk_version"]), queries)
        api_url = urljoin(URL, query_suffix)
        self.output("Query URL: {}".format(api_url))
        api_data = self.download(api_url, text=True)
        api_results = json.loads(api_data)
        # Determine what we're looking for - pkg or tgz
        if binary_type == "pkg":
            checksum_url = api_results["binaries"][0]["installer_checksum_link"]
            url = api_results["binaries"][0]["installer_link"]
        else:
            checksum_url = api_results["binaries"][0]["checksum_link"]
            url = api_results["binaries"][0]["binary_link"]
        # Use semantic versioning for the version string, although historically this
        # hasn't been anything particularly problematic
        version = api_results["binaries"][0]["version_data"]["semver"]
        self.env["version"] = version
        self.output("Version: {}".format(version))
        # Get the checksum from the internet
        checksum = self.get_checksum(checksum_url, binary_type)
        self.env["checksum"] = checksum
        self.output("checksum: {}".format(checksum))
        # Pick the URL
        self.env["url"] = url
        self.output("Found URL {}".format(self.env["url"]))


if __name__ == "__main__":
    PROCESSOR = AdoptOpenJDKURLProvider()
    PROCESSOR.execute_shell()
