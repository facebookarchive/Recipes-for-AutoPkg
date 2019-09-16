#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.#
"""See docstring for ChefTemplate class."""

from __future__ import absolute_import

from autopkglib import Processor

__all__ = ["ChefTemplate"]


class ChefTemplate(Processor):
    description = (
        "Produces a template Chef block. See "
        "https://docs.chef.io/resource_template.html."
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
        "action": {
            "required": False,
            "description": "Resource action. See documentation.",
        },
        "atomic_update": {
            "required": False,
            "description": "Perform atomic file updates on a per-resource basis.",
        },
        "backup": {
            "required": False,
            "description": "The number of backups to be kept in /var/chef/backup.",
        },
        "cookbook": {
            "required": False,
            "description": "The cookbook in which a file is located.",
        },
        "force_unlink": {
            "required": False,
            "description": (
                "How the chef-client handles certain situations when "
                "the target file turns out not to be a file."
            ),
        },
        "group": {
            "required": False,
            "description": "Use to configure permissions for directories.",
        },
        "helper": {"required": False, "description": "Define a helper method inline."},
        "ignore_failure": {
            "required": False,
            "description": (
                "Continue running a recipe if a resource fails for any reason."
            ),
        },
        "inherits": {
            "required": False,
            "description": (
                "Windows only. Whether a file inherits rights from "
                "its parent template."
            ),
        },
        "local": {
            "required": False,
            "description": "Load a template from a local path.",
        },
        "manage_symlink_source": {
            "required": False,
            "description": (
                "Cause the chef-client to detect and manage the "
                "source file for a symlink."
            ),
        },
        "mode": {
            "required": False,
            "description": (
                "A quoted 3-5 character string that defines the octal mode."
            ),
        },
        "notifies": {
            "required": False,
            "description": (
                "Which resource takes action when this resource's state changes."
            ),
        },
        "owner": {
            "required": False,
            "description": "Use to configure permissions for directories.",
        },
        "path": {"required": False, "description": "The path to the template."},
        "provider": {
            "required": False,
            "description": "Optional. Explicitly specify a provider.",
        },
        "retries": {
            "required": False,
            "description": (
                "The number of times to catch exceptions and retry the resource."
            ),
        },
        "retry_delay": {
            "required": False,
            "description": "The retry delay (in seconds).",
        },
        "rights": {
            "required": False,
            "description": (
                "Microsoft Windows only. The permissions for users and "
                "groups in a Microsoft Windows environment."
            ),
        },
        "sensitive": {
            "required": False,
            "description": (
                "Ensure that sensitive resource data is not logged "
                "by the chef-client."
            ),
        },
        "source": {
            "required": True,
            "description": (
                "The name of the file in COOKBOOK_NAME/files/default "
                "or the path to a file located in COOKBOOK_NAME/files."
            ),
        },
        "subscribes": {
            "required": False,
            "description": (
                "Specify that this resource is to listen to another "
                "resource, and then take action when that resource's "
                "state changes.."
            ),
        },
        "variables": {
            "required": True,
            "description": (
                "A Hash of variables that are passed into a Ruby template file."
            ),
        },
        "verify": {
            "required": False,
            "description": (
                "A block or a string that returns true or false. A "
                "string, when true is executed as a system command."
            ),
        },
        "only_if": {"required": False, "description": "only_if guard phrase."},
        "not_if": {"required": False, "description": "not_if guard phrase."},
    }
    output_variables = {"chef_block": {"description": "Chef block."}}

    __doc__ = description

    def main(self):
        extra_formatting = ""
        block_name = "template"
        end_text = "end\n"
        self.env["chef_block"] = ""
        if not isinstance(self.env["resource_name"], basestring):
            # Not a string, assume it's an array of strings
            each_do_beginning = "[\n"
            each_do_end = "].each do |item|\n\t"
            self.env["chef_block"] = each_do_beginning
            for resource_name in self.env["resource_name"]:
                self.env["chef_block"] += "\t%s,\n" % resource_name
            self.env["chef_block"] += each_do_end
            name = "item"
            # insert an extra tab before everything
            extra_formatting = "\t"
            end_text = "\tend\nend\n"
        else:
            name = self.env["resource_name"]
        notif_text = "\tnot_if"
        onlyif_text = "\tonly_if"

        input_list = sorted(self.input_variables.keys())
        # Start the block
        self.env["chef_block"] += "%s %s do\n" % (block_name, name)
        # Place not_if guards first
        if self.env.get("not_if"):
            self.env["chef_block"] += "%s\t%s %s\n" % (
                extra_formatting,
                notif_text,
                self.env["not_if"],
            )
            input_list.remove("not_if")
        # Place only_if guards next
        if self.env.get("only_if"):
            self.env["chef_block"] += "%s\t%s %s\n" % (
                extra_formatting,
                onlyif_text,
                self.env["only_if"],
            )
            input_list.remove("only_if")
        input_list.remove("resource_name")
        # Loop through all keys
        for key in input_list:
            if self.env.get(key, ""):
                key_text = "\t%s" % key
                self.env["chef_block"] += "%s\t%s %s\n" % (
                    extra_formatting,
                    key_text,
                    self.env[key],
                )
            # clear out the key so it doesn't poison future runs
            self.env[key] = ""
        # end it
        self.env["chef_block"] += end_text
        self.output("Chef block:\n%s" % self.env["chef_block"])


if __name__ == "__main__":
    PROCESSOR = ChefTemplate()
    PROCESSOR.execute_shell()
