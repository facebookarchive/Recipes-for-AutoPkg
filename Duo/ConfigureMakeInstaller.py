#!/usr/bin/python
#
# Copyright 2015 Facebook, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""See docstring for ConfigureMakeInstaller class"""

# Disabling warnings for env members and imports that only affect recipe-
# specific processors.
# pylint: disable=e1101,f0401

import subprocess
import os

from autopkglib import Processor, ProcessorError

__all__ = ["ConfigureMakeInstaller"]


class ConfigureMakeInstaller(Processor):
  # pylint: disable=missing-docstring
  description = ("Runs Configure, Make, Make Install on target directory.")
  input_variables = {
    "installer_dir_path": {
      "required": True,
      "description": "Path to directory containing Configure file."
    },
    "prefix_path": {
      "required": False,
      "description": "Path to apply to --prefix argument."
    },
    "output_path": {
      "required": False,
      "description": ('Path to output location. If not specified, '
                      '\'make install\' may install things outside '
                      'the cache directory. Be warned!')
    }
  }
  output_variables = {
  }

  __doc__ = description

  def main(self):
    conf_path = self.env["installer_dir_path"]
    makefile = os.path.join(conf_path, 'Makefile')
    os.chdir(conf_path)
    cmd = ['./configure']
    if self.env["prefix_path"]:
      cmd = ['./configure --prefix=' + self.env["prefix_path"]]

    # ./configure
    self.output("Command: %s" % cmd)
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True)
    (conf_out, conf_err) = proc.communicate()
    if conf_err:
      raise ProcessorError("./configure error: %s" % conf_err)
    self.output(conf_out)

    # make
    self.output("Running make")
    cmd = ['/usr/bin/make -f %s' % makefile]
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True)
    (m_out, m_err) = proc.communicate()
    # if m_err:
    #   raise ProcessorError("make error: %s" % m_err)
    self.output(m_out)

    # make install
    self.output("Running make install")
    destpath = self.env.get("output_path")
    cmd = ['/usr/bin/make install -f %s' % makefile]
    if destpath:
      cmd = ['/usr/bin/make install -f %s DESTDIR=%s' % (makefile, destpath)]
    self.output("install cmd: %s" % cmd)
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True)
    (mi_out, mi_err) = proc.communicate()
    # if mi_err:
    #   raise ProcessorError("make install error: %s" % mi_err)
    self.output(mi_out)


if __name__ == "__main__":
  PROCESSOR = ConfigureMakeInstaller()
  PROCESSOR.execute_shell()
