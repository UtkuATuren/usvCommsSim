# Physics-Based Underwater Acoustic Communication Integration Guide

This guide documents the integration of physics-based packet transmission modeling into the underwater acoustic simulator, replacing hard-coded success probabilities with realistic acoustic propagation calculations.

## Overview

The integration replaces simple fixed success probabilities (e.g., `0.9`) with a comprehensive physics-based model that accounts for:

- **Thorp's absorption formula** for frequency-dependent attenuation
- **Geometric spreading loss** with configurable spreading exponents  
- **Rayleigh fading** statistical modeling for realistic channel variations
- **Distance-dependent propagation** effects
- **SNR-based packet loss** calculations
- **Packet size effects** on transmission reliability

## Files Created/Modified

### New Files

1. **`models/acoustic_physics.py`** - Core physics functions
   - `alpha_thorp()` - Frequency-dependent absorption coefficient
   - `transmission_loss()` - Total transmission loss calculation
   - `linear_attenuation()` - dB to linear conversion
   - `compute_gamma_mean()` - Mean SNR calculation
   - `packet_loss_probability()` - Rayleigh fading loss probability

2. **`models/acoustic_config.py`** - Configuration management
   - `AcousticPhysicsConfig` - Centralized parameter configuration
   - Predefined configurations for different scenarios
   - Unit conversion properties (dB ↔ linear)

3. **`test_physics_integration.py`** - Integration validation
   - Demonstrates physics-based vs hard-coded comparison
   - Tests different environmental configurations
   - Validates packet transmission simulation

### Modified Files

1. **`models/communication_model.py`** - Main integration point
   - Updated `UnderwaterCommunicationModel` constructor to accept configuration
   - Replaced `calculate_packet_loss_probability()` with physics-based implementation
   - Added configuration update capabilities
   - Maintained same random number generation for consistent seeding

## Integration Details

### Before Integration
```python
# Old approach - hard-coded probability
d = compute_current_range()
noise_psd = get_current_noise_psd()
fixed_success_probability = 0.9
if random.random() < fixed_success_probability:
    deliver_packet_to_receiver()
else:
    drop_packet()
```

### After Integration
```python
# New approach - physics-based calculation
d = compute_current_range()            # distance in meters
noise_psd = get_current_noise_psd()    # noise PSD (same units as P0)

# Physics parameters (from configuration)
P0 = SOURCE_PSD_AT_1M                 # linear PSD at 1m
gamma_req = REQUIRED_SNR              # unitless (linear)
spreading_exp = 1.5                   # geometric exponent
anomaly_db = 0.0                      # site anomaly
f_khz = CARRIER_FREQ_KHZ              # e.g. 12.0

# Calculate physics-based loss probability
TL_db = transmission_loss(d, f_khz, spreading_exp, anomaly_db)
gamma_mean = compute_gamma_mean(d, P0, noise_psd, f_khz, spreading_exp, anomaly_db)
P_loss = packet_loss_probability(d, P0, noise_psd, f_khz, gamma_req, spreading_exp, anomaly_db)

# Physics-based transmission decision
if random.random() < (1.0 - P_loss):
    deliver_packet_to_receiver()
else:
    drop_packet()
```

## Key Parameters

### Source and Noise Parameters
- **P0**: Source power spectral density at 1m (linear scale)
- **noise_psd**: Ambient noise power spectral density (linear scale, same units as P0)
- **gamma_req**: Required SNR threshold (linear scale)

