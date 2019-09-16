#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
"""See docstring for ChefAttributeHash class."""

from __future__ import absolute_import

from autopkglib import Processor

__all__ = ["ChefAttributeHash"]


class ChefAttributeHash(Processor):
    description = (
        "Produces a Chef attribute variable for a hash of items. "
        "The attribute prefixes correspond to node settings - i.e. "
        "default[category][prefix][attribute]."
    )
    input_variables = {
        "attribute_category": {
            "required": True,
            "description": "Leading category for each attribute.",
        },
        "attribute_prefix": {
            "required": True,
            "description": "Prefix to each attribute.",
        },
        "attribute": {"required": True, "description": "Name of attribute."},
        "value": {"required": True, "description": ("Dictionary of keys and values.")},
        "in_array": {
            "required": False,
            "description": (
                "Is this hash inside an array? If yes, a comma is added to the end"
            ),
        },
    }
    output_variables = {
        "chef_block": {"description": "Chef attribute block."},
        "attribute_variable": {"description": "Full name of variable."},
    }

    __doc__ = description

    def main(self):
        att_prefix = "default['%s']['%s']['%s']" % (
            self.env["attribute_category"],
            self.env["attribute_prefix"],
            self.env["attribute"],
        )
        self.env["chef_block"] = att_prefix + " = {\n"
        for value in sorted(self.env["value"].keys()):
            self.env["chef_block"] += "\t%s => %s,\n" % (
                value,
                self.env["value"][value],
            )
        self.env["chef_block"] += "}"
        # Remove the trailing comma on the last item
        self.env["chef_block"] = self.env["chef_block"].replace(",\n}", "\n}")
        if self.env.get("in_array"):
            # if this hash is in a list of hashes, add a comma at the end
            self.env["chef_block"] += ","
        self.env["chef_block"] += "\n"
        self.output("Chef block: %s" % self.env["chef_block"])
        self.env["attribute_variable"] = att_prefix.replace("default", "node")


if __name__ == "__main__":
    PROCESSOR = ChefAttributeHash()
    PROCESSOR.execute_shell()
