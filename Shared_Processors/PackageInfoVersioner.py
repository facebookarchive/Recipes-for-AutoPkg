#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.#
"""See docstring for PackageInfoVersioner class."""

# Disabling warnings for env members and imports that only affect recipe-
# specific processors.
# pylint: disable=e1101,f0401

from __future__ import absolute_import

from xml.dom import minidom

from autopkglib import Processor, ProcessorError

__all__ = ["PackageInfoVersioner"]


class PackageInfoVersioner(Processor):
    """Get version from a PackageInfo file in a distribution/bundle package."""

    description = __doc__
    input_variables = {
        "package_info_path": {
            "required": True,
            "description": (
                "Path to PackageInfo file inside a distribution",
                "/bundle package.",
            ),
        }
    }
    output_variables = {
        "pkg_id": {
            "description": "Package identifier returned from pkg-info field in PackageInfo."
        },
        "version": {
            "description": "Version returned from pkg-info field in PackageInfo."
        }
    }

    __doc__ = description

    def main(self):
        try:
            dom = minidom.parse(self.env["package_info_path"])
        except IOError as err:
            raise ProcessorError(err)
        pkgrefs = dom.getElementsByTagName("pkg-info")
        self.env["pkg_id"] = pkgrefs[0].attributes["identifier"].value
        self.output("Found pkg_id %s" % self.env["pkg_id"]) 
        self.env["version"] = pkgrefs[0].attributes["version"].value
        self.output("Found version %s" % self.env["version"])


if __name__ == "__main__":
    PROCESSOR = PackageInfoVersioner()
    PROCESSOR.execute_shell()
