#!/usr/bin/python
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
"""See docstring for AppleURLSearcher class"""

import json
import os.path
import posixpath
import re
import subprocess
import urlparse
from distutils import version
from types import StringType

from autopkglib import Processor, ProcessorError


__all__ = ["AppleURLSearcher"]


class MunkiLooseVersion(version.LooseVersion):
    """Subclass version.LooseVersion to compare things like
    "10.6" and "10.6.0" as equal"""

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
        """Pad a version list by adding extra 0
        components to the end if needed"""
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
    """Search the various Apple URLs for a matching Xcode."""

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
            "description": (
                "Path to download data file from AppleCookieDownloader."
                "Ignored if BETA is set in the environment."
            ),
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

    # This code is taken directly from URLTextSearcher
    def get_url_and_search(self, url, re_pattern, headers=None, flags=None, opts=None):
        """Get data from url and search for re_pattern"""
        flag_accumulator = 0
        if flags:
            for flag in flags:
                if flag in re.__dict__:
                    flag_accumulator += re.__dict__[flag]

        re_pattern = re.compile(re_pattern, flags=flag_accumulator)

        try:
            cmd = [self.env["CURL_PATH"], "--location", "--compressed"]
            if headers:
                for header, value in headers.items():
                    cmd.extend(["--header", "%s: %s" % (header, value)])
            if opts:
                for item in opts:
                    cmd.extend([item])
            cmd.append(url)
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (content, stderr) = proc.communicate()
            if proc.returncode:
                raise ProcessorError("Could not retrieve URL %s: %s" % (url, stderr))
        except OSError:
            raise ProcessorError("Could not retrieve URL: %s" % url)

        # Output this to disk so I can search it later
        with open(
            os.path.join(self.env["RECIPE_CACHE_DIR"], "downloads", "url_text.txt"), "w"
        ) as f:
            f.write(content)
        match = re_pattern.search(content)

        if not match:
            raise ProcessorError("No match found on URL: %s" % url)

        # return the last matched group with the dict of named groups
        return (match.group(match.lastindex or 0), match.groupdict())

    def main(self):
        if self.env.get("BETA"):
            self.output("Beta flag is set, searching Apple downloads URL...")
            beta_url = "https://developer.apple.com/download/"
            # We're going to make the strong assumption that if BETA is
            # populated, we should only use URLTextSearcher, because as of
            # 6/7/19, Apple has only posted the new Xcode beta to the main
            # developer page, and not the "More Downloads" section.
            # If this trend holds true, then URLTextSearcher = betas,
            # AppleURLSearcher = "more downloads" = stable/GM releases.
            # If we do get a url from URLTextSearcher, it needs to be appended
            # to the base Apple Developer Portal URL.
            curl_opts = [
                "--cookie",
                "login_cookies",
                "--cookie-jar",
                "download_cookies",
            ]
            pattern = r"""<a href=["'](.*.xip)"""
            groupmatch, groupdict = self.get_url_and_search(
                beta_url, pattern, opts=curl_opts
            )
            fixed_url = "https://developer.apple.com/" + groupmatch
            self.env[self.env["result_output_var_name"]] = fixed_url
            self.output("New fixed URL: {}".format(fixed_url))
            self.output_variables = {}
            self.output_variables[self.env["result_output_var_name"]] = fixed_url
            return
        self.output("Beta flag not set, searching More downloads list...")
        # If we're not looking for BETA, then disregard everything from
        # URLTextSearcher and search the Apple downloads list instead.
        download_dir = os.path.join(self.env["RECIPE_CACHE_DIR"], "downloads")
        downloads = os.path.join(download_dir, "listDownloads")

        if not os.path.exists(downloads):
            raise ProcessorError("Missing the download data from AppleCookieDownloader")

        with open(downloads) as f:
            data = json.load(f)
        dl_base_url = "https://download.developer.apple.com"
        dl_urls = []
        for x in data["downloads"]:
            for y in x["files"]:
                url = dl_base_url + y["remotePath"]
                # Regex the results
                re_pattern = re.compile(self.env["re_pattern"])
                dl_match = re_pattern.findall(url)
                if not dl_match:
                    continue
                dl_urls.append(url)

        match = re_pattern.findall("\n".join(sorted(dl_urls)))

        if not match or not dl_urls:
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
