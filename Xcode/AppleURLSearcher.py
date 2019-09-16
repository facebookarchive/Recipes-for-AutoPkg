#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.#
"""See docstring for AppleURLSearcher class."""

from __future__ import absolute_import

import json
import os.path
import posixpath
import re
import urlparse
from distutils import version
from types import StringType

from autopkglib import Processor, ProcessorError

__all__ = ["AppleURLSearcher"]


class MunkiLooseVersion(version.LooseVersion):
    """Subclass version.LooseVersion to compare things like "10.6" and "10.6.0"
    as equal."""

    def __init__(self, vstring=None):
        if vstring is None:
            # treat None like an empty string
            self.parse("")
        if vstring is not None:
            if isinstance(vstring, unicode):
                # unicode string! Why? Oh well...
                # convert to string so version.LooseVersion doesn't choke
                vstring = vstring.encode("UTF-8")
            self.parse(str(vstring))

    def _pad(self, version_list, max_length):
        """Pad a version list by adding extra 0 components to the end if
        needed."""
        # copy the version_list so we don't modify it
        cmp_list = list(version_list)
        while len(cmp_list) < max_length:
            cmp_list.append(0)
        return cmp_list

    def __cmp__(self, other):
        if isinstance(other, StringType):
            other = MunkiLooseVersion(other)
        max_length = max(len(self.version), len(other.version))
        self_cmp_version = self._pad(self.version, max_length)
        other_cmp_version = self._pad(other.version, max_length)
        return cmp(self_cmp_version, other_cmp_version)


class AppleURLSearcher(Processor):
    """Downloads a URL to the specified download_dir using curl."""

    description = __doc__
    input_variables = {
        "result_output_var_name": {
            "description": (
                "The name of the output variable that is returned "
                "by the match. If not specified then a default of "
                '"match" will be used.'
            ),
            "required": False,
            "default": "match",
        },
        "re_pattern": {
            "required": True,
            "description": "Path to download data file from AppleCookieDownloader.",
        },
        "re_flags": {
            "description": (
                "Optional array of strings of Python regular "
                "expression flags. E.g. IGNORECASE."
            ),
            "required": False,
        },
    }
    output_variables = {
        "result_output_var_name": {
            "description": (
                "First matched sub-pattern from input found on the fetched "
                "URL. Note the actual name of variable depends on the input "
                'variable "result_output_var_name" or is assigned a default of '
                '"match."'
            )
        }
    }

    def main(self):
        download_dir = os.path.join(self.env["RECIPE_CACHE_DIR"], "downloads")
        downloads = os.path.join(download_dir, "listDownloads")

        if not os.path.exists(downloads):
            raise ProcessorError("Missing the download data from AppleCookieDownloader")

        flags = self.env.get("re_flags", {})

        with open(downloads) as f:
            data = json.load(f)
        dl_base_url = "https://download.developer.apple.com"
        dl_urls = []
        for x in data["downloads"]:
            for y in x["files"]:
                dl_urls.append(dl_base_url + y["remotePath"])

        flag_accumulator = 0
        if flags:
            for flag in flags:
                if flag in re.__dict__:
                    flag_accumulator += re.__dict__[flag]

        re_pattern = re.compile(self.env["re_pattern"], flags=flag_accumulator)

        match = re_pattern.findall("\n".join(sorted(dl_urls)))
        if not match:
            raise ProcessorError("No match found!")

        # Now we have a list of matching URLs, find the highest version
        filenames = [
            os.path.splitext(posixpath.basename(urlparse.urlsplit(x).path))[0]
            for x in match
        ]
        filenames.sort(key=MunkiLooseVersion)
        self.output("Found matching item: %s" % filenames[-1])
        full_url_match = [x for x in match if filenames[-1] in x]

        if not full_url_match:
            raise ProcessorError("No matching URL found!")

        # The final entry is the highest one
        self.output("Full URL: %s" % full_url_match[0])
        self.env[self.env["result_output_var_name"]] = full_url_match[0]
        self.output_variables = {}
        self.output_variables[self.env["result_output_var_name"]] = full_url_match[0]


if __name__ == "__main__":
    PROCESSOR = AppleURLSearcher()
    PROCESSOR.execute_shell()
