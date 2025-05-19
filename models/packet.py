# models/packet.py

class Packet:
    def __init__(self, packet_id: int, distance: float):
        self.packet_id = packet_id
        self.distance = distance
        self.status = "Pending"  # Will be set to "Received" or "Lost"