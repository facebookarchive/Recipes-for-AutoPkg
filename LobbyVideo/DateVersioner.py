#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

import datetime
import time

from autopkglib import Processor

__all__ = ["DateVersioner"]


class DateVersioner(Processor):
    description = "Places current date and time into %version%."
    input_variables = {
        "notime": {
            "required": False,
            "description": (
                "True/false. If true, ",
                "only the current date is provided. Defaults to false.",
            ),
        }
    }
    output_variables = {"version": {"description": "Current date and time as version."}}

    __doc__ = description

    def main(self):
        try:
            notime = self.env["notime"]
        except KeyError:
            notime = False
            self.output("notime is %s" % notime)
        self.env["version"] = (
            str(datetime.date.today()) + "_" + str(time.strftime("%H-%M-%S"))
        )
        if notime:
            self.env["version"] = str(datetime.date.today())
        self.output("Version is set to %s" % self.env["version"])


if __name__ == "__main__":
    processor = DateVersioner()
    processor.execute_shell()
