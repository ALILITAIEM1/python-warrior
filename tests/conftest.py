import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from python_warrior.config import Config  # noqa: E402
from python_warrior.events import bus  # noqa: E402
from python_warrior.ui import UI, TextBackend  # noqa: E402

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


@pytest.fixture(autouse=True)
def reset_config():
    Config.reset()
    UI.use(TextBackend())
    bus.clear()
    yield
    Config.reset()
    bus.clear()
