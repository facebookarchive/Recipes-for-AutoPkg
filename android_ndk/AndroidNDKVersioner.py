#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Return version for Android NDK."""
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

from __future__ import absolute_import

import os
import shlex

from autopkglib import Processor, ProcessorError

__all__ = ["AndroidNDKVersioner"]


class AndroidNDKVersioner(Processor):
    """Return version for Android NDK."""

    description = (
        "Detect version of downloaded Android NDK based on source.properties."
    )
    input_variables = {
        "properties_path": {
            "required": True,
            "description": "File to parse for version info.",
        }
    }
    output_variables = {
        "release_num": {"description": "Release of download."},
        "version": {"description": "Version of download."},
    }

    def main(self):
        """Main."""
        path = self.env.get("properties_path")
        if not os.path.isfile(path):
            raise ProcessorError("%s doesn't exist!" % path)
        with open(path, "rb") as f:
            data = f.read()
        split_data = shlex.split(data)
        # Version is defined in the files
        version = split_data[split_data.index("Pkg.Revision") + 2]
        self.env["version"] = version.split()[-1]
        # Release is just based on filename
        self.env["release_num"] = os.path.basename(os.path.dirname(path)).split("-")[-1]


if __name__ == "__main__":
    PROCESSOR = AndroidNDKVersioner()
    PROCESSOR.execute_shell()
