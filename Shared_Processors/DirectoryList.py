#!/usr/bin/python
#
# Copyright 2013 Jesse Peterson
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""See docstring for DirectoryList class"""


from glob import glob
import os
from autopkglib import Processor, ProcessorError

__all__ = ["DirectoryList"]


class DirectoryList(Processor):
  '''Returns a list of items in a subdirectory as
   a string, separated by commas. Does not recurse
   into subdirectories.
  '''

  input_variables = {
    'pattern': {
      'description': 'Shell glob pattern to match files by',
      'required': True,
    },
    'find_method': {
      'description': ('Type of pattern to match. Currently only '
                      'supported type is "glob" (also the default)'),
      'default': 'glob',
      'required': False,
    },
    'remove_extension': {
      'description': ('Remove the extension at the end. Default to '
                      'False.'),
      'default': False,
      'required': False,
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
      'description': 'Found filename',
    }
  }

  description = __doc__

  def globfind(self, pattern):
    '''Returns multiple files matching a glob'''
    # pylint: disable=no-self-use

    glob_matches = glob(pattern)

    if len(glob_matches) < 1:
      raise ProcessorError('No matching filename found')

    glob_matches.sort()

    # return glob_matches
    new_glob = []
    for glob_item in glob_matches:
      new_string = os.path.basename(glob_item)
      if self.env['remove_extension']:
        new_string = os.path.splitext(new_string)[0]
      new_glob.append(new_string)
    return new_glob

  def main(self):
    pattern = self.env.get('pattern')
    method = self.env.get('find_method')

    format_string = '%s' % self.env['suffix_string']
    search_string = '{0}'
    if method == 'glob':
      self.env['found_filenames'] = search_string.format(
        format_string.join(self.globfind(pattern))).strip()
    else:
      raise ProcessorError('Unsupported find_method: %s' % method)
    self.output('Found matches: %s' % self.env['found_filenames'])

if __name__ == '__main__':
  PROCESSOR = DirectoryList()
  PROCESSOR.execute_shell()
