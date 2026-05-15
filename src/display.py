from collections import Counter

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
            drone.current_zone.name for drone in self.network.drones
        )

    def draw(
        self,
        ax: Axes,
        drone_counts: Counter[str] | None = None,
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
            count = counts.get(name, 0)
            label_with_drones = f"{label}\nDrones: {count}"
            fill_color = self._zone_color(self.network.zones[name])
            ax.text(
                x_pos,
                y_pos,
                label_with_drones,
                ha="center",
                va="center",
                fontsize=10,
                color=self.readable_text_color(fill_color),
            )

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

    def show_history(self, history: list[Counter[str]]) -> None:
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
                drone_counts=history[step_index],
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

        figure.canvas.mpl_connect("key_press_event", on_key)
        render_step()
        plt.show()
