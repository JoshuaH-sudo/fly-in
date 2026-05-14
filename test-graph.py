import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors

# Example map data from: maps/easy/02_simple_fork.txt
# Coordinates are used directly so the plot reflects map geometry.


# --- Map 1: easy/02_simple_fork.txt ---
zones1 = {
    "start": (0, 0, "green"),
    "junction": (1, 0, "yellow"),
    "path_a": (2, 1, "blue"),
    "path_b": (2, -1, "blue"),
    "goal": (3, 0, "red"),
}
connections1 = [
    ("start", "junction", 2),
    ("junction", "path_a", 1),
    ("junction", "path_b", 1),
    ("path_a", "goal", 1),
    ("path_b", "goal", 1),
]

# --- Map 2: easy/01_linear_path.txt ---
zones2 = {
    "start": (0, 0, "green"),
    "waypoint1": (1, 0, "blue"),
    "waypoint2": (2, 0, "blue"),
    "goal": (3, 0, "red"),
}
connections2 = [
    ("start", "waypoint1", 1),
    ("waypoint1", "waypoint2", 1),
    ("waypoint2", "goal", 1),
]

maps = [
    (zones1, connections1, "easy/02_simple_fork"),
    (zones2, connections2, "easy/01_linear_path"),
]


def readable_text_color(fill_color: str) -> str:
    red, green, blue = mcolors.to_rgb(fill_color)
    luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue
    return "#111111" if luminance > 0.55 else "#f5f5f5"


def draw_map(ax, zones, connections, title):
    graph = nx.DiGraph()
    graph.add_nodes_from(zones.keys())
    graph.add_weighted_edges_from(connections)
    positions = {name: (x, y) for name, (x, y, _) in zones.items()}
    node_colors = [zones[name][2] for name in graph.nodes()]
    node_sizes = [
        5400 if name in {"start", "goal"} else 4400 for name in graph
    ]
    node_labels = {name: name.replace("_", "\n") for name in graph.nodes()}
    edge_labels = {(a, b): f"cap={int(cap)}" for a, b, cap in connections}

    ax.clear()
    ax.set_facecolor("#efefef")
    nx.draw_networkx_edges(
        graph,
        positions,
        ax=ax,
        width=3.6,
        edge_color="#8e8e8e",
        arrows=True,
        arrowstyle="-|>",
        arrowsize=36,
        min_source_margin=18,
        min_target_margin=22,
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
        ax.text(
            x_pos,
            y_pos,
            node_labels[name],
            ha="center",
            va="center",
            fontsize=12,
            color=readable_text_color(zones[name][2]),
        )
    nx.draw_networkx_edge_labels(
        graph,
        positions,
        edge_labels=edge_labels,
        font_size=11,
        font_color="#444444",
        rotate=False,
        bbox={"facecolor": "#efefef", "edgecolor": "none", "pad": 0.2},
    )
    ax.grid(color="#d5d5d5", linewidth=1.2, alpha=0.8)
    ax.set_axis_on()
    ax.set_title(f"Fly-in Graph Preview ({title})", fontsize=16)
    ax.set_xlim(-0.8, 3.8)
    ax.set_ylim(-2.2, 2.2)
    plt.tight_layout()


# --- Slideshow logic ---
fig, ax = plt.subplots(figsize=(12.5, 6.5))
current = [0]  # mutable so handler can update


def show(idx):
    draw_map(ax, *maps[idx])
    fig.canvas.draw_idle()


def on_key(event):
    if event.key in ("right", "down"):  # next
        current[0] = (current[0] + 1) % len(maps)
        show(current[0])
    elif event.key in ("left", "up"):  # prev
        current[0] = (current[0] - 1) % len(maps)
        show(current[0])


fig.canvas.mpl_connect("key_press_event", on_key)
show(current[0])
plt.show()
