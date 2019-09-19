#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.#
"""See docstring for ChefLaunchd class."""

from __future__ import absolute_import

from autopkglib import Processor

__all__ = ["ChefLaunchd"]


class ChefLaunchd(Processor):
    description = (
        "Produces a cookbook_file Chef block. See "
        "https://docs.chef.io/resource_launchd.html."
    )
    input_variables = {
        "resource_name": {
            "required": True,
            "description": (
                "Name for the resource. This can be a single "
                "string or an array of strings. If an array is "
                "provided, the first item in the array will be the "
                "resource name and the rest will be turned "
                "into an array."
            ),
        },
        "launchd_resource_array": {
            "required": False,
            "description": "Does the resource_name represent an array variable?",
        },
        "launchd_action": {
            "required": True,
            "description": "Resource action. See documentation.",
        },
        "launchd_notifies": {
            "required": False,
            "description": (
                "Which resource takes action when this resource's state changes."
            ),
        },
        "launchd_launchd_name": {
            "required": False,
            "description": ("The name of the launchd."),
        },
        "launchd_subscribes": {
            "required": False,
            "description": (
                "Specify that this resource is to listen "
                "to another resource, and then take action "
                "when that resource's state changes."
            ),
        },
        "launchd_only_if": {"required": False, "description": "only_if guard phrase."},
        "launchd_not_if": {"required": False, "description": "not_if guard phrase."},
        "launchd_extra_indentation": {
            "required": False,
            "description": "Indent this block. Defaults to empty.",
        },
        "launchd_indentation_end": {
            "required": False,
            "description": "Should this end an indented section? Defaults to empty.",
        },
        "launchd_path": {
            "required": False,
            "description": "Explicit path to plist file.",
        },
    }
    output_variables = {"chef_block": {"description": "Chef block."}}

    __doc__ = description

    def main(self):
        # chef block variables
        prefix = "launchd_"
        block_name = "launchd"

        # formatting variables
        extra_formatting = ""
        end_text = "end\n"
        self.env["chef_block"] = ""
        each_do_beginning = "[\n"
        each_do_end = ".each do |item|\n"
        self.env["chef_block"] = each_do_beginning
        name = "item"
        notif_text = "not_if"
        onlyif_text = "only_if"
        indent_block = ""

        # Should this block be indented?
        if self.env.get("%sextra_indentation" % prefix):
            self.output("Adding indentation.")
            indent_block = "  "
            end_text = "  " + end_text
            extra_formatting = "  "
        # Should this end an indented block?
        if self.env.get("%sindentation_end" % prefix):
            end_text = end_text + "end\n"

        # Check to see if only one item was passed
        if len(self.env["resource_name"].split(",")) == 1:
            if self.env.get("%sresource_array" % prefix):
                # it's a node variable representating an array
                self.env["chef_block"] = (
                    indent_block
                    + block_name
                    + " "
                    + self.env["resource_name"]
                    + each_do_end
                )
            else:
                self.env["chef_block"] = (
                    indent_block
                    + block_name
                    + " "
                    + self.env["resource_name"]
                    + " do\n"
                )
        else:
            for resource_name in self.env["resource_name"].split(","):
                self.env["chef_block"] += "  %s,\n" % resource_name
            self.env["chef_block"] += "]" + each_do_end
            # Remove trailing comma
            self.env["chef_block"] = self.env["chef_block"].replace(",\n]", "\n]")
            self.env["chef_block"] += "%s %s do\n" % (block_name, name)
            # Insert an extra tab before everything
            extra_formatting = "  "
            end_text = indent_block + "end\n\n"

        input_list = sorted(self.input_variables.keys())
        # Start the block
        # Remove the indentation keys
        input_list.remove("%sextra_indentation" % prefix)
        input_list.remove("%sindentation_end" % prefix)
        # Place not_if guards first
        if self.env.get("%snot_if" % prefix):
            self.env["chef_block"] += "%s  %s %s\n" % (
                extra_formatting,
                notif_text,
                self.env["%snot_if" % prefix],
            )
            input_list.remove("%snot_if" % prefix)
        # Place only_if guards next
        if self.env.get("%sonly_if" % prefix):
            self.env["chef_block"] += "%s  %s %s\n" % (
                extra_formatting,
                onlyif_text,
                self.env["%sonly_if" % prefix],
            )
            input_list.remove("%sonly_if" % prefix)
        # Remove the special keys
        input_list.remove("%sresource_array" % prefix)
        input_list.remove("resource_name")
        # Loop through all remaining keys
        for key in input_list:
            if self.env.get(key, ""):
                key_text = "%s" % key.replace("%s" % prefix, "")
                self.env["chef_block"] += "%s  %s %s\n" % (
                    extra_formatting,
                    key_text,
                    self.env[key],
                )
            # Clear out the key so it doesn't poison future runs
            self.env[key] = ""
        # end it
        self.env["chef_block"] += end_text + "\n"
        self.output("Chef block:\n%s" % self.env["chef_block"])
        # Clean up the keys that weren't iterated through
        self.env["%sextra_indentation" % prefix] = ""
        self.env["%sindentation_end" % prefix] = ""
        self.env["%snot_if" % prefix] = ""
        self.env["%sonly_if" % prefix] = ""


if __name__ == "__main__":
    PROCESSOR = ChefLaunchd()
    PROCESSOR.execute_shell()
