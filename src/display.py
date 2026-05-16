from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
import math

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib import colors as mcolors
from matplotlib.axes import Axes

from src.network import Network
from src.types import DronePositionsView
from src.utils.drone_labels import drone_label
from src.zone import Zone


class Display:
    """Render a Fly-in network graph and current drone distribution."""

    network: Network

    def __init__(self, network: Network) -> None:
        """Initialize the renderer with a parsed network.

        Args:
            network: Network to visualize.
        """
        self.network = network

    def readable_text_color(self, fill_color: str) -> str:
        """Return high-contrast text color for a node fill color.

        Args:
            fill_color: Matplotlib-compatible fill color value.

        Returns:
            Dark or light text color optimized for readability.
        """
        red, green, blue = mcolors.to_rgb(fill_color)
        luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue
        return "#111111" if luminance > 0.55 else "#f5f5f5"

    def _zone_color(self, zone: Zone) -> str:
        """Resolve a matplotlib-safe display color for a zone.

        Args:
            zone: Zone whose color metadata should be resolved.

        Returns:
            Valid matplotlib color token.
        """
        candidate = zone.color if zone.color is not None else "#9aa0a6"
        try:
            mcolors.to_rgb(candidate)
            return candidate
        except ValueError:
            return "#9aa0a6"

    def _drone_counts(self) -> Counter[str]:
        """Count how many drones are currently in each zone.

        Returns:
            Counter keyed by zone name.
        """
        return Counter(
            drone.current_pos.name for drone in self.network.drones
        )

    def _draw_drones(
        self,
        ax: Axes,
        positions: Mapping[str, tuple[float | int, float | int]],
        node_sizes: Mapping[str, float | int],
        drone_positions: DronePositionsView | None = None,
    ) -> None:
        """Draw drones in compact clusters anchored to each zone center.

        Args:
            ax: Target axes used for drawing.
            positions: Zone positions in data coordinates.
            node_sizes: Per-zone node marker sizes.
            drone_positions: Optional per-drone snapshot for one history step.

        Returns:
            None.
        """
        drones_by_zone: dict[str, list[str]] = defaultdict(list)
        if drone_positions is None:
            for drone in self.network.drones:
                drones_by_zone[drone.current_pos.name].append(drone.name)
        else:
            for drone_name, zone_name in drone_positions.items():
                drones_by_zone[zone_name].append(drone_name)

        def data_from_pixel_offset(
            x_center: float | int,
            y_center: float | int,
            dx_px: float,
            dy_px: float,
        ) -> tuple[float, float]:
            # Work in pixel space so drone spacing stays visually consistent
            # regardless of axis limits or map coordinate scale.
            base_px = ax.transData.transform((x_center, y_center))
            target_px = (base_px[0] + dx_px, base_px[1] + dy_px)
            data_x, data_y = ax.transData.inverted().transform(target_px)
            return float(data_x), float(data_y)

        def layout_offsets(
            count: int,
            zone_size: float,
        ) -> list[tuple[float, float]]:
            if count <= 0:
                return []
            if count == 1:
                return [(0.0, 0.0)]

            node_radius_pt = math.sqrt(zone_size / math.pi)
            px_per_pt = ax.figure.dpi / 72.0
            max_radius_px = node_radius_pt * px_per_pt * 0.78
            drone_radius_pt = max(4.6, min(9.2, node_radius_pt / 2.7))
            min_sep_px = (2.0 * drone_radius_pt * px_per_pt) * 1.03
            ring_step_px = max(min_sep_px * 0.88, 9.0)

            offsets: list[tuple[float, float]] = []
            if count % 2 == 1:
                offsets.append((0.0, 0.0))

            ring_index = 1
            while len(offsets) < count:
                radius_px = ring_index * ring_step_px
                ring_capacity = max(
                    6,
                    int((2.0 * math.pi * radius_px) / max(min_sep_px, 1.0)),
                )
                slots = min(ring_capacity, count - len(offsets))
                for slot in range(slots):
                    angle = (2.0 * math.pi * slot / slots) - (math.pi / 2.0)
                    offsets.append(
                        (
                            radius_px * math.cos(angle),
                            radius_px * math.sin(angle),
                        )
                    )
                ring_index += 1

            furthest = max(
                math.hypot(x_off, y_off) for x_off, y_off in offsets
            )
            if furthest > max_radius_px > 0:
                # Scale the cluster back into the node to avoid drifting away
                # when many drones share one zone.
                scale = max_radius_px / furthest
                offsets = [
                    (x_off * scale, y_off * scale)
                    for x_off, y_off in offsets
                ]

            return offsets

        for zone_name, drone_names in drones_by_zone.items():
            x_pos, y_pos = positions[zone_name]
            count = len(drone_names)
            sorted_names = sorted(drone_names)
            zone_size = float(node_sizes.get(zone_name, 4600))
            node_radius_pt = math.sqrt(zone_size / math.pi)
            drone_radius_pt = max(4.6, min(9.2, node_radius_pt / 2.7))
            drone_marker_size = math.pi * (drone_radius_pt**2)
            offsets = layout_offsets(count, zone_size)

            placements: list[tuple[float, float, str]] = []
            for drone_name, (x_off, y_off) in zip(sorted_names, offsets):
                drone_x, drone_y = data_from_pixel_offset(
                    x_pos,
                    y_pos,
                    x_off,
                    y_off,
                )
                placements.append((drone_x, drone_y, drone_name))

            for drone_x, drone_y, drone_name in placements:
                ax.scatter(
                    drone_x,
                    drone_y,
                    s=drone_marker_size,
                    marker="D",
                    c="#ffffff",
                    edgecolors="#1f1f1f",
                    linewidths=1.5,
                    zorder=5,
                )
                ax.text(
                    drone_x,
                    drone_y,
                    drone_label(drone_name),
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
        drone_positions: DronePositionsView | None = None,
        title: str = "Fly-in Graph Preview",
    ) -> None:
        """Draw the network graph and drone overlays on a matplotlib axis.

        Args:
            ax: Target axes used for drawing.
            drone_counts: Optional precomputed zone-level drone counts.
            drone_positions: Optional per-drone positions snapshot.
            title: Figure title shown above the graph.

        Returns:
            None.
        """
        graph: nx.DiGraph[str] = nx.DiGraph()
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
        node_sizes_by_name = dict(zip(graph.nodes(), node_sizes))
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
            self._draw_drones(
                ax,
                positions,
                node_sizes_by_name,
                drone_positions=drone_positions,
            )
        elif drone_counts is None:
            self._draw_drones(ax, positions, node_sizes_by_name)

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
        """Open a matplotlib window with the current network rendering.

        Returns:
            None.
        """
        _, ax = plt.subplots(figsize=(12.5, 6.5))
        self.draw(ax)
        plt.tight_layout()
        plt.show()

    def show_history(self, history: Sequence[DronePositionsView]) -> None:
        """Render a turn history and browse with keyboard arrows.

        Args:
            history: Ordered drone-position snapshots.

        Returns:
            None.
        """
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
