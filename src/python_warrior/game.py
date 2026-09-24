"""Game flow: profiles, normal mode and epic mode (port of RubyWarrior::Game)."""

import glob
import os
import sys

from .config import Config
from .level import Level
from .profile import Profile
from .tower import Tower
from .ui import UI
from .utils import hard_wrap


class Game:
    def __init__(self):
        self._profile = None
        self._current_level = None
        self._next_level = None

    def start(self):
        UI.puts("Welcome to Python Warrior")

        profile_file = os.path.join(Config.path_prefix, ".profile")
        if os.path.exists(profile_file):
            self._profile = Profile.load(profile_file)
        elif not os.path.exists(os.path.join(Config.path_prefix, "pywarrior")):
            self.make_game_directory()

        if self.profile.is_epic():
            if self.profile.is_level_after_epic():
                self.go_back_to_normal_mode()
            else:
                self.play_epic_mode()
        else:
            self.play_normal_mode()

    def make_game_directory(self):
        if UI.ask("No pywarrior directory found, would you like to create one?"):
            os.mkdir(os.path.join(Config.path_prefix, "pywarrior"))
        else:
            UI.puts("Unable to continue without directory.")
            sys.exit()

    def play_epic_mode(self):
        if Config.delay:
            Config.delay /= 2  # speed up UI since we're going to be doing a lot here
        self.profile.current_epic_score = 0
        self.profile.current_epic_grades = {}
        if Config.practice_level:
            self._current_level = self._next_level = None
            self.profile.level_number = Config.practice_level
            self.play_current_level()
        else:
            playing = True
            while playing:
                self._current_level = self._next_level = None
                self.profile.level_number += 1
                playing = self.play_current_level()
            self.profile.save()  # saves the score for epic mode

    def play_normal_mode(self):
        if Config.practice_level:
            UI.puts("Unable to practice level while not in epic mode, remove -l option.")
        elif self.current_level.number == 0:
            self.prepare_next_level()
            UI.puts(
                "First level has been generated. "
                f"See the pywarrior/{self.profile.directory_name}/README for instructions."
            )
        else:
            self.play_current_level()

    def play_current_level(self):
        cont = True
        self.current_level.load_player()
        UI.puts(f"Starting Level {self.current_level.number}")
        self.current_level.play()
        if self.current_level.passed():
            if self.next_level.exists():
                UI.puts("Success! You have found the stairs.")
            else:
                UI.puts(
                    "CONGRATULATIONS! You have climbed to the top of the tower "
                    "and rescued the fair maiden Ruby."
                )
                cont = False
            self.current_level.tally_points()
            if self.profile.is_epic():
                if self.final_report() and not cont:
                    UI.puts(self.final_report())
            else:
                self.request_next_level()
        else:
            cont = False
            UI.puts(
                f"Sorry, you failed level {self.current_level.number}. "
                "Change your script and try again."
            )
            if (
                not Config.skip_input
                and self.current_level.clue
                and UI.ask("Would you like to read the additional clues for this level?")
            ):
                UI.puts(hard_wrap(self.current_level.clue))
        return cont

    def request_next_level(self):
        if Config.skip_input:
            UI.puts("Staying on current level. Remove --skip option to continue on to the next level.")
        elif UI.ask(
            "Would you like to continue on to the next level?"
            if self.next_level.exists()
            else "Would you like to continue on to epic mode?"
        ):
            if self.next_level.exists():
                self.prepare_next_level()
                UI.puts(f"See the updated README in the pywarrior/{self.profile.directory_name} directory.")
            else:
                self.prepare_epic_mode()
                UI.puts("Run pywarrior again to play epic mode.")
        else:
            UI.puts("Staying on current level.")

    def prepare_next_level(self):
        self.next_level.generate_player_files()
        self.profile.level_number += 1
        self.profile.save()  # this saves score and new abilities too

    def prepare_epic_mode(self):
        self.profile.enable_epic_mode()
        self.profile.level_number = 0
        self.profile.save()  # this saves score too

    def go_back_to_normal_mode(self):
        self.profile.enable_normal_mode()
        self.prepare_next_level()
        UI.puts("Another level has been added since you started epic, going back to normal mode.")
        UI.puts(f"See the updated README in the pywarrior/{self.profile.directory_name} directory.")

    # profiles

    def profiles(self):
        return [Profile.load(path) for path in self.profile_paths()]

    def profile_paths(self):
        pattern = os.path.join(Config.path_prefix, "pywarrior", "**", ".profile")
        return sorted(glob.glob(pattern, recursive=True))

    @property
    def profile(self):
        if self._profile is None:
            self._profile = self._choose_profile()
        return self._profile

    def new_profile(self):
        profile = Profile()
        profile.tower_path = UI.choose("tower", self.towers()).path
        profile.warrior_name = UI.request("Enter a name for your warrior: ")
        return profile

    # towers

    def towers(self):
        return [Tower(os.path.basename(path)) for path in self.tower_paths()]

    def tower_paths(self):
        return sorted(p for p in glob.glob(os.path.join(Config.towers_dir(), "*")) if os.path.isdir(p)
                      and not os.path.basename(p).startswith("_"))

    # levels

    @property
    def current_level(self):
        if self._current_level is None:
            self._current_level = self.profile.current_level
        return self._current_level

    @property
    def next_level(self):
        if self._next_level is None:
            self._next_level = self.profile.next_level
        return self._next_level

    def final_report(self):
        average = self.profile.calculate_average_grade()
        if average and not Config.practice_level:
            report = f"Your average grade for this tower is: {Level.grade_letter(average)}\n\n"
            for level in sorted(self.profile.current_epic_grades):
                grade = Level.grade_letter(self.profile.current_epic_grades[level])
                report += f"  Level {level}: {grade}\n"
            report += "\nTo practice a level, use the -l option:\n\n  pywarrior -l 3"
            return report
        return None

    def _choose_profile(self):
        profile = UI.choose("profile", self.profiles() + [("new", "New Profile")])
        if profile == "new":
            profile = self.new_profile()
            if any(p.player_path == profile.player_path for p in self.profiles()):
                if UI.ask("Are you sure you want to replace your existing profile for this tower?"):
                    UI.puts("Replacing existing profile.")
                else:
                    UI.puts("Not replacing profile.")
                    sys.exit()
        return profile
