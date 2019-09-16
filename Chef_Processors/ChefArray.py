#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
"""See docstring for ChefArray class."""

from __future__ import absolute_import

from autopkglib import Processor

__all__ = ["ChefArray"]


class ChefArray(Processor):
    description = (
        "Produces an array that can be used with other "
        " Chef blocks. See "
        "https://docs.chef.io/ruby.html#arrays."
    )
    input_variables = {
        "item_list": {
            "description": (
                "Array of items to be put into the array block. This "
                "can also be a single string."
            ),
            "required": True,
        },
        "no_wrap_quotes": {
            "description": "Do not add wrapping quotation marks.",
            "required": False,
        },
        "remove_version": {
            "description": ("Removes the version string from the variable."),
            "required": False,
        },
    }
    output_variables = {"array_block": {"description": "Chef array block."}}

    __doc__ = description

    def main(self):
        beginning_bracket = "[\n"
        iterator = "item"
        end_bracket = "]"
        each_text = ".each do |%s|\n" % iterator
        quotes = "'"
        itemlist = list()

        # Are we going to use wrapping quotes?
        if self.env.get("no_wrap_quotes"):
            quotes = ""

        # Check to see if one item was passed as a single string
        if isinstance(self.env["item_list"], basestring):
            if self.env["remove_version"]:
                # Remove the ['version'] text from the string
                version_string = "['%s']" % self.env["remove_version"]
                if version_string in self.env["item_list"]:
                    self.env["item_list"] = self.env["item_list"].replace(
                        version_string, ""
                    )
            self.env["array_block"] = self.env["item_list"] + each_text
        else:
            itemlist = self.env["item_list"]
            # Begin the block
            self.env["array_block"] = beginning_bracket
            # Loop through the array of items
            for item in itemlist:
                self.output("Item: %s" % item)
                self.env["array_block"] += "  %s%s%s,\n" % (quotes, str(item), quotes)
            # End the block
            self.env["array_block"] += end_bracket
            # Remove the trailing comma on the last item
            self.env["array_block"] = self.env["array_block"].replace(",\n]", "\n]")
            self.env["array_block"] += each_text
        self.output("Chef block: \n%s" % self.env["array_block"])


if __name__ == "__main__":
    PROCESSOR = ChefArray()
    PROCESSOR.execute_shell()
