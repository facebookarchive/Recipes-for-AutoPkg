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
    os.chdir(output_dir)
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
  # https://gist.github.com/pudquick/ff412bcb29c9c1fa4b8d
  def seekread(self, f, offset=None, length=0, relative=True):
    """Seek read an archive."""
    if (offset is not None):
      # offset provided, let's seek
      f.seek(offset, [0, 1, 2][relative])
    if (length != 0):
      return f.read(length)

  def parse_pbzx(self, pbzx_path):
    """Parse a pbzx archive."""
    section = 0
    xar_out_path = '%s.part%02d.cpio.xz' % (pbzx_path, section)
    f = open(pbzx_path, 'rb')
    # pbzx = f.read()
    # f.close()
    magic = self.seekread(f, length=4)
    if magic != 'pbzx':
      raise "Error: Not a pbzx file"
    # Read 8 bytes for initial flags
    flags = self.seekread(f, length=8)
    # Interpret the flags as a 64-bit big-endian unsigned int
    flags = struct.unpack('>Q', flags)[0]
    xar_f = open(xar_out_path, 'wb')
    while (flags & (1 << 24)):
      # Read in more flags
      flags = self.seekread(f, length=8)
      flags = struct.unpack('>Q', flags)[0]
      # Read in length
      f_length = self.seekread(f, length=8)
      f_length = struct.unpack('>Q', f_length)[0]
      xzmagic = self.seekread(f, length=6)
      if xzmagic != '\xfd7zXZ\x00':
        # This isn't xz content, this is actually _raw decompressed cpio_
        # chunk of 16MB in size...
        # Let's back up ...
        self.seekread(f, offset=-6, length=0)
        # ... and split it out ...
        f_content = self.seekread(f, length=f_length)
        section += 1
        decomp_out = '%s.part%02d.cpio' % (pbzx_path, section)
        g = open(decomp_out, 'wb')
        g.write(f_content)
        g.close()
        # Now to start the next section, which should hopefully be .xz
        # (we'll just assume it is ...)
        xar_f.close()
        section += 1
        new_out = '%s.part%02d.cpio.xz' % (pbzx_path, section)
        xar_f = open(new_out, 'wb')
      else:
        f_length -= 6
        # This part needs buffering
        f_content = self.seekread(f, length=f_length)
        tail = self.seekread(f, offset=-2, length=2)
        xar_f.write(xzmagic)
        xar_f.write(f_content)
        if tail != 'YZ':
          xar_f.close()
          raise "Error: Footer is not xar file footer"
    try:
      f.close()
      xar_f.close()
    except:
      pass

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
    self.parse_pbzx(content_path)
    # 3. gunzip the xz packages
    xz_list = glob.glob(os.path.join(xar_path, "*.xz"))
    for xz_file in xz_list:
      self.gunzip_unpack(xz_file, output)
    # 4. Combine the cpio files into one
    self.output("Combining .cpio files together")
    cpio_list = glob.glob(os.path.join(xar_path, "*.cpio"))
    new_cpio_path = os.path.join(
      output,
      'Content.cpio',
    )
    with open(new_cpio_path, 'wb') as cpio_combined_file:
      for cpio_file in cpio_list:
        with open(cpio_file, 'rb') as f:
          shutil.copyfileobj(f, cpio_combined_file)
    # 5. Ditto contents out of cpio archive
    self.ditto_unpack(new_cpio_path, output)
    # 6. Clean up if desired
    cleanup = True
    if bool(self.env.get('nocleanup')) is True:
      cleanup = False
    if cleanup:
      self.output("Cleaning up temporary archives.")
      shutil.rmtree(xar_path)
    # Set output
    self.env['output_app'] = glob.glob(
      os.path.join(output, 'Xcode*'),
    )[0]

if __name__ == '__main__':
  processor = XcodeXIPUnpacker()
  processor.execute_shell()
