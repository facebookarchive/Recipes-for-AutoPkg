#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.#
"""See docstring for ChefAttributeList class."""

from __future__ import absolute_import

import os.path

from autopkglib import Processor

__all__ = ["ChefAttributeList"]


class ChefAttributeList(Processor):
    """Class for Attribute List."""

    description = (
        "Produces a Chef attribute variable for a list of items. "
        "The attribute prefixes correspond to node settings - i.e. "
        "default[category][prefix][attribute]."
    )
    input_variables = {
        "attribute_version": {
            "required": True,
            "description": "Version of Munki this applies to.",
        },
        "attribute": {"required": True, "description": "Name of attribute."},
        "value": {
            "required": True,
            "description": (
                "Single string containing list of items, separated by commas."
            ),
        },
        "path_prefix": {
            "required": False,
            "description": "Path to prepend to each found item.",
            "default": "",
        },
    }
    output_variables = {
        "chef_block": {"description": "Chef attribute block."},
        "attribute_variable": {"description": "Full name of variable."},
    }

    __doc__ = description

    def main(self):
        """Main."""
        att_prefix = "munki['%s']['%s']" % (
            self.env["attribute_version"],
            self.env["attribute"],
        )
        self.env["chef_block"] = att_prefix + " = [\n"
        for value in self.env["value"].split(","):
            # attribute = '%s = [\n'
            # print "Value: %s" % value
            self.env["chef_block"] += "  '%s',\n" % str(
                os.path.join(self.env["path_prefix"], value)
            )
        self.env["chef_block"] += "]\n"
        self.output("Chef block: %s" % self.env["chef_block"])
        self.env["attribute_variable"] = att_prefix.replace("default", "node")


if __name__ == "__main__":
    PROCESSOR = ChefAttributeList()
    PROCESSOR.execute_shell()
