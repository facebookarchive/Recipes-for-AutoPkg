#!/usr/bin/python
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Get all Version information from Xcode."""


from collections import namedtuple

from autopkglib import Processor, ProcessorError


try:
    import objc
except ImportError:
    pass

__all__ = ["XcodeVersioner"]


class XcodeVersioner(Processor):
    """Break down a version number into its separate components."""

    description = __doc__
    input_variables = {
        "version": {
            "required": True,
            "description": (
                "CFBundleShortVersionString from an Xcode Info.plist. Produced by "
                "PlistReader."
            ),
        },
        "app_path": {
            "required": True,
            "description": (
                "Path to Xcode app to look up version information from the bundle."
            ),
        },
    }
    output_variables = {
        "major_version": {"description": "Major version of Xcode - i.e. Xcode 7, 8."},
        "minor_version": {
            "description": "Minor version of Xcode - i.e. Xcode X.1, X.2."
        },
        "patch_version": {
            "description": (
                "Patch version of Xcode - i.e. Xcode X.Y.0, X.Y.1. "
                "Patch version will be normalized to 0 if missing (i.e. 8.3 "
                "becomes 8.3.0)."
            )
        },
        "is_beta": {
            "description": ("Boolean that is true if this Xcode is a beta version.")
        },
        "beta_version": {"description": ("The beta number - 1, 2, 3, etc.")},
        "build_version": {"description": ("Build version of Xcode - e.g. 11B500")},
    }

    __doc__ = description

    def _load_objc_framework(self, f_name, f_path, class_whitelist):
        loaded = {}
        framework_bundle = objc.loadBundle(  # NOQA
            f_name, bundle_path=f_path, module_globals=loaded
        )
        desired = {}
        for x in class_whitelist:
            if x in loaded:
                desired[x] = loaded[x]
        return namedtuple("AttributedFramework", desired.keys())(**desired)

    def xcode_info(self, app_path):
        DVTFoundation_path = (
            "%s/Contents/SharedFrameworks/" + "DVTFoundation.framework"
        ) % app_path
        desired_classes = ["DVTToolsInfo"]
        DVTFoundation = self._load_objc_framework(
            "DVTFoundation", DVTFoundation_path, desired_classes
        )
        x_info = DVTFoundation.DVTToolsInfo.toolsInfo()
        x_v = x_info.toolsVersion()
        x_b = x_info.toolsBuildVersion()
        app_info = []
        app_info.append(["major_version", str(x_v.versionMajorComponent())])
        app_info.append(["minor_version", str(x_v.versionMinorComponent())])
        app_info.append(["patch_version", str(x_v.versionUpdateComponent())])
        app_info.append(["build_version", x_b.name()])
        is_beta = bool(x_info.isBeta())
        app_info.append(["is_beta", is_beta])
        if is_beta:
            app_info.append(["beta_version", str(x_info.toolsBetaVersion())])
        else:
            app_info.append(["beta_version", "0"])
        return app_info

    def main(self):
        """Main."""
        main_version_string = self.env["version"]
        split_string = main_version_string.split(".")
        if len(split_string) < 2:
            raise ProcessorError(
                "Version string should be in format X.Y, unless Apple broke "
                "literally everything again."
            )
        self.env["major_version"] = str(split_string[0])
        self.output("Major version: %s" % self.env["major_version"])
        self.env["minor_version"] = str(split_string[1])
        self.output("Minor version: %s" % self.env["minor_version"])
        try:
            self.env["patch_version"] = split_string[2]
        except IndexError:
            self.output("Normalizing patch to 0")
            self.env["patch_version"] = str("0")
        self.env["is_beta"] = False
        xcode_info_results = self.xcode_info(self.env["app_path"])
        xcode_data = {}
        for info_pair in xcode_info_results:
            xcode_data[info_pair[0]] = info_pair[1]
        if xcode_data["is_beta"]:
            self.output("Beta version: %s" % xcode_data["beta_version"])
            self.env["is_beta"] = xcode_data["is_beta"]
            self.env["beta_version"] = xcode_data["beta_version"]
        self.output("Patch version: %s" % self.env["patch_version"])

        self.env["build_version"] = xcode_data["build_version"]
        self.output("Build version: %s" % self.env["build_version"])


if __name__ == "__main__":
    PROCESSOR = XcodeVersioner()
    PROCESSOR.execute_shell()
