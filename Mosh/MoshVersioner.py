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

"""See docstring for MoshVersioner class"""

# The majority of this code is taken from MunkiCommon:
# https://github.com/munki/munki/blob/master/code/client/munkilib/munkicommon.py

import os
import subprocess
import tempfile
from xml.dom import minidom

from autopkglib import Processor, ProcessorError


__all__ = ["MoshVersioner"]


class MoshVersioner(Processor):
    description = "Get version from Mosh download."
    input_variables = {
        "pathname": {"required": True, "description": ("Path to downloaded package.")}
    }
    output_variables = {
        "version": {
            "description": (
                "Version info parsed, naively derived from the " "package's name."
            )
        }
    }

    __doc__ = description

    def main(self):
        filepath = self.env["pathname"]
        pkgtmp = tempfile.mkdtemp()
        os.chdir(pkgtmp)
        cmd_extract = ["/usr/bin/xar", "-xf", filepath, "Distribution"]
        result = subprocess.call(cmd_extract)
        if result == 0:
            dom = minidom.parse(os.path.join(pkgtmp, "Distribution"))
            pkgrefs = dom.getElementsByTagName("pkg-ref")
            unfixed = pkgrefs[1].attributes["version"].value.encode("UTF-8")
            # At this point, unfixed_version is typically "mosh-1.x.x"
            self.env["version"] = unfixed.lstrip(b"mosh-").decode()
            self.output("Found version: %s" % self.env["version"])
        else:
            raise ProcessorError(
                "An error occurred while extracting Distribution file"
            )


if __name__ == "__main__":
    PROCESSOR = MoshVersioner()
    PROCESSOR.execute_shell()
