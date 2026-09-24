"""String and number helpers (port of core_additions.rb)."""

import math
import re


def underscore(word):
    word = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", word)
    word = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", word)
    return word.replace("-", "_").lower()


def camelize(word):
    return re.sub(r"(?:^|_)(.)", lambda m: m.group(1).upper(), word)


def humanize(word):
    return word.replace("_", " ").capitalize()


def titleize(word):
    return re.sub(r"\b('?[a-z])", lambda m: m.group(1).capitalize(), humanize(underscore(word)))


def hard_wrap(text, width=80):
    return re.sub(r"(.{1,%d})(\s+|$)" % width, "\\1\n", text).strip()


def ruby_round(value):
    """Round half away from zero, like Ruby's Float#round."""
    return int(math.floor(abs(value) + 0.5)) * (1 if value >= 0 else -1)
