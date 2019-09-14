#!/usr/bin/python
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.#
"""See docstring for SQLDeveloperVersioner class"""

# Disabling warnings for env members and imports that only affect recipe-
# specific processors.
# pylint: disable=e1101,f0401

from __future__ import absolute_import

import ConfigParser
import os.path

from autopkglib import Processor, ProcessorError

__all__ = ["SQLDeveloperVersioner"]


# this code stolen directly from
# http://stackoverflow.com/questions/2819696/parsing-properties-file-in-python/2819788#2819788
class FakeSecHead(object):
  def __init__(self, fp):
    self.fp = fp
    self.sechead = '[properties]\n'

  def readline(self):
    if self.sechead:
      try:
        return self.sechead
      finally:
        self.sechead = None
    else:
      return self.fp.readline()


class SQLDeveloperVersioner(Processor):
  # pylint: disable=missing-docstring
  description = ("Read the version.properties file inside the "
                 "SQLDeveloper.app.")
  input_variables = {
    "app_path": {
      "required": True,
      "description": "Path to app to find the version.properties file in."
    }
  }
  output_variables = {
    "version": {
      "description": "Actual version of app."
    }
  }

  __doc__ = description

  def main(self):
    # Unsurprisingly, SQLDeveloper fails to include a useful version in
    # the app's Info.plist.  Instead, the actual version is buried deep
    # inside in a file called "version.properties". Thanks, Oracle.
    # You know, I was a having a pretty good day up until now...
    relative_path = \
      'Contents/Resources/sqldeveloper/sqldeveloper/bin/version.properties'
    file_path = os.path.join(self.env['app_path'], relative_path)
    # this code stolen directly from
    # http://stackoverflow.com/questions/2819696/parsing-properties-file-in-python/2819788#2819788
    cp = ConfigParser.SafeConfigParser()
    try:
      cp.readfp(FakeSecHead(open(file_path)))
    except IOError as err:
      raise ProcessorError(err)
    self.env['version'] = cp.get('properties', 'ver_full')
    self.output("Version: %s" % self.env['version'])

if __name__ == "__main__":
    PROCESSOR = SQLDeveloperVersioner()
    PROCESSOR.execute_shell()
