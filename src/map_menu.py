"""Interactive map selection menu based on the maps folder structure."""

import os
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class MapOption:
    label: str
    path: str


class MapMenu:
    """Builds and displays a map selection menu from folders under maps/."""

    def __init__(self, maps_dir: str) -> None:
        self.maps_dir = maps_dir

    def discover_options(self) -> list[MapOption]:
        options: list[MapOption] = []
        if not os.path.isdir(self.maps_dir):
            return options

        categories = sorted(
            name
            for name in os.listdir(self.maps_dir)
            if os.path.isdir(os.path.join(self.maps_dir, name))
        )

        for category in categories:
            category_path = os.path.join(self.maps_dir, category)
            for file_name in sorted(os.listdir(category_path)):
                if not file_name.endswith(".txt"):
                    continue
                rel_label = f"{category}/{file_name}"
                full_path = os.path.join(category_path, file_name)
                options.append(MapOption(label=rel_label, path=full_path))

        return options

    def choose_map(self, options: list[MapOption]) -> str | None:
        if not options:
            return None

        if not sys.stdin.isatty():
            return options[0].path

        print("Available maps:")
        for index, option in enumerate(options, start=1):
            print(f"  {index:>2}. {option.label}")

        while True:
            raw_choice = input("Select a map number (or q to quit): ").strip()
            if raw_choice.lower() in {"q", "quit", "exit"}:
                return None
            if not raw_choice.isdigit():
                print("Invalid input. Enter a number or q to quit.")
                continue

            selected_index = int(raw_choice)
            if 1 <= selected_index <= len(options):
                return options[selected_index - 1].path
            print("Choice out of range. Try again.")
