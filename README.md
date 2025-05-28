# 🌊 Advanced UUV Communication Simulation

A sophisticated underwater vehicle (UUV) communication simulation designed for machine learning research on packet loss prediction in underwater acoustic communication systems.

## 🎯 Overview

This simulation creates a realistic underwater environment where a ship and submarine communicate using acoustic signals while the submarine searches for objects. The system models real-world underwater communication challenges including multi-path propagation, environmental attenuation, and distance-based signal degradation.

**Key Features:**
- 🌊 Realistic underwater acoustic communication model
- 🤖 ML-optimized data export for packet loss prediction
- 🔍 Object detection and autonomous navigation
- 📊 Comprehensive environmental sensor simulation
- ⚡ Real-time packet timing and delay modeling
- 🛡️ Safety constraints and intelligent mission planning

## 🚀 Quick Start

### Basic Demo (1000 ticks)
```bash
python3 complex_simulation.py demo
```

### Full Mission (5000 ticks)
```bash
python3 complex_simulation.py full
```

### ML Training Data Collection (15000 ticks)
```bash
python3 complex_simulation.py ml
```

### Custom Simulation
```bash
python3 complex_simulation.py custom <ticks> <world_size>
# Example: python3 complex_simulation.py custom 10000 1200.0
```

## 📁 Project Structure

```
usvCommsSim/
├── complex_simulation.py          # Main simulation runner
├── analyze_simulation.py          # Data analysis tools
├── models/                        # Core simulation models
│   ├── communication_model.py     # Underwater acoustic communication
│   ├── game_state.py              # Environment and vehicle states
│   ├── simulation_controller.py   # Mission control and safety
│   ├── csv_logger.py              # Standard data export
│   ├── ml_csv_logger.py           # ML-optimized data export
│   └── packet.py                  # Packet data structures
├── protocol/                      # Communication protocols
│   └── packet_formatter.py        # Packet encoding/decoding
└── outputs/                       # Generated data files
    ├── standard_simulation/       # Standard CSV exports
    ├── ml_training_data/          # ML-optimized datasets
    └── legacy_data/               # Historical data files
```

## 🌊 Simulation Features

### Realistic Underwater Communication Model

**Physics-Based Acoustic Propagation:**
- **Frequency**: 12 kHz (typical for underwater modems)
- **Multi-path Propagation**: Surface and bottom reflections
- **Thorp's Absorption**: Frequency-dependent signal loss
- **SNR Calculation**: Signal-to-noise ratio based packet success
- **Environmental Factors**: Sea state, temperature, salinity effects

**Performance Metrics:**
- Overall success rate: ~96.5% (realistic for underwater systems)
- Propagation delays: 20-30ms for typical distances
- Multi-path delays: 5-10ms additional from reflections

### Comprehensive Environmental Modeling

**9 Environmental Sensors:**
- 🌡️ **Water Temperature**: Thermocline modeling with depth
- 💧 **Pressure**: Accurate depth-based calculation
- 💡 **Light Levels**: Exponential decay with depth
- 🌫️ **Turbidity**: Water clarity affecting visibility
- 🌊 **Current**: Speed and direction affecting propagation
- 🧪 **Chemical Properties**: Salinity, pH, dissolved oxygen

### Intelligent Mission Planning

**Safety-First Approach:**
- **Max Safe Distance**: 800m communication range limit
- **Return Logic**: Automatic return at 80% of max distance
- **Command Validation**: Safety checks before execution
- **Adaptive Movement**: Distance-aware speed reduction

**Search Patterns:**
- Spiral search for systematic coverage
- Grid search for structured exploration
- Random search for unpredictable patterns

### Object Detection System

**Dynamic Object Generation:**
- 5-15 random objects per mission
- Object types: wreck, rock, debris, mine, artifact
- Detection range: 50m radius
- Real-time detection tracking and reporting

## 🤖 Machine Learning Integration

### Generated Datasets

The simulation generates three specialized datasets optimized for ML training:

#### 1. Main Training Dataset (`packet_prediction.csv`)
**50+ Features for Comprehensive Analysis:**

**Temporal Features:**
- `tick`, `timestamp`, `time_since_last_transmission`
- `propagation_delay_ms`, `multipath_delay_ms`, `total_delay_ms`

**Spatial Features:**
- `distance_2d`, `distance_3d`, `depth_difference`
- `submarine_x`, `submarine_y`, `submarine_z`
- `heading_to_ship`, `distance_from_safe_zone`

**Environmental Features:**
- `water_temperature`, `sea_state`, `submarine_depth`
- `pressure`, `light_level`, `turbidity`, `current_speed`
- `salinity`, `ph_level`, `dissolved_oxygen`

**Communication Features:**
- `signal_strength`, `snr_db`, `propagation_loss_db`
- `packet_size_bytes`, `sound_velocity`

**Historical Features (Sliding Window):**
- `packets_sent_last_10`, `packets_lost_last_10`
- `success_rate_last_10`, `avg_delay_last_10`

**Target Variables:**
- `packet_lost` (binary): Main prediction target
- `loss_reason` (categorical): Why packet was lost
- `delay_category` (categorical): Delay classification

#### 2. Sequence Dataset (`packet_prediction_sequences.csv`)
**Time Series Analysis:**
- Packet sequences with temporal patterns
- Cumulative loss rates over time
- Inter-packet timing analysis
- Ideal for LSTM/RNN models

#### 3. Quality Timeline (`packet_prediction_quality_timeline.csv`)
**Communication Trends:**
- SNR and propagation loss over time
- Environmental condition changes
- Quality improvement/degradation patterns

### Recommended ML Approaches

