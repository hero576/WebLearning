from fdfs_client.client import Fdfs_client
from django.core.files.storage import Storage
from django.conf import settings

class FdfsStorage(Storage):
    def __init__(self):
        self.client=settings.FDFS_CLIENT
        self.server=settings.FDFS_SERVER

    def open(self, name, mode='rb'):
        pass

    def save(self, name, content, max_length=None):
        client = Fdfs_client(self.client)
        try:
            ret = client.upload_by_buffer(content.read())
        except:
            raise

        if ret.get("Status") == "Upload successed.":
            return ret.get("Remote file_id")
        else:
            raise Exception(ret.get("Status"))

    def url(self, name):
        return self.server+name


