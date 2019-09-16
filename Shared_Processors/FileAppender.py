#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.#
"""Processor that creates a file."""

from __future__ import absolute_import

from autopkglib import Processor, ProcessorError

__all__ = ["FileAppender"]


class FileAppender(Processor):
    """Append contents to the end of a file."""

    description = __doc__
    input_variables = {
        "file_path": {"required": True, "description": "Path to a file to append to."},
        "file_content": {"required": True, "description": "Contents to add to a file."},
    }
    output_variables = {}

    def main(self):
        try:
            with open(self.env["file_path"], "a") as fileref:
                fileref.write(self.env["file_content"])
            self.output("Appened to file at %s" % self.env["file_path"])
        except BaseException as err:
            raise ProcessorError(
                "Can't append to file at %s: %s" % (self.env["file_path"], err)
            )
        # clean the variable up afterwards to not poison future runs
        self.env["file_content"] = ""
        self.env["file_path"] = ""


if __name__ == "__main__":
    PROCESSOR = FileAppender()
    PROCESSOR.execute_shell()
