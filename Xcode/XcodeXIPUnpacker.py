#!/usr/bin/python
"""Unpack an Xcode XIP."""
#
# Copyright 2016-present Facebook, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Disabling warnings for env members and imports that only affect recipe-
# specific processors.
# pylint: disable=e1101,f0401


from autopkglib import Processor, ProcessorError
import glob
import os
import shutil
import struct
import subprocess


__all__ = ["XcodeXIPUnpacker"]


class XcodeXIPUnpacker(Processor):
  """Unpack a XIP file from Apple."""

  description = "Unpack an Apple XIP file."
  input_variables = {
    "PKG": {
      "required": True,
      "description": "Path to an Xcode .xip file.",
    },
    "output_path": {
      "required": False,
      "description": ("Path to unpack the contents. Defaults to "
                      "%RECIPE_CACHE_DIR%/%NAME%_unpack.")
    },
    "nocleanup": {
      "required": False,
      "description": ("Don't clean up temp archives after extraction. "
                      "Defaults to False.")
    }
  }
  output_variables = {
    "output_app": {
      "description": "Path to the extracted Xcode.app."
    }
  }

  __doc__ = description

  def ditto_unpack(self, cpio_path, output_dir):
    """Extract cpio archive with ditto."""
    self.output("Ditto extraction of CPIO archive %s" % cpio_path)
    cmd = [
      '/usr/bin/ditto',
      '-x',
      cpio_path,
      output_dir
    ]
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    (out, err) = proc.communicate()
    if err:
      raise ProcessorError(err)
    self.output(out)
    self.output("Finished ditto extraction.")

  def gunzip_unpack(self, xz_path, output_dir):
    """Unpack the xz file into the same dir."""
    self.output("Gunzip unpacking %s" % xz_path)
    current_dir = os.getcwd()
    os.chdir(os.path.join(output_dir, 'temp'))
    cmd = [
      '/usr/bin/gunzip',
      xz_path,
      '-f',
    ]
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    (out, err) = proc.communicate()
    if err:
      raise ProcessorError(err)
    self.output(out)
    os.chdir(current_dir)
    self.output("Finished gunzipping.")

  def xar_unpack(self, xip_path, output_dir):
    """Unpack the .xip as a .xar encoding."""
    self.output("Xar unpacking %s" % xip_path)
    cmd = [
      '/usr/bin/xar',
      '-xf',
      xip_path,
      '-C',
      output_dir,
    ]
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    (out, err) = proc.communicate()
    if err:
      raise ProcessorError(err)
    self.output(out)
    self.output("Finished xar unpack.")

  # This function was written by Mike Lynn:
  # https://gist.github.com/pudquick/ac29c8c19432f2d200d4
  def parse_pbzx(self, pbzx_path, xar_out_path):
    """Unpack a pbzx file."""
    self.output("PBZX unpacking %s" % pbzx_path)
    with open(pbzx_path, 'rb') as f:
      with open(xar_out_path, 'wb') as g:
        real_magic = '\xfd7zXZ\x00'
        magic = f.read(4)
        if magic != 'pbzx':
          raise Exception("Error: Not a pbzx file")
        # Read 8 bytes for initial flags
        tmp = f.read(8)
        # Interpret the flags as a 64-bit big-endian unsigned int
        flags = struct.unpack('>Q', tmp)[0]
        # xar_f is a dummy variable
        xar_f = open(xar_out_path, 'wb')
        while (flags & (1 << 24)):
          # Read in more flags
          tmp1 = f.read(8)
          if len(tmp1) < 8:
            # We're at the end!
            break
          flags = struct.unpack('>Q', tmp1)[0]
          # Read in length
          tmp2 = f.read(8)
          f_length = struct.unpack('>Q', tmp2)[0]
          xzmagic = f.read(6)
          if xzmagic != real_magic:
            raise Exception("Error: Header is not xar file header")
          f.seek(-6, 1)
          g.write(f.read(f_length))
    self.output("Finished pbzx decode.")

  def main(self):
    """Main."""
    xip_path = self.env['PKG']
    if self.env.get('output_path'):
      output = self.env['output_path']
    else:
      output = os.path.join(
        self.env['RECIPE_CACHE_DIR'],
        self.env['NAME'] + '_unpack',
      )
    if not os.path.isdir(output):
      os.makedirs(output)
    # 1. xar unpack the file
    xar_path = os.path.join(
      output,
      'xar',
    )
    if not os.path.isdir(xar_path):
      os.makedirs(xar_path)
    self.xar_unpack(xip_path, xar_path)
    # 2. PBZX unpack the output
    content_path = os.path.join(
      xar_path,
      'Content',
    )
    xz_output = os.path.join(
      output,
      'temp',
      'Content.xz',
    )
    if not os.path.isdir(os.path.dirname(xz_output)):
      os.makedirs(os.path.dirname(xz_output))
    self.parse_pbzx(content_path, xz_output)
    # 3. gunzip the content
    self.gunzip_unpack(xz_output, output)
    # 4. Move to cpio format
    current_cpio_path = os.path.join(
      output,
      'temp',
      'Content',
    )
    new_cpio_path = os.path.join(
      output,
      'temp',
      'Content.cpio',
    )
    os.rename(content_path, new_cpio_path)
    # 5. Ditto contents out of cpio archive
    self.ditto_unpack(current_cpio_path, output)
    # 6. Clean up if desired
    cleanup = True
    if bool(self.env.get('nocleanup')) is True:
      cleanup = False
    if cleanup:
      self.output("Cleaning up temporary archives.")
      shutil.rmtree(xar_path)
      shutil.rmtree(os.path.join(output, 'temp',))
    # Set output
    self.env['output_app'] = glob.glob(
      os.path.join(output, 'Xcode*'),
    )[0]

if __name__ == '__main__':
  processor = XcodeXIPUnpacker()
  processor.execute_shell()
