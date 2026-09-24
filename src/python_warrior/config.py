"""Global game configuration (port of RubyWarrior::Config)."""

import os


class Config:
    delay = None
    in_stream = None
    out_stream = None
    practice_level = None
    path_prefix = "."
    skip_input = False
    towers_path = None  # overrides the bundled towers directory (used by tests)

    @classmethod
    def reset(cls):
        cls.delay = None
        cls.in_stream = None
        cls.out_stream = None
        cls.practice_level = None
        cls.path_prefix = "."
        cls.skip_input = False
        cls.towers_path = None

    @classmethod
    def towers_dir(cls):
        return cls.towers_path or os.path.join(os.path.dirname(__file__), "towers")

    @classmethod
    def templates_dir(cls):
        return os.path.join(os.path.dirname(__file__), "templates")
