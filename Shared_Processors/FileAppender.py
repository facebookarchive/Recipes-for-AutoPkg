#!/usr/bin/python
#
# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
#
"""Processor that creates a file"""

from autopkglib import Processor, ProcessorError


__all__ = ["FileAppender"]


class FileAppender(Processor):
  """Append contents to the end of a file."""
  description = __doc__
  input_variables = {
    "file_path": {
      "required": True,
      "description": "Path to a file to append to.",
    },
    "file_content": {
      "required": True,
      "description": "Contents to add to a file.",
    }
  }
  output_variables = {
  }

  def main(self):
    try:
      with open(self.env['file_path'], "a") as fileref:
        fileref.write(self.env['file_content'])
      self.output("Appened to file at %s" % self.env['file_path'])
    except BaseException, err:
      raise ProcessorError("Can't append to file at %s: %s"
                           % (self.env['file_path'], err))
    # clean the variable up afterwards to not poison future runs
    self.env['file_content'] = ''
    self.env['file_path'] = ''

if __name__ == '__main__':
  PROCESSOR = FileAppender()
  PROCESSOR.execute_shell()
