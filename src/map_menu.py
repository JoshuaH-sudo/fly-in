"""Interactive map selection menu based on the maps folder structure."""

import os
import sys
from dataclasses import dataclass
from simple_term_menu import TerminalMenu


@dataclass(frozen=True)
class MapOption:
    label: str
    path: str


class MapMenu:
    """Builds and displays a map selection menu from folders under maps/."""

    _CATEGORY_ORDER = ["easy", "medium", "hard", "challenger"]

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

    def _ordered_categories(
        self,
        by_category: dict[str, list[MapOption]],
    ) -> list[str]:
        ordered = [
            category
            for category in self._CATEGORY_ORDER
            if category in by_category
        ]
        ordered.extend(
            sorted(
                category
                for category in by_category
                if category not in self._CATEGORY_ORDER
            )
        )
        return ordered

    def _choose_with_numeric_prompt(
        self,
        ordered_categories: list[str],
        by_category: dict[str, list[MapOption]],
    ) -> str | None:
        print("Map categories:")
        for index, category in enumerate(ordered_categories, start=1):
            count = len(by_category[category])
            print(f"  {index:>2}. {category} ({count} maps)")

        while True:
            raw_choice = input(
                "Select a category number (or q to quit): "
            ).strip()
            if raw_choice.lower() in {"q", "quit", "exit"}:
                return None
            if not raw_choice.isdigit():
                print("Invalid input. Enter a number or q to quit.")
                continue

            selected_index = int(raw_choice)
            if 1 <= selected_index <= len(ordered_categories):
                selected_category = ordered_categories[selected_index - 1]
                break
            print("Category choice out of range. Try again.")

        selected_options = sorted(
            by_category[selected_category],
            key=lambda option: option.label,
        )

        print(f"Maps in {selected_category}:")
        for index, option in enumerate(selected_options, start=1):
            file_name = option.label.split("/", maxsplit=1)[1]
            print(f"  {index:>2}. {file_name}")

        while True:
            raw_choice = input("Select a map number (or q to quit): ").strip()
            if raw_choice.lower() in {"q", "quit", "exit"}:
                return None
            if not raw_choice.isdigit():
                print("Invalid input. Enter a number or q to quit.")
                continue

            selected_index = int(raw_choice)
            if 1 <= selected_index <= len(selected_options):
                return selected_options[selected_index - 1].path
            print("Map choice out of range. Try again.")

    def _choose_with_terminal_menu(
        self,
        ordered_categories: list[str],
        by_category: dict[str, list[MapOption]],
    ) -> str | None:

        category_entries = [
            f"{category} ({len(by_category[category])} maps)"
            for category in ordered_categories
        ]
        category_menu = TerminalMenu(
            category_entries,
            title="Select map category",
            cycle_cursor=True,
        )
        selected_category_choice = category_menu.show()
        if selected_category_choice is None:
            return None
        if isinstance(selected_category_choice, tuple):
            if not selected_category_choice:
                return None
            selected_category_index = selected_category_choice[0]
        else:
            selected_category_index = selected_category_choice

        selected_category = ordered_categories[selected_category_index]
        selected_options = sorted(
            by_category[selected_category],
            key=lambda option: option.label,
        )

        map_entries = [
            option.label.split("/", maxsplit=1)[1]
            for option in selected_options
        ]
        map_menu = TerminalMenu(
            map_entries,
            title=f"Select map in {selected_category}",
            cycle_cursor=True,
        )
        selected_map_choice = map_menu.show()
        if selected_map_choice is None:
            return None
        if isinstance(selected_map_choice, tuple):
            if not selected_map_choice:
                return None
            selected_map_index = selected_map_choice[0]
        else:
            selected_map_index = selected_map_choice

        return selected_options[selected_map_index].path

    def choose_map(self, options: list[MapOption]) -> str | None:
        if not options:
            return None

        if not sys.stdin.isatty():
            return options[0].path

        by_category: dict[str, list[MapOption]] = {}
        for option in options:
            category, _, _ = option.label.partition("/")
            by_category.setdefault(category, []).append(option)

        ordered_categories = self._ordered_categories(by_category)

        try:
            return self._choose_with_terminal_menu(
                ordered_categories,
                by_category,
            )
        except (ImportError, OSError):
            return self._choose_with_numeric_prompt(
                ordered_categories,
                by_category,
            )
