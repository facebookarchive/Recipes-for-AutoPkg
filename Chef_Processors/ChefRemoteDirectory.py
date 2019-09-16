#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.#
"""See docstring for ChefRemoteDirectory class."""

from __future__ import absolute_import

from autopkglib import Processor

__all__ = ["ChefRemoteDirectory"]


class ChefRemoteDirectory(Processor):
    description = (
        "Produces a remote_directory Chef block. See "
        "https://docs.chef.io/resource_remote_directory.html."
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
        "cookbook": {
            "required": False,
            "description": "The cookbook in which a file is located.",
        },
        "files_backup": {
            "required": False,
            "description": (
                "The number of backup copies to keep for files in the directory."
            ),
        },
        "files_group": {
            "required": False,
            "description": (
                "Configure group permissions for files. A string or ID "
                "that identifies the group owner by group name."
            ),
        },
        "files_mode": {"required": False, "description": "The octal mode for a file."},
        "files_owner": {
            "required": False,
            "description": (
                "Configure owner permissions for files. A string or ID "
                "that identifies the group owner by group name."
            ),
        },
        "group": {
            "required": False,
            "description": "Use to configure permissions for directories.",
        },
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
                "its parent directory."
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
        "overwrite": {
            "required": False,
            "description": "Overwrite a file when it is different.",
        },
        "owner": {
            "required": False,
            "description": "Use to configure permissions for directories.",
        },
        "path": {"required": False, "description": "The path to the directory."},
        "provider": {
            "required": False,
            "description": "Optional. Explicitly specify a provider.",
        },
        "purge": {
            "required": False,
            "description": "Purge extra files found in the target directory.",
        },
        "recursive": {
            "required": False,
            "description": "Create or delete directories recursively.",
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
        "source": {
            "required": True,
            "description": "The base name of the source file.",
        },
        "subscribes": {
            "required": False,
            "description": (
                "Specify that this resource is to listen to another "
                "resource, and then take action when that resource's "
                "state changes.."
            ),
        },
        "only_if": {"required": False, "description": "only_if guard phrase."},
        "not_if": {"required": False, "description": "not_if guard phrase."},
    }
    output_variables = {"chef_block": {"description": "Chef block."}}

    __doc__ = description

    def main(self):
        extra_formatting = ""
        block_name = "remote_directory"
        self.env["remote_directory"] = ""
        if not isinstance(self.env["chef_block"], basestring):
            # Not a string, assume it's an array of strings
            each_do_beginning = "[\n"
            each_do_end = "].each do |item|\n\t"
            self.env["remote_directory"] = each_do_beginning
            for resource_name in self.env["chef_block"]:
                self.env["remote_directory"] += "\t%s,\n" % resource_name
            self.env["remote_directory"] += each_do_end
            name = "item"
            # insert an extra tab before everything
            extra_formatting = "\t"
            end_text = "\tend\nend\n\n"
        else:
            name = self.env["chef_block"]
        notif_text = "\tnot_if"
        onlyif_text = "\tonly_if"

        input_list = sorted(self.input_variables.keys())
        # Start the block
        self.env["remote_directory"] += "%s %s do\n" % (block_name, name)
        # Place not_if guards first
        if self.env.get("not_if"):
            self.env["remote_directory"] += "%s\t%s %s\n" % (
                extra_formatting,
                notif_text,
                self.env["not_if"],
            )
            input_list.remove("not_if")
        # Place only_if guards next
        if self.env.get("only_if"):
            self.env["remote_directory"] += "%s\t%s %s\n" % (
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
                self.env["remote_directory"] += "%s\t%s %s\n" % (
                    extra_formatting,
                    key_text,
                    self.env[key],
                )
            # clear out the key so it doesn't poison future runs
            self.env[key] = ""
        # end it
        self.env["remote_directory"] += end_text
        self.output("Chef block:\n%s" % self.env["remote_directory"])


if __name__ == "__main__":
    PROCESSOR = ChefRemoteDirectory()
    PROCESSOR.execute_shell()
