from collections import Counter, defaultdict
from collections.abc import Mapping

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib import colors as mcolors
from matplotlib.axes import Axes

from src.network import Network
from src.zone import Zone


class Display:
    """Render a Fly-in network graph and current drone distribution."""

    network: Network

    def __init__(self, network: Network) -> None:
        self.network = network

    def readable_text_color(self, fill_color: str) -> str:
        """Return high-contrast text color for a given node fill color."""
        red, green, blue = mcolors.to_rgb(fill_color)
        luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue
        return "#111111" if luminance > 0.55 else "#f5f5f5"

    def _zone_color(self, zone: Zone) -> str:
        """Resolve a matplotlib-safe display color for a zone."""
        candidate = zone.color if zone.color is not None else "#9aa0a6"
        try:
            mcolors.to_rgb(candidate)
            return candidate
        except ValueError:
            return "#9aa0a6"

    def _drone_counts(self) -> Counter[str]:
        """Count how many drones are currently in each zone."""
        return Counter(
            drone.current_pos.name for drone in self.network.drones
        )

    def _drone_label(self, drone_name: str) -> str:
        """Format an internal drone name as user-facing label D n."""
        if drone_name.startswith("drone_"):
            return f"D{drone_name.split('_', maxsplit=1)[1]}"
        return drone_name

    def _draw_drones(
        self,
        ax: Axes,
        positions: Mapping[str, tuple[float | int, float | int]],
        drone_positions: Mapping[str, str] | None = None,
    ) -> None:
        """Draw each drone as a small diamond around its current zone."""
        drones_by_zone: dict[str, list[str]] = defaultdict(list)
        if drone_positions is None:
            for drone in self.network.drones:
                drones_by_zone[drone.current_pos.name].append(drone.name)
        else:
            for drone_name, zone_name in drone_positions.items():
                drones_by_zone[zone_name].append(drone_name)

        for zone_name, drone_names in drones_by_zone.items():
            x_pos, y_pos = positions[zone_name]
            count = len(drone_names)
            sorted_names = sorted(drone_names)

            if count == 1:
                placements = [(x_pos, y_pos, sorted_names[0])]
            else:
                cols = min(3, count)
                rows = (count + cols - 1) // cols
                spacing = 0.18
                start_x = x_pos - spacing * (cols - 1) / 2
                start_y = y_pos + spacing * (rows - 1) / 2
                placements = []
                for index, drone_name in enumerate(sorted_names):
                    row = index // cols
                    col = index % cols
                    drone_x = start_x + col * spacing
                    drone_y = start_y - row * spacing
                    placements.append((drone_x, drone_y, drone_name))

            for drone_x, drone_y, drone_name in placements:

                ax.scatter(
                    drone_x,
                    drone_y,
                    s=200,
                    marker="D",
                    c="#ffffff",
                    edgecolors="#1f1f1f",
                    linewidths=1.5,
                    zorder=5,
                )
                ax.text(
                    drone_x,
                    drone_y,
                    self._drone_label(drone_name),
                    ha="center",
                    va="center",
                    fontsize=8,
                    color="#111111",
                    zorder=6,
                )

    def draw(
        self,
        ax: Axes,
        drone_counts: Counter[str] | None = None,
        drone_positions: Mapping[str, str] | None = None,
        title: str = "Fly-in Graph Preview",
    ) -> None:
        """Draw the network graph and drone counts on a matplotlib axis."""
        graph = nx.DiGraph()
        graph.add_nodes_from(self.network.zones.keys())

        for connection in self.network.connections:
            graph.add_edge(
                connection.zone_a,
                connection.zone_b,
                weight=connection.max_link_capacity,
            )
            graph.add_edge(
                connection.zone_b,
                connection.zone_a,
                weight=connection.max_link_capacity,
            )

        positions = {
            zone.name: (zone.x, zone.y) for zone in self.network.zones.values()
        }
        node_colors = [
            self._zone_color(self.network.zones[name])
            for name in graph.nodes()
        ]
        node_sizes = [
            (
                6000
                if name
                in {
                    self.network.start_hub,
                    self.network.end_hub,
                }
                else 4600
            )
            for name in graph.nodes()
        ]
        counts = (
            drone_counts if drone_counts is not None else self._drone_counts()
        )

        edge_labels = {
            (zone_a, zone_b): f"cap={int(data['weight'])}"
            for zone_a, zone_b, data in graph.edges(data=True)
            if zone_a < zone_b
        }

        ax.clear()
        ax.set_facecolor("#efefef")
        nx.draw_networkx_edges(
            graph,
            positions,
            ax=ax,
            width=3.2,
            edge_color="#8e8e8e",
            arrows=True,
            arrowstyle="-|>",
            arrowsize=24,
            min_source_margin=16,
            min_target_margin=20,
            alpha=0.8,
        )
        nx.draw_networkx_nodes(
            graph,
            positions,
            ax=ax,
            node_size=node_sizes,
            node_color=node_colors,
            edgecolors="#303030",
            linewidths=3,
        )

        for name, (x_pos, y_pos) in positions.items():
            label = name.replace("_", "\n")
            label_text = (
                f"{label}\nDrones: {counts.get(name, 0)}"
                if drone_counts is not None and drone_positions is None
                else label
            )
            fill_color = self._zone_color(self.network.zones[name])
            ax.text(
                x_pos,
                y_pos,
                label_text,
                ha="center",
                va="center",
                fontsize=10,
                color=self.readable_text_color(fill_color),
            )

        if drone_positions is not None:
            self._draw_drones(ax, positions, drone_positions=drone_positions)
        elif drone_counts is None:
            self._draw_drones(ax, positions)

        nx.draw_networkx_edge_labels(
            graph,
            positions,
            edge_labels=edge_labels,
            font_size=10,
            font_color="#444444",
            rotate=False,
            bbox={"facecolor": "#efefef", "edgecolor": "none", "pad": 0.2},
        )

        ax.grid(color="#d5d5d5", linewidth=1.2, alpha=0.8)
        ax.set_axis_on()
        ax.set_title(title, fontsize=16)

    def show(self) -> None:
        """Open a matplotlib window with the current network rendering."""
        _, ax = plt.subplots(figsize=(12.5, 6.5))
        self.draw(ax)
        plt.tight_layout()
        plt.show()

    def show_history(self, history: list[dict[str, str]]) -> None:
        """Render a turn history and browse with arrow keys."""
        if not history:
            return

        figure, ax = plt.subplots(figsize=(12.5, 6.5))
        current = [0]
        total_steps = len(history)

        def render_step() -> None:
            step_index = current[0]
            self.draw(
                ax,
                drone_positions=history[step_index],
                title=(
                    "Fly-in Graph Preview "
                    f"(Step {step_index}/{total_steps - 1}, "
                    "Left/Right to navigate)"
                ),
            )
            figure.tight_layout()
            figure.canvas.draw_idle()

        def on_key(event: object) -> None:
            key = getattr(event, "key", None)
            if key in ("right", "down"):
                current[0] = min(current[0] + 1, total_steps - 1)
                render_step()
            elif key in ("left", "up"):
                current[0] = max(current[0] - 1, 0)
                render_step()
            elif key in ("escape", "enter"):
                plt.close(figure)

        figure.canvas.mpl_connect("key_press_event", on_key)
        render_step()
        plt.show()
