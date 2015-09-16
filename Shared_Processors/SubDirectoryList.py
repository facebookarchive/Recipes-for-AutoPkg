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
"""See docstring for SubDirectoryList class"""


import os
from autopkglib import Processor, ProcessorError

__all__ = ["SubDirectoryList"]


class SubDirectoryList(Processor):
  '''Returns a string-converted list of comma-separated items inside
  a directory, relative to path root, for use in other Processors.'''

  input_variables = {
    'root_path': {
      'description': 'Path to start looking for files.',
      'required': True,
    },
    'suffix_string': {
      'description': ("String to append to each found item name in dir."
                      "Defaults to ','"),
      'default': ',',
      'required': False,
    }
  }
  output_variables = {
    'found_filenames': {
      'description': ('String containing a list of all files found '
                      'relative to root_path, separated by '
                      'suffix_string.')
    },
    'found_directories': {
      'description': ('String containg a list of all directories '
                      'found relative to root_path, separated by '
                      'suffix_string.')
    },
    'relative_root': {
      'description': ('Relative root path')
    }
  }

  description = __doc__

  def main(self):
    format_string = '%s' % self.env['suffix_string']
    # search_string = '  \'{0}\''
    search_string = '{0}'
    dir_list = list()
    file_list = list()
    if not os.path.isdir(self.env['root_path']):
      raise ProcessorError("Can't find root path!")
    for dirName, subdirList, fileList in os.walk(self.env['root_path']):
      # print('Found directory: %s' % dirName)
      relative_path = os.path.relpath(dirName, self.env['root_path'])
      if not relative_path == '.':
        dir_list.append(relative_path)
      # search_string.format(format_string.join(dirName)).strip()
      for fname in fileList:
        if '.DS_Store' in fname:
          continue
        # print('\t%s' % fname)
        relpath = os.path.relpath(os.path.join(fname, dirName),
                                  self.env['root_path'])
        self.output("Relative path: %s" % relpath)
        if relpath == ".":
          # we want to avoid prepending './' to files at root dir
          relpath = ''
        # print "Real relative path: %s" % relpath
        file_list.append(os.path.join(relpath, fname))
    self.env['found_directories'] = search_string.format(
      format_string.join(dir_list)).strip()
    self.env['found_filenames'] = search_string.format(
      format_string.join(file_list)).strip()

if __name__ == '__main__':
  PROCESSOR = SubDirectoryList()
  PROCESSOR.execute_shell()
