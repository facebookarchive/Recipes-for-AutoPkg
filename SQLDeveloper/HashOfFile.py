import hashlib

from autopkglib import Processor, ProcessorError

__all__ = ["HashOfFile"]

class HashOfFile(Processor):
    # pylint: disable=missing-docstring
    description = "Read the version.properties file inside the SQLDeveloper.app."
    input_variables = {
        "hashfile_path": {
            "required": True,
            "description": "Path to file you want hash of",
        }
    }
    output_variables = {"hashoffile": {"description": "Hash of the requested file"}}

    __doc__ = description

    def hash_file(self, filename):
        # make a hash object
        h = hashlib.md5()
        #h = hashlib.sha1()

        # open file for reading in binary mode
        with open(filename,'rb') as file:

            # loop till the end of the file
            chunk = 0
            while chunk != b'':
                # read only 1024 bytes at a time
                chunk = file.read(1024)
                h.update(chunk)

        # return the hex representation of digest
        return h.hexdigest()

    def main(self):
        self.output(self.env['hashfile_path'])
        self.env['hashoffile'] = self.hash_file(self.env['hashfile_path'])
if __name__ == "__main__":
    PROCESSOR = HashOfFile()
    PROCESSOR.execute_shell()