import os
import shutil
import tempfile


class TemporaryDirectory(object):
    def __init__(self):
        self.name = tempfile.mkdtemp()

    def cleanup(self):
        shutil.rmtree(self.name)


class TemporaryFile(object):
    def __init__(self, ext=""):
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.name = "".join([temp_file.name, ext])

        self.fd = temp_file
        self.name = temp_file.name

    def cleanup(self):
        os.unlink(self.name)
