# Python Warrior

Portage en Python de [Ruby Warrior](https://github.com/ryanb/ruby-warrior), avec une **interface graphique 2D** (pygame).

Vous écrivez l'intelligence d'un guerrier dans `player.py`. À chaque tour, votre code décide de l'action : avancer, attaquer, se reposer, délivrer un captif… Le but est d'atteindre l'escalier et de gravir les 9 niveaux de chaque tour (`beginner`, `intermediate`).

Les règles, les niveaux, les dégâts, les scores et les notes (S à F) sont identiques à ceux de la version Ruby.

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[gui]"
```

Python 3.10 ou plus récent est requis. pygame (`pygame-ce`) n'est nécessaire que pour le mode graphique.

## Jouer

```bash
.venv/bin/pywarrior          # mode console (identique à l'original)
.venv/bin/pywarrior --gui    # mode graphique 2D
```

1. Au premier lancement, un dossier `pywarrior/` est créé. Choisissez une tour et un nom.
2. Lisez `pywarrior/<nom>-<tour>/README` et modifiez `player.py`.
3. Relancez `pywarrior` pour jouer le niveau.

Options (identiques à `rubywarrior`) :

| Option | Rôle |
|---|---|
| `-d DIR` | Utiliser un autre dossier de jeu |
| `-l N` | S'entraîner sur le niveau N (mode epic) |
| `-s` | Ne rien demander (pas de questions interactives) |
| `-t SEC` | Délai entre les messages en mode console (0,6 s par défaut) |
| `-g`, `--gui` | Interface graphique 2D |

### Commandes du mode graphique

| Touche | Action |
|---|---|
| `Espace` / `P` | Pause / reprise |
| `N` / `→` | Avancer d'un seul tour (pas à pas) |
| `+` / `-` (ou `↑` / `↓`) | Vitesse ×0,25 à ×8 |
| `Échap` / `Q` | Quitter |
| `1`–`9`, `O` / `N`, `Entrée` | Répondre aux dialogues |

À la fin d'une session, **Rejouer** recharge `player.py` depuis le disque. Vous pouvez donc corriger votre code sans fermer la fenêtre. Si votre code lève une exception, la trace s'affiche dans le journal.

## Écrire son guerrier

```python
class Player:
    def play_turn(self, warrior):
        if warrior.feel().is_empty():
            warrior.walk()
        else:
            warrior.attack()
```

L'API reprend celle de Ruby Warrior, avec des noms pythoniques :

| Ruby | Python |
|---|---|
| `warrior.walk!` / `walk!(:backward)` | `warrior.walk()` / `warrior.walk("backward")` |
| `warrior.attack!`, `rest!`, `rescue!`, `pivot!`, `shoot!`, `bind!`, `detonate!` | `warrior.attack()`, `rest()`, `rescue()`, `pivot()`, `shoot()`, `bind()`, `detonate()` |
| `warrior.feel`, `warrior.look`, `warrior.listen` | `warrior.feel()`, `warrior.look()`, `warrior.listen()` |
| `warrior.health` | `warrior.health()` |
| `warrior.direction_of_stairs`, `direction_of(space)`, `distance_of(space)` | idem, avec des parenthèses |
| `space.empty?`, `enemy?`, `captive?`, `wall?`, `stairs?`, `ticking?`, `golem?`, `player?` | `space.is_empty()`, `is_enemy()`, `is_captive()`, `is_wall()`, `is_stairs()`, `is_ticking()`, `is_golem()`, `is_player()` |
| `@health` | `self.health` (attribut de votre classe `Player`) |
| `:forward`, `:left`… | `"forward"`, `"left"`, `"right"`, `"backward"` |

Comme en Ruby, une seule action est autorisée par tour, et seules les capacités débloquées existent sur l'objet `warrior`.

## Architecture

```
src/python_warrior/
├── cli.py               # options de ligne de commande (← Runner)
├── config.py            # configuration globale (← Config)
├── game.py              # déroulé : profils, mode normal, mode epic (← Game)
├── profile.py, tower.py # sauvegarde .profile (JSON + base64 au lieu de Marshal)
├── level.py             # boucle des tours, score, notes (← Level)
├── level_loader.py      # DSL des fichiers de niveau (← LevelLoader)
├── player_generator.py  # génère player.py et le README de chaque niveau
├── events.py            # bus d'événements moteur → vues
├── engine/
│   ├── position.py, space.py, floor.py, turn.py
│   ├── units/           # warrior, sludge, thick_sludge, archer, wizard, captive, golem
│   └── abilities/       # les 18 capacités (walk, attack, feel, look, listen, detonate…)
├── towers/              # beginner/ et intermediate/, level_001.py … level_009.py
├── templates/player.py
└── ui/
    ├── base.py          # façade UI + interface Backend ; TextBackend = console
    └── graphics2d/      # backend pygame
        ├── app.py         # GuiBackend : dialogues, boucle d'affichage, rythme des tours
        ├── board.py       # modèle de vue du plateau + dessin (tuiles, murs, escalier, unités)
        ├── animations.py  # événement moteur → animation (déplacement, attaque, tir, explosion…)
        ├── sprites.py     # sprites vectoriels (aucune image externe)
        ├── hud.py         # panneau latéral, journal, boutons
        └── theme.py       # couleurs, polices
```

Principes :

- **Le moteur ne connaît pas l'affichage.** Les unités et les capacités émettent des événements (`moved`, `attacked`, `shot`, `damaged`, `died`, `rescued`, `bound`, `detonated`, `exploded`, `ticking`…) sur `events.bus`. Leurs messages texte passent par `UI`, comme en Ruby.
- **`Game` n'est pas modifié pour le mode graphique.** Il appelle `UI.ask`, `UI.choose`, `UI.request` et `UI.puts`. Le backend console lit et écrit les flux, tandis que le backend pygame affiche des dialogues modaux. `Level.play` notifie le backend au début et à la fin de chaque tour. Le backend graphique rejoue alors les événements du tour sous forme d'animations.
- **Le plateau a son propre modèle de vue.** Pendant un tour, l'état du moteur change instantanément. Le plateau garde une copie des unités, l'anime événement par événement, puis se resynchronise sur l'état réel.

## Tests

```bash
.venv/bin/pip install -e ".[dev]"
.venv/bin/python -m pytest
```

La suite de tests contient :

- le portage des specs RSpec (position, espace, étage, tour, unités, capacités, niveau, profil) ;
- le portage des scénarios Cucumber (création de profil, réussite ou échec d'un niveau, option `-s`, mode epic et notes, retour au mode normal) ;
- la résolution des 18 niveaux par des solutions de référence (`tests/fixtures/solutions/`) ;
- le mode graphique sans écran (`SDL_VIDEODRIVER=dummy`) sur de vrais niveaux, y compris l'affichage d'une erreur du joueur.

## Licence

MIT, comme le projet d'origine.
