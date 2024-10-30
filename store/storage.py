# my_store/storage.py

from django.contrib.staticfiles.storage import StaticFilesStorage
from django.conf import settings
from django.utils._os import safe_join
import os


class CustomStaticFilesStorage(StaticFilesStorage):
    def get_files(self, ignore_patterns=None, location="", ignore=None):
        if ignore_patterns is None:
            ignore_patterns = []
        # Add custom ignore patterns here
        ignore_patterns += [
            "www.portotheme.com/html/molla/assets/css/plugins/owl-carousel/owl.video.play.html"
        ]
        return super().get_files(ignore_patterns, location, ignore)
