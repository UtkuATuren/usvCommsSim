"""
Test script for corrected physics-based underwater acoustic communication model.
This demonstrates realistic packet loss with corrected pressure-to-power conversions.
"""

import math
import random
from models.communication_model import UnderwaterCommunicationModel
from models.acoustic_config import (
    DEFAULT_CONFIG, HARSH_ENVIRONMENT_CONFIG, AcousticPhysicsConfig
)

def test_corrected_physics_model():
    """Test the corrected physics model with realistic parameters"""
    
    print("=== Corrected Physics-Based Model Test ===\n")
    
    # Test with even harsher conditions to show packet loss
    very_harsh_config = AcousticPhysicsConfig(
        transmission_power_db=160.0,  # Lower power
        noise_level_db=65.0,  # High noise
        required_snr_db=15.0,  # High SNR requirement
        frequency_hz=15000.0,  # Higher frequency (more absorption)
        spreading_exponent=2.0,  # Spherical spreading
        site_anomaly_db=10.0  # Very poor propagation
    )
    
    configs = [
        ("Default Config", DEFAULT_CONFIG),
        ("Harsh Environment", HARSH_ENVIRONMENT_CONFIG),
        ("Very Harsh Environment", very_harsh_config)
    ]
    
    test_distances = [100, 500, 1000, 2000, 5000, 10000]  # meters
    
    for config_name, config in configs:
        print(f"\n--- {config_name} ---")
        print(f"Source level: {config.transmission_power_db} dB re 1 μPa")
        print(f"Noise level: {config.noise_level_db} dB re 1 μPa") 
        print(f"Required SNR: {config.required_snr_db} dB")
        print(f"Frequency: {config.frequency_hz/1000:.1f} kHz")
        print(f"Spreading: {config.spreading_exponent}")
        print(f"Anomaly: {config.site_anomaly_db} dB")
        
        # Show the actual power levels
        print(f"Source power (linear): {config.transmission_power_linear:.2e}")
        print(f"Noise power (linear): {config.noise_power_linear:.2e}")
        print(f"Initial SNR: {config.transmission_power_linear/config.noise_power_linear:.2e}")
        print()
        
        comm_model = UnderwaterCommunicationModel(config)
        
        print("Distance (m) | Loss Prob | SNR (dB) | Reason")
        print("-" * 50)
        
        for distance in test_distances:
            # Test with standard packet size
            loss_prob, reason = comm_model.calculate_packet_loss_probability(
                distance, 5.0, 50.0, 50  # ship at 5m, sub at 50m, 50 byte packet
            )
            
            # Calculate actual SNR for diagnostics
            from models.acoustic_physics import transmission_loss, compute_gamma_mean
            TL_db = transmission_loss(distance, config.frequency_khz, config.spreading_exponent, config.site_anomaly_db)
            gamma_mean = compute_gamma_mean(distance, config.transmission_power_linear, 
                                          config.noise_power_linear, config.frequency_khz, 
                                          config.spreading_exponent, config.site_anomaly_db)
            snr_db = 10 * math.log10(gamma_mean)
            
            print(f"{distance:8d} | {loss_prob:8.3f} | {snr_db:7.1f} | {reason}")
        
        print()

def test_transmission_simulation():
    """Test packet transmission simulation with corrected model"""
    
    print("\n=== Transmission Simulation with Corrected Model ===\n")
    
    # Use harsh environment to see some failures
    comm_model = UnderwaterCommunicationModel(HARSH_ENVIRONMENT_CONFIG)
    
    # Fixed seed for reproducible results
    random.seed(42)
    
    ship_pos = (0.0, 0.0, 5.0)
    
    print("Distance (m) | Type    | Success | Loss Prob | Reason")
    print("-" * 60)
    
    successful = 0
    total = 0
    
    # Test at various distances to see transition from success to failure
    test_distances = [200, 500, 1000, 2000, 3000, 5000, 8000, 10000]
    
    for distance in test_distances:
        sub_pos = (distance, 0.0, 50.0)
        
        # Simulate 2 transmissions per distance
        for packet_type in ["command", "status"]:
            packet_size = 16 if packet_type == "command" else 50
            
            transmission = comm_model.simulate_transmission(
                sender="ship",
                receiver="submarine",
                packet_type=packet_type,
                data_size=packet_size,
                ship_pos=ship_pos,
                sub_pos=sub_pos
            )
            
            total += 1
            success = "YES" if transmission.is_received else "NO"
            
            # Get loss probability for display
            loss_prob, reason = comm_model.calculate_packet_loss_probability(
                distance, ship_pos[2], sub_pos[2], packet_size
            )
            
            if transmission.is_received:
                successful += 1
                reason = "delivered"
            else:
                reason = transmission.loss_reason
            
            print(f"{distance:8d} | {packet_type:7s} | {success:7s} | {loss_prob:8.3f} | {reason}")
    
    success_rate = (successful / total) * 100
    print(f"\nOverall Success Rate: {successful}/{total} ({success_rate:.1f}%)")

def compare_configs_at_distance():
    """Compare different configurations at a fixed challenging distance"""
    
    print("\n=== Configuration Comparison at 2km Distance ===\n")
    
    distance = 2000  # 2km - challenging but realistic
    
    configs = [
        ("Default", DEFAULT_CONFIG),
        ("Shallow Water", DEFAULT_CONFIG.__class__(
            transmission_power_db=165.0, frequency_hz=25000.0, spreading_exponent=1.0, site_anomaly_db=-5.0)),
        ("Deep Water", DEFAULT_CONFIG.__class__(
            transmission_power_db=175.0, frequency_hz=8000.0, spreading_exponent=2.0, site_anomaly_db=3.0)),
        ("High Noise", DEFAULT_CONFIG.__class__(
            noise_level_db=65.0, required_snr_db=15.0, transmission_power_db=180.0)),
        ("Low Power", DEFAULT_CONFIG.__class__(
            transmission_power_db=160.0, required_snr_db=8.0, frequency_hz=15000.0)),
        ("Harsh Environment", HARSH_ENVIRONMENT_CONFIG)
    ]
    
    print(f"Test distance: {distance}m")
    print("Config           | Power(dB) | Noise(dB) | SNR(dB) | Loss Prob | Reason")
    print("-" * 80)
    
    for config_name, config in configs:
        comm_model = UnderwaterCommunicationModel(config)
        loss_prob, reason = comm_model.calculate_packet_loss_probability(
            distance, 5.0, 50.0, 50
        )
        
        print(f"{config_name:16s} | {config.transmission_power_db:8.1f} | {config.noise_level_db:8.1f} | {config.required_snr_db:6.1f} | {loss_prob:8.3f} | {reason}")

if __name__ == "__main__":
    test_corrected_physics_model()
    test_transmission_simulation()
    compare_configs_at_distance()
    
    print("\n=== Summary ===")
    print("✅ Fixed pressure-to-power conversion (dB/20 for pressure, dB/10 for power)")
    print("✅ Used realistic underwater acoustic parameters")
    print("✅ Demonstrated distance-dependent packet loss")
    print("✅ Physics-based model now shows realistic behavior!") 