**Binary Classification (Packet Loss Prediction):**
```python
# Target: packet_lost (True/False)
# Recommended models: Random Forest, XGBoost, Neural Networks
# Key features: distance_2d, snr_db, signal_strength, sea_state
```

**Multi-class Classification (Loss Reason):**
```python
# Target: loss_reason ('low_snr', 'moderate_snr', 'out_of_range', 'good_snr')
# Use: Understanding failure modes and optimization
```

**Time Series Prediction:**
```python
# Dataset: Sequence data with temporal patterns
# Models: LSTM, RNN for sequential prediction
# Use: Predicting future communication quality
```

**Delay Prediction:**
```python
# Target: total_delay_ms or delay_category
# Use: Optimizing communication timing and scheduling
```

## 📊 Sample Results

From a 1000-tick demo mission:

```
🎯 Mission Results:
   Total ticks: 1,000
   Distance traveled: 2,102.0m
   Objects detected: 1/12 (8.3%)
   Max distance from ship: 49.9m

📡 Communication Performance:
   Overall success rate: 96.5%
   Command success rate: 96.7%
   Status success rate: 96.2%
   Average propagation delay: 22.1ms
   Average total delay: 27.6ms
   Total communication events: 2,000
```

## 🔧 Configuration

### Communication Parameters
```python
# In models/communication_model.py
frequency = 12000.0  # Hz (12 kHz)
transmission_power = 180.0  # dB re 1 μPa at 1m
noise_level = 50.0  # dB re 1 μPa
max_reliable_range = 1000.0  # meters
data_rate = 1200.0  # bits per second
```

### Mission Parameters
```python
# In complex_simulation.py
num_ticks = 5000  # Simulation duration
world_size = 1000.0  # World dimensions (meters)
```

### Safety Settings
```python
# In models/game_state.py
max_safe_distance_from_ship = 800.0  # meters
detection_range = 50.0  # meters
max_depth = 200.0  # meters
```

## 🛠️ Available Commands

The simulation implements all UUV commands from the packet formatter:

- **MOVE**: Move submarine in current heading direction
- **TURN**: Change submarine heading
- **STOP**: Stop all submarine movement
- **ASCEND**: Move submarine toward surface
- **DESCEND**: Move submarine deeper
- **REPORT_STATUS**: Request comprehensive status report

## 📈 Data Analysis

Use the included analysis tools to examine simulation results:

```bash
python3 analyze_simulation.py
```

**Analysis Features:**
- Communication performance metrics
- Object detection statistics
- Environmental correlation analysis
- Packet loss pattern identification
- Timing and delay analysis

## 🎯 Research Applications

This simulation is designed for research in:

1. **Packet Loss Prediction**: ML models to predict communication failures
2. **Timing Optimization**: Understanding delay patterns for better scheduling
3. **Communication Planning**: Optimal positioning for reliable communication
4. **Environmental Adaptation**: Adjusting communication based on conditions
5. **Mission Efficiency**: Balancing exploration with communication reliability

## 🔬 Technical Validation

**Communication Model Validation:**
- SNR calculations match underwater acoustic theory
- Propagation delays consistent with sound velocity (1497-1500 m/s)
- Multi-path effects realistic for shallow water environments
- Environmental factors properly weighted according to literature

**Safety System Validation:**
- No communication failures due to excessive distance
- Intelligent return behavior when approaching limits
- Command validation prevents unsafe operations
- Comprehensive error handling and logging

## 📚 Dependencies

- **Python 3.7+**
- **Standard Library Only** (no external dependencies for simulation)
- **Optional for ML Development**: pandas, scikit-learn, tensorflow, pytorch

## 🤝 Development Workflow

### For ML Model Development:

1. **Generate Training Data:**
   ```bash
   python3 complex_simulation.py ml
   ```

2. **Load and Preprocess Data:**
   ```python
   import pandas as pd
   df = pd.read_csv('outputs/ml_training_data/packet_prediction.csv')
   ```

3. **Feature Engineering:**
   - Select relevant features based on correlation analysis
   - Create additional derived features
   - Handle categorical variables

4. **Model Training:**
   - Split data into train/validation/test sets
   - Train multiple models (RF, XGBoost, NN)
   - Evaluate performance using appropriate metrics

5. **Model Integration:**
   - Implement trained models back into simulation
   - Use for real-time prediction and adaptive strategies

### For Simulation Extension:

1. **Add New Sensors:** Extend `EnvironmentalSensors` class
2. **Modify Communication Model:** Update physics parameters
3. **Add New Commands:** Extend `CommandCode` enum and handlers
4. **Custom Mission Patterns:** Modify `MissionPlanner` class

## 🎉 Key Achievements

✅ **Realistic Communication Model**: Physics-based underwater acoustic propagation  
✅ **Comprehensive Sensor Data**: 9 environmental sensors with realistic modeling  
✅ **Safety Constraints**: Intelligent mission planning with communication limits  
✅ **Packet Timing**: Complete transmission lifecycle tracking  
✅ **ML-Ready Data**: 50+ features optimized for machine learning  
✅ **Multiple Datasets**: Training, sequence, and quality timeline data  
✅ **Scalable Architecture**: Easy to extend and modify for research  
✅ **Performance Optimization**: Efficient simulation of complex scenarios  

## 📄 License

This project is developed for research purposes. Please cite appropriately if used in academic work.

## 🤝 Contributing

Contributions are welcome! Please focus on:
- Improving communication model accuracy
- Adding new environmental factors
- Enhancing ML feature engineering
- Optimizing simulation performance
- Adding new analysis tools

---

**For questions or support, please refer to the code documentation or create an issue.** 