### Propagation Parameters
- **f_khz**: Carrier frequency in kHz (required for Thorp's formula)
- **spreading_exp**: Geometric spreading exponent
  - `1.0` = cylindrical spreading
  - `1.5` = intermediate (default)
  - `2.0` = spherical spreading
- **anomaly_db**: Site-specific propagation anomaly in dB

### Distance and Size Effects
- **d**: Distance in meters between transmitter and receiver
- **packet_size**: Packet size in bytes (affects transmission duration and error probability)

## Configuration Examples

### Default Configuration
```python
from models.communication_model import UnderwaterCommunicationModel
from models.acoustic_config import DEFAULT_CONFIG

# Use default parameters
comm_model = UnderwaterCommunicationModel(DEFAULT_CONFIG)
```

### Custom Configuration
```python
from models.acoustic_config import AcousticPhysicsConfig

# Create custom configuration
custom_config = AcousticPhysicsConfig(
    transmission_power_db=185.0,  # Higher power
    frequency_hz=8000.0,          # Lower frequency for long range
    noise_level_db=55.0,          # Higher noise environment
    required_snr_db=12.0,         # Higher SNR requirement
    spreading_exponent=2.0,       # Spherical spreading
    site_anomaly_db=3.0           # Harsh propagation conditions
)

comm_model = UnderwaterCommunicationModel(custom_config)
```

### Predefined Scenarios
```python
from models.acoustic_config import (
    SHALLOW_WATER_CONFIG,
    DEEP_WATER_CONFIG,
    HIGH_NOISE_CONFIG,
    LOW_POWER_CONFIG
)

# Use predefined configurations
shallow_model = UnderwaterCommunicationModel(SHALLOW_WATER_CONFIG)
deep_model = UnderwaterCommunicationModel(DEEP_WATER_CONFIG)
```

## Usage in Simulation

### Basic Packet Transmission
```python
# Create communication model
comm_model = UnderwaterCommunicationModel()

# Define positions
ship_pos = (0.0, 0.0, 5.0)      # x, y, depth in meters
sub_pos = (500.0, 0.0, 50.0)    # 500m away, 50m deep

# Simulate transmission
transmission = comm_model.simulate_transmission(
    sender="ship",
    receiver="submarine",
    packet_type="command",
    data_size=16,  # bytes
    ship_pos=ship_pos,
    sub_pos=sub_pos
)

# Check result
if transmission.is_received:
    print(f"Packet delivered with {transmission.total_delay*1000:.2f}ms delay")
else:
    print(f"Packet lost: {transmission.loss_reason}")
```

### Direct Loss Probability Calculation
```python
# Calculate loss probability without full simulation
distance = 500.0  # meters
ship_depth = 5.0
sub_depth = 50.0
packet_size = 50  # bytes

loss_prob, reason = comm_model.calculate_packet_loss_probability(
    distance, ship_depth, sub_depth, packet_size
)

print(f"Loss probability: {loss_prob:.3f} ({reason})")
print(f"Success probability: {1.0 - loss_prob:.3f}")
```

## Performance Optimizations

### Cached Calculations
The implementation includes several optimizations:

1. **Frequency conversion**: `f_khz` is cached to avoid repeated Hz→kHz conversion
2. **Absorption coefficient**: `alpha_thorp(f_khz)` is cached when frequency doesn't change
3. **Anomaly factor**: Linear anomaly factor is pre-calculated for repeated use

### Batch Processing
For scenarios with constant frequency and anomaly:
```python
# Pre-calculate common values outside packet loop
f_khz = comm_model._f_khz
alpha_cached = comm_model._alpha_cached
anomaly_linear = comm_model._anomaly_linear_cached

# Use cached values in packet processing loop
```

## Validation and Testing

### Run Integration Tests
```bash
python test_physics_integration.py
```

This will:
- Compare different configuration scenarios
- Demonstrate packet transmission simulation
- Show physics-based vs hard-coded approach differences
- Validate parameter calculations

### Expected Results
- **Short distances (< 100m)**: Very low loss probability
- **Medium distances (100-500m)**: Moderate loss probability, dependent on SNR
- **Long distances (> 1000m)**: High loss probability due to propagation loss
- **Larger packets**: Higher loss probability due to longer transmission time
- **Different configurations**: Significantly different loss characteristics

## Key Benefits

1. **Realistic modeling**: Physics-based calculations instead of arbitrary probabilities
2. **Distance dependency**: Loss probability correctly increases with distance
3. **Frequency effects**: Absorption varies realistically with frequency
4. **Environmental adaptation**: Different configurations for different scenarios
5. **Statistical accuracy**: Rayleigh fading provides realistic channel variation
6. **Packet size effects**: Larger packets have appropriately higher error rates
7. **Consistent seeding**: Same `random` module maintains reproducible behavior

## Migration Notes

### Backward Compatibility
- Same `random.random()` calls maintain seeding behavior
- Same function signatures for packet transmission simulation
- Configuration can be changed without code modifications

### Parameter Tuning
- Start with `DEFAULT_CONFIG` and adjust based on specific requirements
- Use predefined configurations as starting points
- Monitor success rates and adjust `required_snr_db` for desired performance

### Debugging
- Loss reasons provide insight into failure modes
- Configuration summary shows all parameter values
- Test script demonstrates expected behavior ranges

## Troubleshooting

### Common Issues

1. **Very high/low loss rates**: Check power levels and SNR requirements
2. **Unexpected behavior**: Verify distance units (meters) and frequency units (Hz/kHz)
3. **Numerical errors**: Handled gracefully with fallback loss probability
4. **Configuration conflicts**: Use `get_configuration_summary()` to inspect values

### Parameter Guidelines

- **transmission_power_db**: Typical range 160-190 dB
- **frequency_hz**: Typical range 8000-25000 Hz for underwater modems
- **noise_level_db**: Typical range 40-70 dB depending on environment
- **required_snr_db**: Typical range 6-15 dB depending on modulation scheme
- **spreading_exponent**: 1.0-2.0, with 1.5 as reasonable default

The physics-based model provides a significant improvement in realism while maintaining the same interface and random number generation behavior as the original implementation. 