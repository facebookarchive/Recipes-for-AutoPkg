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
"""See docstring for AppleCookieDownloader class"""

import json
import os.path
import subprocess
import time

from autopkglib import Processor, ProcessorError


__all__ = ["AppleCookieDownloader"]


class AppleCookieDownloader(Processor):
    """Downloads a URL to the specified download_dir using curl."""

    description = __doc__
    input_variables = {
        "login_data": {"required": True, "description": "Path to login data file."},
        "CURL_PATH": {
            "required": False,
            "default": "/usr/bin/curl",
            "description": "Path to curl binary. Defaults to /usr/bin/curl.",
        },
    }
    output_variables = {
        "download_cookies": {"description": "Path to the download cookies."}
    }

    def download(self, url, curl_opts, output, request_headers, allow_failure=False):
        """Run a download with curl."""
        # construct curl command.
        curl_cmd = [
            self.env["CURL_PATH"],
            "--silent",
            "--show-error",
            "--no-buffer",
            "--fail",
            "--dump-header",
            "-",
            "--speed-time",
            "30",
            "--location",
            "--url",
            url,
            "--output",
            output,
        ]

        if request_headers:
            for header, value in request_headers.items():
                curl_cmd.extend(["--header", "%s: %s" % (header, value)])

        if curl_opts:
            for item in curl_opts:
                curl_cmd.extend([item])

        # Open URL.
        proc = subprocess.Popen(
            curl_cmd,
            shell=False,
            bufsize=1,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        donewithheaders = False
        maxheaders = 15
        header = {}
        header["http_result_code"] = "000"
        header["http_result_description"] = ""
        while True:
            if not donewithheaders:
                info = proc.stdout.readline().decode().strip("\r\n")
                if info.startswith("HTTP/"):
                    try:
                        header["http_result_code"] = info.split(None, 2)[1]
                        header["http_result_description"] = info.split(None, 2)[2]
                    except IndexError:
                        pass
                elif ": " in info:
                    # got a header line
                    part = info.split(None, 1)
                    fieldname = part[0].rstrip(":").lower()
                    try:
                        header[fieldname] = part[1]
                    except IndexError:
                        header[fieldname] = ""
                elif info == "":
                    # we got an empty line; end of headers (or curl exited)
                    if header.get("http_result_code") in [
                        "301",
                        "302",
                        "303",
                        "307",
                        "308",
                    ]:
                        # redirect, so more headers are coming.
                        # Throw away the headers we've received so far
                        header = {}
                        header["http_result_code"] = "000"
                        header["http_result_description"] = ""
                    else:
                        donewithheaders = True
            else:
                time.sleep(0.1)

            if proc.poll() is not None:
                # For small download files curl may exit before all headers
                # have been parsed, don't immediately exit.
                maxheaders -= 1
                if donewithheaders or maxheaders <= 0:
                    break

        retcode = proc.poll()
        if (
            retcode and not allow_failure
        ):  # Non-zero exit code from curl => problem with download
            curlerr = ""
            try:
                curlerr = proc.stderr.read().rstrip("\n")
                curlerr = curlerr.split(None, 2)[2]
            except IndexError:
                pass

            raise ProcessorError("Curl failure: %s (exit code %s)" % (curlerr, retcode))

    def main(self):
        download_dir = os.path.join(self.env["RECIPE_CACHE_DIR"], "downloads")
        login_cookies = os.path.join(download_dir, "login_cookies")
        download_cookies = os.path.join(download_dir, "download_cookies")
        # create download_dir if needed
        if not os.path.exists(download_dir):
            try:
                os.makedirs(download_dir)
            except OSError as err:
                raise ProcessorError(
                    "Can't create %s: %s" % (download_dir, err.strerror)
                )

        self.output("Getting login cookie")
        # We need to POST a request to the auth page to get the
        # 'myacinfo' cookie
        login_curl_opts = [
            "--request",
            "POST",
            "--data",
            "@{}".format(self.env["login_data"]),
            "--cookie-jar",
            login_cookies,
        ]
        self.download(
            url="https://idmsa.apple.com/IDMSWebAuth/authenticate",
            curl_opts=login_curl_opts,
            output="-",
            request_headers=None,
            allow_failure=True,
        )
        self.output("Getting download cookie")
        # Now we need to get the download cookie
        dl_curl_opts = [
            "--request",
            "POST",
            "--cookie",
            login_cookies,
            "--cookie-jar",
            download_cookies,
        ]
        headers = {"Content-length": "0"}
        output = os.path.join(download_dir, "listDownloads.gz")
        if os.path.exists(output):
            # Delete it first
            os.unlink(output)
        self.download(
            url="https://developer.apple.com/services-account/QH65B2/downloadws/listDownloads.action",
            curl_opts=dl_curl_opts,
            output=output,
            request_headers=headers,
            allow_failure=True,
        )
        self.env["download_cookies"] = download_cookies
        try:
            with open(output) as f:
                json.load(f)
                # If we successfully load this as JSON, then we failed
                # to download the gzip list
                raise ProcessorError(
                    "Unable to list downloads. Check your Apple credentials."
                )
        except IOError:
            raise ProcessorError("Unable to load listDownloads.gz file.")
        except ValueError:
            pass
        # While we're at it, let's unzip the download list
        # It's actually a gunzip, so Unarchiver doesn't work
        # The result is a JSON blob
        self.output("Unzipping download list")
        os.chdir(download_dir)
        if os.path.exists(output.rstrip(".gz")):
            # Delete the file if it's already here
            os.unlink(output.rstrip(".gz"))
        gunzip_cmd = ["/usr/bin/gunzip", output]
        proc = subprocess.Popen(
            gunzip_cmd,
            shell=False,
            bufsize=1,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        (stdout, stderr) = proc.communicate()
        if proc.returncode:
            gzerr = stderr.rstrip("\n")
            raise ProcessorError(
                "Gunzip failure: %s (exit code %s)" % (gzerr, proc.returncode)
            )


if __name__ == "__main__":
    PROCESSOR = AppleCookieDownloader()
    PROCESSOR.execute_shell()
