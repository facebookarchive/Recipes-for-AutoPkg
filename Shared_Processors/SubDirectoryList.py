#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.#
"""See docstring for SubDirectoryList class."""


from __future__ import absolute_import

import os

from autopkglib import Processor, ProcessorError

__all__ = ["SubDirectoryList"]


class SubDirectoryList(Processor):
    """Finds a filename for use in other Processors.

    Currently only supports glob filename patterns.
    """

    input_variables = {
        "root_path": {
            "description": "Path to start looking for files.",
            "required": True,
        },
        "suffix_string": {
            "description": (
                "String to append to each found item name in dir. Defaults to ','"
            ),
            "default": ",",
            "required": False,
        },
    }
    output_variables = {
        "found_filenames": {
            "description": (
                "String containing a list of all files found "
                "relative to root_path, separated by "
                "suffix_string."
            )
        },
        "found_directories": {
            "description": (
                "String containg a list of all directories "
                "found relative to root_path, separated by "
                "suffix_string."
            )
        },
        "relative_root": {"description": ("Relative root path")},
    }

    description = __doc__

    def main(self):
        sip_dirs = ["usr", "usr/local", "private", "private/etc", "Library"]
        format_string = "%s" % self.env["suffix_string"]
        # search_string = '  \'{0}\''
        search_string = "{0}"
        dir_list = list()
        file_list = list()
        if not os.path.isdir(self.env["root_path"]):
            raise ProcessorError("Can't find root path!")
        for dirName, subdirList, fileList in os.walk(self.env["root_path"]):
            relative_path = os.path.relpath(dirName, self.env["root_path"])
            # We need to remove the SIP folders so Chef doesn't try to create them
            if not relative_path == "." and not (relative_path in sip_dirs):
                dir_list.append(relative_path)
            # search_string.format(format_string.join(dirName)).strip()
            for fname in fileList:
                if ".DS_Store" in fname:
                    continue
                # print('\t%s' % fname)
                relpath = os.path.relpath(
                    os.path.join(fname, dirName), self.env["root_path"]
                )
                self.output("Relative path: %s" % relpath)
                if relpath == ".":
                    # we want to avoid prepending './' to files at root dir
                    relpath = ""
                # print "Real relative path: %s" % relpath
                file_list.append(os.path.join(relpath, fname))
        self.env["found_directories"] = search_string.format(
            format_string.join(dir_list)
        ).strip()
        self.env["found_filenames"] = search_string.format(
            format_string.join(file_list)
        ).strip()


if __name__ == "__main__":
    PROCESSOR = SubDirectoryList()
    PROCESSOR.execute_shell()
