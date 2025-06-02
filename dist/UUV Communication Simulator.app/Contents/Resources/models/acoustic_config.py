"""
Configuration module for physics-based underwater acoustic communication parameters.
This module centralizes all configurable parameters for the acoustic physics model.
"""

from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class AcousticPhysicsConfig:
    """Configuration for physics-based underwater acoustic communication model"""
    
    # Source parameters (dB re 1 μPa at 1m for underwater acoustics)
    # Typical underwater modems: 160-190 dB, but these are PRESSURE levels
    transmission_power_db: float = 170.0  # dB re 1 μPa at 1m (realistic modem)
    frequency_hz: float = 12000.0  # Hz (12 kHz typical for underwater modems)
    
    # Noise parameters (dB re 1 μPa for ambient noise)
    # Typical underwater noise: 40-70 dB re 1 μPa
    noise_level_db: float = 50.0  # dB re 1 μPa (ambient noise)
    
    # SNR requirements (power ratio in dB)
    required_snr_db: float = 10.0  # dB (minimum SNR for reliable communication)
    
    # Propagation model parameters
    spreading_exponent: float = 1.5  # 1.0=cylindrical, 1.5=intermediate, 2.0=spherical
    site_anomaly_db: float = 0.0  # dB (site-specific propagation anomaly)
    
    # Packet size adjustment parameters
    baseline_packet_size: int = 50  # bytes (reference packet size)
    size_adjustment_factor: float = 500.0  # scaling factor for packet size effects
    max_size_penalty: float = 2.0  # maximum size-based loss multiplier
    
    @property
    def frequency_khz(self) -> float:
        """Convert frequency from Hz to kHz for Thorp's formula"""
        return self.frequency_hz / 1000.0
    
    @property 
    def transmission_pressure_linear(self) -> float:
        """Convert transmission pressure from dB to linear scale (CORRECTED)"""
        # For pressure levels: p = 10^(dB/20)
        return 10.0 ** (self.transmission_power_db / 20.0)
    
    @property
    def noise_pressure_linear(self) -> float:
        """Convert noise pressure from dB to linear scale (CORRECTED)"""
        # For pressure levels: p = 10^(dB/20)
        return 10.0 ** (self.noise_level_db / 20.0)
    
    @property 
    def transmission_power_linear(self) -> float:
        """Convert transmission pressure to power (intensity) for SNR calculations"""
        # Power is proportional to pressure squared: P ∝ p²
        return self.transmission_pressure_linear ** 2
    
    @property
    def noise_power_linear(self) -> float:
        """Convert noise pressure to power (intensity) for SNR calculations"""
        # Power is proportional to pressure squared: P ∝ p²
        return self.noise_pressure_linear ** 2
    
    @property
    def required_snr_linear(self) -> float:
        """Convert required SNR from dB to linear scale"""
        # SNR is a power ratio: SNR = 10^(dB/10)
        return 10.0 ** (self.required_snr_db / 10.0)
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration"""
        return {
            'frequency': {
                'hz': self.frequency_hz,
                'khz': self.frequency_khz
            },
            'pressure_levels': {
                'transmission_pressure_db': self.transmission_power_db,
                'transmission_pressure_linear': self.transmission_pressure_linear,
                'noise_pressure_db': self.noise_level_db,
                'noise_pressure_linear': self.noise_pressure_linear,
            },
            'power_levels': {
                'transmission_power_linear': self.transmission_power_linear,
                'noise_power_linear': self.noise_power_linear,
                'required_snr_db': self.required_snr_db,
                'required_snr_linear': self.required_snr_linear
            },
            'propagation': {
                'spreading_exponent': self.spreading_exponent,
                'site_anomaly_db': self.site_anomaly_db
            },
            'packet_adjustments': {
                'baseline_packet_size': self.baseline_packet_size,
                'size_adjustment_factor': self.size_adjustment_factor,
                'max_size_penalty': self.max_size_penalty
            }
        }

# Default configuration instance (realistic underwater modem)
DEFAULT_CONFIG = AcousticPhysicsConfig()

# Predefined configurations for different scenarios
SHALLOW_WATER_CONFIG = AcousticPhysicsConfig(
    transmission_power_db=165.0,  # Lower power for shallow water
    frequency_hz=25000.0,  # Higher frequency for short range
    spreading_exponent=1.0,  # More cylindrical spreading
    site_anomaly_db=-5.0  # Better propagation conditions
)

DEEP_WATER_CONFIG = AcousticPhysicsConfig(
    transmission_power_db=175.0,  # Higher power for deep water
    frequency_hz=8000.0,  # Lower frequency for long range
    spreading_exponent=2.0,  # More spherical spreading
    site_anomaly_db=3.0  # Harsher propagation conditions
)

HIGH_NOISE_CONFIG = AcousticPhysicsConfig(
    noise_level_db=65.0,  # High ambient noise (ship traffic, etc.)
    required_snr_db=15.0,  # Higher SNR requirement
    transmission_power_db=180.0  # Compensate with higher power
)

LOW_POWER_CONFIG = AcousticPhysicsConfig(
    transmission_power_db=160.0,  # Low power operation
    required_snr_db=8.0,  # Lower SNR requirement 
    frequency_hz=15000.0  # Optimize frequency for efficiency
)

# Harsh environment configuration for testing
HARSH_ENVIRONMENT_CONFIG = AcousticPhysicsConfig(
    transmission_power_db=165.0,  # Moderate power
    noise_level_db=60.0,  # High noise
    required_snr_db=12.0,  # High SNR requirement
    frequency_hz=10000.0,  # Lower frequency
    spreading_exponent=2.0,  # Spherical spreading
    site_anomaly_db=5.0  # Poor propagation conditions
)

# Realistic testing configuration for meaningful packet loss at moderate ranges
REALISTIC_TESTING_CONFIG = AcousticPhysicsConfig(
    transmission_power_db=155.0,  # Much lower power (typical small UUV)
    noise_level_db=65.0,  # Very high noise (shipping traffic)
    required_snr_db=15.0,  # High SNR requirement for reliable comms
    frequency_hz=15000.0,  # Higher frequency (more absorption)
    spreading_exponent=2.0,  # Spherical spreading (worst case)
    site_anomaly_db=10.0  # Very poor propagation conditions
) 