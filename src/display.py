from src.network import Network


class Display:
    network: Network

    def __init__(self, network: Network):
        self.network = network
