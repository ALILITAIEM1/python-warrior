"""Command line entry point (port of RubyWarrior::Runner)."""

import argparse
import sys

from .config import Config
from .game import Game


def parse_options(arguments):
    parser = argparse.ArgumentParser(prog="pywarrior", description="Python Warrior")
    parser.add_argument("-d", "--directory", metavar="DIR", help="Run under given directory")
    parser.add_argument("-l", "--level", type=int, metavar="LEVEL", help="Practice level on epic")
    parser.add_argument("-s", "--skip", action="store_true", help="Skip user input")
    parser.add_argument("-t", "--time", type=float, metavar="SECONDS", help="Delay each turn by seconds")
    parser.add_argument("-g", "--gui", action="store_true", help="Play with the 2D graphical interface")
    return parser.parse_args(arguments)


def run(arguments, stdin=sys.stdin, stdout=sys.stdout):
    Config.in_stream = stdin
    Config.out_stream = stdout
    Config.delay = 0.6
    options = parse_options(arguments)
    if options.directory:
        Config.path_prefix = options.directory
    if options.level:
        Config.practice_level = options.level
    if options.skip:
        Config.skip_input = True
    if options.time is not None:
        Config.delay = options.time
    if options.gui:
        from .ui.graphics2d.app import run_gui

        run_gui(Game)
    else:
        Game().start()


def main():
    try:
        run(sys.argv[1:])
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()
