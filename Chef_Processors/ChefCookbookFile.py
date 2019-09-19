#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
"""See docstring for ChefCookbookFile class."""

from __future__ import absolute_import

from autopkglib import Processor

__all__ = ["ChefCookbookFile"]


class ChefCookbookFile(Processor):
    description = (
        "Produces a cookbook_file Chef block. See "
        "https://docs.chef.io/resource_cookbook_file.html."
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
        "cookbook_file_resource_array": {
            "required": False,
            "description": "Does the resource_name represent an array variable?",
        },
        "cookbook_file_action": {
            "required": False,
            "description": "Resource action. See documentation.",
        },
        "cookbook_file_atomic_update": {
            "required": False,
            "description": "Perform atomic file updates on a per-resource basis.",
        },
        "cookbook_file_backup": {
            "required": False,
            "description": "The number of backups to be kept in /var/chef/backup.",
        },
        "cookbook_file_cookbook": {
            "required": False,
            "description": "The cookbook in which a file is located.",
        },
        "cookbook_file_force_unlink": {
            "required": False,
            "description": (
                "How the chef-client handles certain situations when "
                "the target file turns out not to be a file."
            ),
        },
        "cookbook_file_group": {
            "required": False,
            "description": "Use to configure permissions for directories.",
        },
        "cookbook_file_ignore_failure": {
            "required": False,
            "description": (
                "Continue running a recipe if a resource fails for any reason."
            ),
        },
        "cookbook_file_inherits": {
            "required": False,
            "description": (
                "Windows only. Whether a file inherits rights from "
                "its parent cookbook_file."
            ),
        },
        "cookbook_file_manage_symlink_source": {
            "required": False,
            "description": (
                "Cause the chef-client to detect and manage the "
                "source file for a symlink."
            ),
        },
        "cookbook_file_mode": {
            "required": False,
            "description": (
                "A quoted 3-5 character string that defines the octal mode."
            ),
        },
        "cookbook_file_notifies": {
            "required": False,
            "description": (
                "Which resource takes action when this resource's state changes."
            ),
        },
        "cookbook_file_owner": {
            "required": False,
            "description": "Use to configure permissions for directories.",
        },
        "cookbook_file_path": {
            "required": False,
            "description": "The path to the cookbook_file.",
        },
        "cookbook_file_provider": {
            "required": False,
            "description": "Optional. Explicitly specify a provider.",
        },
        "cookbook_file_retries": {
            "required": False,
            "description": (
                "The number of times to catch exceptions and retry the resource."
            ),
        },
        "cookbook_file_retry_delay": {
            "required": False,
            "description": "The retry delay (in seconds).",
        },
        "cookbook_file_rights": {
            "required": False,
            "description": (
                "Microsoft Windows only. The permissions for users and "
                "groups in a Microsoft Windows environment."
            ),
        },
        "cookbook_file_source": {
            "required": True,
            "description": (
                "The name of the file in COOKBOOK_NAME/files/default "
                "or the path to a file located in COOKBOOK_NAME/files."
            ),
        },
        "cookbook_file_subscribes": {
            "required": False,
            "description": (
                "Specify that this resource is to listen to another "
                "resource, and then take action when that resource's "
                "state changes.."
            ),
        },
        "cookbook_file_verify": {
            "required": False,
            "description": (
                "A block or a string that returns true or false. A "
                "string, when true is executed as a system command."
            ),
        },
        "cookbook_file_only_if": {
            "required": False,
            "description": "only_if guard phrase.",
        },
        "cookbook_file_not_if": {
            "required": False,
            "description": "not_if guard phrase.",
        },
        "cookbook_file_extra_indentation": {
            "required": False,
            "description": "Indent this block. Defaults to empty.",
        },
        "cookbook_file_indentation_end": {
            "required": False,
            "description": "Should this end an indented section? Defaults to empty.",
        },
    }
    output_variables = {"chef_block": {"description": "Chef block."}}

    __doc__ = description

    def main(self):
        # chef block variables
        prefix = "cookbook_file_"
        block_name = "cookbook_file"

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
    PROCESSOR = ChefCookbookFile()
    PROCESSOR.execute_shell()
