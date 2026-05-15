"""Simulation skeleton for Fly-in."""


from src.display import Display
from src.network import Network


def run_simulation(network: Network) -> list[str]:
    display = Display(network)
    display.show()
    return []
