from django.contrib.staticfiles.storage import ManifestStaticFilesStorage
import os


class IgnoreStaticFilesStorage(ManifestStaticFilesStorage):
    def path(self, name):
        # List of files you want to block
        blocked_files = ["owl.video.play.html", "nouislider.css"]

        # If the file is blocked, return None or an invalid path
        if any(file in name for file in blocked_files):
            return None  # This silently prevents the file from being served

        return super().path(name)

    def url(self, name):
        # If the file is blocked, return an empty string or an invalid URL
        blocked_files = ["owl.video.play.html", "nouislider.css"]

        if any(file in name for file in blocked_files):
            return ""  # This prevents the file from being served without errors

        return super().url(name)
