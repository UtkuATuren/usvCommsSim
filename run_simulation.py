# run_simulation.py

import simpy
import random

from models.packet import Packet

class NetworkSimulator:
    def __init__(self, env: simpy.Environment, loss_function):
        self.env = env
        self.loss_function = loss_function
        self.packet_id = 0

    def send_packet(self, distance: float) -> Packet:
        self.packet_id += 1
        packet = Packet(self.packet_id, distance)
        loss_chance = self.loss_function(distance)

        if random.random() < loss_chance:
            packet.status = "Lost"
        else:
            packet.status = "Received"

        print(
            f"Time {self.env.now}: Packet {packet.packet_id} "
            f"- Distance: {distance}m - Loss Chance: {loss_chance:.2f} "
            f"- Status: {packet.status}"
        )
        return packet

def distance_based_loss(distance: float) -> float:
    # linear 0% at 0m, 100% at 1000m
    return min(1.0, max(0.0, distance / 1000.0))

def run_simulation():
    env = simpy.Environment()
    simulator = NetworkSimulator(env, distance_based_loss)

    for distance in range(0, 1200, 100):
        simulator.send_packet(distance)

if __name__ == "__main__":
    run_simulation()