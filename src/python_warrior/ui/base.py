"""User interface facade (port of RubyWarrior::UI).

``UI`` keeps the exact text behaviour of the Ruby version through a text
backend bound to ``Config.in_stream`` / ``Config.out_stream``. A different
backend (the 2D graphical one) can be plugged with ``UI.use(backend)``.
"""

import time

from ..config import Config


class Backend:
    """Interface every UI backend implements."""

    def puts(self, msg):
        raise NotImplementedError

    def print(self, msg):
        raise NotImplementedError

    def gets(self):
        raise NotImplementedError

    def request(self, msg):
        self.print(msg)
        return self.gets().rstrip("\r\n")

    def ask(self, msg):
        return self.request(f"{msg} [yn] ") == "y"

    def choose(self, item, options):
        if len(options) == 1:
            response = options[0]
        else:
            for i, option in enumerate(options):
                label = option[-1] if isinstance(option, tuple) else option
                self.puts(f"[{i + 1}] {label}")
            choice = self.request(f"Choose {item} by typing the number: ")
            try:
                index = int(choice.strip() or 0) - 1
            except ValueError:
                index = -1
            # Ruby's options[-1] returns the last element, keep that behaviour
            response = options[index] if -len(options) <= index < len(options) else None
        if isinstance(response, tuple):
            return response[0]
        return response

    # Hooks called by the level loop, used by graphical backends.
    def level_started(self, level):
        pass

    def turn_started(self, level, number):
        pass

    def turn_finished(self, level, number):
        pass

    def level_finished(self, level):
        pass

    def wait(self, seconds):
        time.sleep(seconds)


class TextBackend(Backend):
    def puts(self, msg):
        if Config.out_stream:
            Config.out_stream.write(f"{msg}\n")
            if hasattr(Config.out_stream, "flush"):
                Config.out_stream.flush()

    def print(self, msg):
        if Config.out_stream:
            Config.out_stream.write(str(msg))
            if hasattr(Config.out_stream, "flush"):
                Config.out_stream.flush()

    def gets(self):
        if Config.in_stream:
            return Config.in_stream.readline()
        return ""


class UI:
    backend = TextBackend()

    @classmethod
    def use(cls, backend):
        cls.backend = backend

    @classmethod
    def puts(cls, msg):
        cls.backend.puts(msg)

    @classmethod
    def puts_with_delay(cls, msg):
        cls.backend.puts(msg)
        if Config.delay:
            cls.backend.wait(Config.delay)

    @classmethod
    def print(cls, msg):
        cls.backend.print(msg)

    @classmethod
    def gets(cls):
        return cls.backend.gets()

    @classmethod
    def request(cls, msg):
        return cls.backend.request(msg)

    @classmethod
    def ask(cls, msg):
        return cls.backend.ask(msg)

    @classmethod
    def choose(cls, item, options):
        return cls.backend.choose(item, options)
