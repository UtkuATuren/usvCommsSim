"""
Test script for physics-based underwater acoustic communication model integration.
This demonstrates the replacement of hard-coded success probabilities with physics-based calculations.
"""

import math
import random
from models.communication_model import UnderwaterCommunicationModel
from models.acoustic_config import (
    DEFAULT_CONFIG, SHALLOW_WATER_CONFIG, DEEP_WATER_CONFIG, 
    HIGH_NOISE_CONFIG, LOW_POWER_CONFIG
)

def test_physics_model_comparison():
    """Compare physics-based model with different configurations"""
    
    print("=== Physics-Based Underwater Acoustic Communication Test ===\n")
    
    # Test scenarios
    scenarios = [
        ("Default Configuration", DEFAULT_CONFIG),
        ("Shallow Water", SHALLOW_WATER_CONFIG),
        ("Deep Water", DEEP_WATER_CONFIG), 
        ("High Noise Environment", HIGH_NOISE_CONFIG),
        ("Low Power Operation", LOW_POWER_CONFIG)
    ]
    
    # Test distances and packet sizes
    test_distances = [50, 100, 200, 500, 1000, 2000]  # meters
    test_packet_sizes = [16, 50, 100, 200]  # bytes
    
    # Fixed positions for testing
    ship_pos = (0.0, 0.0, 5.0)  # surface ship at 5m depth
    
    for scenario_name, config in scenarios:
        print(f"\n--- {scenario_name} ---")
        print(f"Frequency: {config.frequency_hz/1000:.1f} kHz")
        print(f"Power: {config.transmission_power_db} dB")
        print(f"Noise: {config.noise_level_db} dB")
        print(f"Required SNR: {config.required_snr_db} dB")
        print(f"Spreading exponent: {config.spreading_exponent}")
        print()
        
        # Create communication model with this configuration
        comm_model = UnderwaterCommunicationModel(config)
        
        print("Distance (m) | Packet Size (B) | Loss Prob | Reason")
        print("-" * 55)
        
        for distance in test_distances:
            sub_pos = (distance, 0.0, 50.0)  # submarine at 50m depth
            
            # Test with different packet sizes
            for packet_size in test_packet_sizes:
                loss_prob, reason = comm_model.calculate_packet_loss_probability(
                    distance, ship_pos[2], sub_pos[2], packet_size
                )
                
                print(f"{distance:8d} | {packet_size:11d} | {loss_prob:8.3f} | {reason}")
        
        print()

def demonstrate_transmission_simulation():
    """Demonstrate complete packet transmission simulation"""
    
    print("\n=== Packet Transmission Simulation Demonstration ===\n")
    
    # Use default configuration
    comm_model = UnderwaterCommunicationModel(DEFAULT_CONFIG)
    
    # Fixed random seed for reproducible results
    random.seed(42)
    
    # Simulate multiple transmissions at different distances
    ship_pos = (0.0, 0.0, 5.0)
    packet_types = ["command", "status"]
    
    print("Simulating 20 packet transmissions...")
    print("Distance (m) | Type    | Size | Success | Delay (ms) | Reason")
    print("-" * 65)
    
    successful_transmissions = 0
    total_transmissions = 0
    
    for i in range(20):
        # Vary distance and packet type
        distance = 100 + (i * 50)  # 100m to 1050m
        sub_pos = (distance, 0.0, 30.0 + (i * 2))  # varying depth
        packet_type = packet_types[i % 2]
        packet_size = 16 if packet_type == "command" else 50
        
        # Simulate transmission
        transmission = comm_model.simulate_transmission(
            sender="ship",
            receiver="submarine", 
            packet_type=packet_type,
            data_size=packet_size,
            ship_pos=ship_pos,
            sub_pos=sub_pos
        )
        
        total_transmissions += 1
        success = "YES" if transmission.is_received else "NO"
        delay_ms = transmission.total_delay * 1000 if transmission.is_received else 0
        reason = transmission.loss_reason if transmission.is_lost else "delivered"
        
        if transmission.is_received:
            successful_transmissions += 1
        
        print(f"{distance:8d} | {packet_type:7s} | {packet_size:4d} | {success:7s} | {delay_ms:8.2f} | {reason}")
    
    success_rate = (successful_transmissions / total_transmissions) * 100
    print(f"\nOverall Success Rate: {successful_transmissions}/{total_transmissions} ({success_rate:.1f}%)")

def compare_old_vs_new_approach():
    """Compare the physics-based approach with a simulated old approach"""
    
    print("\n=== Comparison: Physics-Based vs Hard-Coded Approach ===\n")
    
    # Physics-based model
    physics_model = UnderwaterCommunicationModel(DEFAULT_CONFIG)
    
    # Test distance
    distance = 500  # meters
    ship_pos = (0.0, 0.0, 5.0)
    sub_pos = (distance, 0.0, 50.0)
    packet_size = 50
    
    # Get physics-based loss probability
    physics_loss_prob, physics_reason = physics_model.calculate_packet_loss_probability(
        distance, ship_pos[2], sub_pos[2], packet_size
    )
    
    # Simulate old hard-coded approach (example)
    hardcoded_success_prob = 0.9  # The old fixed probability
    hardcoded_loss_prob = 1.0 - hardcoded_success_prob
    
    print(f"Test Scenario: {distance}m distance, {packet_size} byte packet")
    print(f"Ship at {ship_pos[2]}m depth, Submarine at {sub_pos[2]}m depth")
    print()
    print("Hard-coded approach:")
    print(f"  Fixed success probability: {hardcoded_success_prob:.3f}")
    print(f"  Fixed loss probability: {hardcoded_loss_prob:.3f}")
    print(f"  Reason: fixed_value")
    print()
    print("Physics-based approach:")
    print(f"  Calculated success probability: {1.0 - physics_loss_prob:.3f}")
    print(f"  Calculated loss probability: {physics_loss_prob:.3f}")
    print(f"  Reason: {physics_reason}")
    print()
    
    # Show configuration details
    config_summary = physics_model.physics_config.get_configuration_summary()
    print("Physics model parameters:")
    print(f"  Frequency: {config_summary['frequency']['khz']:.1f} kHz")
    print(f"  Source power: {config_summary['power_levels']['transmission_power_db']:.1f} dB")
    print(f"  Noise level: {config_summary['power_levels']['noise_level_db']:.1f} dB")
    print(f"  Required SNR: {config_summary['power_levels']['required_snr_db']:.1f} dB")
    print(f"  Spreading exponent: {config_summary['propagation']['spreading_exponent']}")

if __name__ == "__main__":
    # Run all tests
    test_physics_model_comparison()
    demonstrate_transmission_simulation()
    compare_old_vs_new_approach()
    
    print("\n=== Integration Complete ===")
    print("The physics-based model is now fully integrated!")
    print("Key benefits:")
    print("- Realistic acoustic propagation modeling")
    print("- Distance-dependent loss calculations") 
    print("- Frequency-dependent absorption (Thorp's formula)")
    print("- Configurable spreading exponents and noise levels")
    print("- Rayleigh fading statistical model")
    print("- Packet size effects")
    print("- Same random number generation for consistent seeding") 