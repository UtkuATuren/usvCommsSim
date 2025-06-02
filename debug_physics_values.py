"""
Diagnostic script to debug the physics-based model values and identify why there's no packet loss.
"""

import math
from models.acoustic_physics import transmission_loss, compute_gamma_mean, packet_loss_probability
from models.acoustic_config import DEFAULT_CONFIG

def debug_physics_calculations():
    """Debug the actual values being calculated in the physics model"""
    
    print("=== Debugging Physics-Based Model Values ===\n")
    
    # Test scenario
    distance = 500.0  # meters
    config = DEFAULT_CONFIG
    
    print(f"Test scenario: {distance}m distance")
    print(f"Configuration:")
    print(f"  Transmission power: {config.transmission_power_db} dB re 1 μPa")
    print(f"  Noise level: {config.noise_level_db} dB re 1 μPa")
    print(f"  Required SNR: {config.required_snr_db} dB")
    print(f"  Frequency: {config.frequency_hz/1000:.1f} kHz")
    print()
    
    # Current (incorrect) conversion
    P0_current = config.transmission_power_linear
    N_current = config.noise_power_linear
    gamma_req_current = config.required_snr_linear
    
    print("Current conversions (INCORRECT - treating pressure as power):")
    print(f"  P0 = 10^({config.transmission_power_db}/10) = {P0_current:.2e}")
    print(f"  N = 10^({config.noise_level_db}/10) = {N_current:.2e}")
    print(f"  gamma_req = 10^({config.required_snr_db}/10) = {gamma_req_current:.2f}")
    print(f"  Initial gamma_0 = P0/N = {P0_current/N_current:.2e}")
    print()
    
    # Correct conversion for pressure levels
    P0_correct = 10.0 ** (config.transmission_power_db / 20.0)  # Pressure conversion
    N_correct = 10.0 ** (config.noise_level_db / 20.0)  # Pressure conversion
    # For SNR we want power ratio, so we square the pressure ratios or use /10
    gamma_req_correct = 10.0 ** (config.required_snr_db / 10.0)  # Power ratio is correct
    
    print("Correct conversions (pressure levels with dB/20):")
    print(f"  P0 = 10^({config.transmission_power_db}/20) = {P0_correct:.2e}")
    print(f"  N = 10^({config.noise_level_db}/20) = {N_correct:.2e}")
    print(f"  gamma_req = 10^({config.required_snr_db}/10) = {gamma_req_correct:.2f}")
    print(f"  Initial gamma_0 = (P0/N)^2 = {(P0_correct/N_correct)**2:.2e}")
    print()
    
    # Calculate transmission loss
    f_khz = config.frequency_khz
    TL_db = transmission_loss(distance, f_khz)
    L_lin = 10.0 ** (TL_db / 10.0)  # This is correct for power loss
    
    print(f"Transmission loss calculation:")
    print(f"  TL = {TL_db:.2f} dB")
    print(f"  L_linear = 10^({TL_db:.2f}/10) = {L_lin:.2e}")
    print()
    
    # Current (incorrect) SNR calculation
    gamma_mean_current = compute_gamma_mean(distance, P0_current, N_current, f_khz)
    P_loss_current = packet_loss_probability(distance, P0_current, N_current, f_khz, gamma_req_current)
    
    print("Current model results (INCORRECT):")
    print(f"  gamma_mean = {gamma_mean_current:.2e}")
    print(f"  P_loss = {P_loss_current:.6f}")
    print()
    
    # Correct SNR calculation (using squared pressure ratio for power)
    gamma_0_correct = (P0_correct / N_correct) ** 2  # Convert pressure ratio to power ratio
    gamma_mean_correct = gamma_0_correct / L_lin
    P_loss_correct = 1.0 - math.exp(-gamma_req_correct / gamma_mean_correct)
    
    print("Corrected model results:")
    print(f"  gamma_mean = {gamma_mean_correct:.2e}")
    print(f"  P_loss = {P_loss_correct:.6f}")
    print()
    
    # Show why the difference matters
    print("Why this matters:")
    print(f"  Current model has gamma_mean = {gamma_mean_current:.0e} (way too high!)")
    print(f"  Corrected model has gamma_mean = {gamma_mean_correct:.0e}")
    print(f"  Required gamma = {gamma_req_correct:.0e}")
    print()
    print(f"  Current exp(-gamma_req/gamma_mean) = {math.exp(-gamma_req_current/gamma_mean_current):.6f}")
    print(f"  Corrected exp(-gamma_req/gamma_mean) = {math.exp(-gamma_req_correct/gamma_mean_correct):.6f}")

def test_distance_effects():
    """Test how packet loss should vary with distance"""
    
    print("\n=== Distance Effect Test (with corrected units) ===\n")
    
    config = DEFAULT_CONFIG
    f_khz = config.frequency_khz
    
    # Correct conversions
    P0_correct = 10.0 ** (config.transmission_power_db / 20.0)
    N_correct = 10.0 ** (config.noise_level_db / 20.0)
    gamma_req_correct = 10.0 ** (config.required_snr_db / 10.0)
    gamma_0_correct = (P0_correct / N_correct) ** 2
    
    print("Distance (m) | TL (dB) | gamma_mean | P_loss")
    print("-" * 45)
    
    distances = [50, 100, 200, 500, 1000, 2000, 5000]
    
    for distance in distances:
        TL_db = transmission_loss(distance, f_khz)
        L_lin = 10.0 ** (TL_db / 10.0)
        gamma_mean = gamma_0_correct / L_lin
        P_loss = 1.0 - math.exp(-gamma_req_correct / gamma_mean)
        
        print(f"{distance:8d} | {TL_db:6.1f} | {gamma_mean:10.2e} | {P_loss:6.3f}")

if __name__ == "__main__":
    debug_physics_calculations()
    test_distance_effects() 