"""Event bus decoupling the game engine from its views.

The engine emits typed events (unit moved, attacked, died...) and any view
(console, 2D graphics, tests) can subscribe to them. The engine never
depends on a view.
"""

from dataclasses import dataclass, field


@dataclass
class Event:
    kind: str
    unit: object = None
    data: dict = field(default_factory=dict)

    def __getitem__(self, key):
        return self.data[key]

    def get(self, key, default=None):
        return self.data.get(key, default)


class EventBus:
    def __init__(self):
        self._listeners = []

    def subscribe(self, listener):
        self._listeners.append(listener)
        return listener

    def unsubscribe(self, listener):
        if listener in self._listeners:
            self._listeners.remove(listener)

    def clear(self):
        self._listeners.clear()

    def emit(self, kind, unit=None, **data):
        event = Event(kind, unit, data)
        for listener in list(self._listeners):
            listener(event)
        return event


bus = EventBus()


def emit(kind, unit=None, **data):
    return bus.emit(kind, unit, **data)
