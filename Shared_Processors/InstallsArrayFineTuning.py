#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.#
"""See docstring for PackageInfoVersioner class."""


from __future__ import absolute_import

from autopkglib import Processor, ProcessorError

__all__ = ["InstallsArrayFineTuning"]


class InstallsArrayFineTuning(Processor):
    """Change an installs array to allow fine-tuning of a type."""

    description = __doc__
    input_variables = {
        "additional_pkginfo": {
            "required": True,
            "description": ("Dictionary containing an installs array."),
        },
        "changes": {
            "required": True,
            "description": (
                "List of dictionaries containing replacement values "
                "for installs types. Each dictionary must contain a "
                "path and the new type."
            ),
        },
    }

    output_variables = {
        "changed_pkginfo": {"description": "Fine tuned additional_pkginfo dictionary."}
    }

    __doc__ = description

    def main(self):
        """Magic."""
        current = self.env["additional_pkginfo"]["installs"]
        changes = self.env["changes"]
        for change in changes:
            path = change.get("path", None)
            if not path:
                raise ProcessorError("No path found in change!")
            newtype = change.get("type", None)
            if not newtype:
                raise ProcessorError("No type found in change!")
            # Replace the installs
            for install in current:
                if install["path"] == path:
                    install["type"] = newtype
                    self.output("Replacing type for %s to %s" % (path, newtype))
        self.env["changed_pkginfo"] = current


if __name__ == "__main__":
    PROCESSOR = InstallsArrayFineTuning()
    PROCESSOR.execute_shell()
