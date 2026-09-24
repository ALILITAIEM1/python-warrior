import os

from .config import Config


class Tower:
    def __init__(self, path):
        self.path = os.path.join(Config.towers_dir(), path)

    @property
    def name(self):
        return os.path.basename(self.path)

    def __str__(self):
        return self.name
