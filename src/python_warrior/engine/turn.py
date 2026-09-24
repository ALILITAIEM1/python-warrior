"""The object handed to ``play_turn``: exposes only the unlocked abilities.

Actions (Ruby ``walk!``) become ``turn.walk()``; only one action may be
chosen per turn. Senses (``feel``, ``look``...) are performed immediately.
"""


class Turn:
    def __init__(self, abilities):
        self.action = None
        self._senses = {}
        for name, sense in abilities.items():
            if name.endswith("!"):
                self._add_action(name)
            else:
                self._add_sense(name, sense)

    def _add_action(self, action):
        def perform(*args):
            if self.action:
                raise RuntimeError("Only one action can be performed per turn.")
            self.action = (action, *args)

        setattr(self, action[:-1], perform)

    def _add_sense(self, name, sense):
        self._senses[name] = sense

        def perform(*args):
            return self._senses[name].perform(*args)

        setattr(self, name, perform)
