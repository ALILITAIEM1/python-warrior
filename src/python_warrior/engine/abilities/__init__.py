"""Registry of abilities, keyed like in Ruby: actions end with "!"."""

from ...utils import camelize
from .attack import Attack
from .base import Base
from .bind import Bind
from .detonate import Detonate
from .direction_of import DirectionOf
from .direction_of_stairs import DirectionOfStairs
from .distance_of import DistanceOf
from .explode import Explode
from .feel import Feel
from .form import Form
from .health import Health
from .listen import Listen
from .look import Look
from .pivot import Pivot
from .rescue import Rescue
from .rest import Rest
from .shoot import Shoot
from .walk import Walk

ABILITIES = {
    cls.__name__: cls
    for cls in (Attack, Bind, Detonate, DirectionOf, DirectionOfStairs, DistanceOf, Explode,
                Feel, Form, Health, Listen, Look, Pivot, Rescue, Rest, Shoot, Walk)
}


def ability_class(name):
    return ABILITIES[camelize(name.replace("!", ""))]


def player_method(name):
    """Name of the method the player calls for an ability ("walk!" -> "walk")."""
    return name.rstrip("!")


__all__ = ["ABILITIES", "Base", "ability_class", "player_method"]
