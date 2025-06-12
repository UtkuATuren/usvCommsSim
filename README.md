# 🌊 Advanced UUV Communication Simulation

A sophisticated underwater vehicle (UUV) communication simulation designed for machine learning research on packet loss prediction in underwater acoustic communication systems.

## 🎯 Overview

This simulation creates a realistic underwater environment where a ship and submarine communicate using acoustic signals while the submarine searches for objects. The system models real-world underwater communication challenges including multi-path propagation, environmental attenuation, and distance-based signal degradation.

**Key Features:**
- 🌊 Realistic underwater acoustic communication model with advanced physics
- 🎮 **Professional GUI interface** with real-time monitoring
- 🍎 **Native macOS application** with build system
- 🤖 **Complete ML pipeline** with CNN, LSTM, and Transformer models
- 🔧 **Advanced acoustic configuration system** with 6 preset scenarios
- 🔍 Object detection and autonomous navigation
- 📊 Comprehensive environmental sensor simulation
- ⚡ Real-time packet timing and delay modeling
- 🛡️ Safety constraints and intelligent mission planning
- 📈 **Professional data analysis and visualization tools**

## 🚀 Quick Start

### 🎮 GUI Interface (Recommended)
```bash
# Simple launcher
python3 launch_gui.py

# Or direct launch
python3 simulation_gui.py
```

### 📱 macOS Application
```bash
# Build native macOS app
./build_app.sh

# Launch the built application
open dist/UUV\ Communication\ Simulator.app
```

### 💻 Command Line Interface

#### Basic Simulations
```bash
# Quick demo (1000 ticks)
python3 complex_simulation.py demo

# Full mission (5000 ticks)
python3 complex_simulation.py full

# Extended mission (10000 ticks)
python3 complex_simulation.py extended

# ML training data collection (15000 ticks)
python3 complex_simulation.py ml
```

#### Advanced Options
```bash
# Interactive launcher with menu
python3 complex_simulation.py interactive

# Configuration comparison study
python3 complex_simulation.py compare

# Custom simulation (interactive)
python3 complex_simulation.py custom

# Automated mode for scripting
python3 complex_simulation.py autorun <ticks> <world_size> [config_name]
# Example: python3 complex_simulation.py autorun 10000 1200.0 harsh
```

#### Available Configurations
- `default` - Optimal conditions (170 dB, 12 kHz)
- `shallow` - Shallow water operations (165 dB, 25 kHz)
- `deep` - Deep water operations (175 dB, 8 kHz)  
- `noise` - High noise environment (180 dB, 65 dB noise)
- `low_power` - Low power operations (160 dB)
- `harsh` - Challenging conditions (165 dB, 60 dB noise)

## 📁 Project Structure

```
usvCommsSim/
├── complex_simulation.py          # Main simulation engine
├── comprehensive_physics_simulation.py  # Physics validation suite
├── preprocess.py                  # ML data preprocessing
├── analyze_simulation.py          # Data analysis tools
├── 
├── 🎮 GUI Components
├── simulation_gui.py              # Main GUI application (2,300+ lines)
├── launch_gui.py                  # Simple GUI launcher
├── GUI_README.md                  # Comprehensive GUI documentation
├── 
├── 🍎 macOS Application
├── macos_launcher.py              # macOS app entry point
├── setup.py                       # Application packaging configuration
├── build_app.sh                   # macOS app build script
├── 
├── 🧠 Models & Physics
├── models/
│   ├── acoustic_config.py         # Advanced acoustic configurations
│   ├── acoustic_physics.py        # Core physics calculations
│   ├── communication_model.py     # Underwater acoustic communication
│   ├── game_state.py              # Environment and vehicle states
│   ├── simulation_controller.py   # Mission control and safety
│   ├── csv_logger.py              # Standard data export
│   ├── ml_csv_logger.py           # ML-optimized data export
│   └── packet.py                  # Packet data structures
├── 
├── 🤖 Machine Learning Pipeline
├── machine-learning/
│   ├── CNN/                       # Convolutional Neural Network models
│   │   ├── main.py               # CNN training and evaluation
│   │   ├── predict.py            # CNN prediction interface
│   │   ├── cnn-model.keras       # Trained CNN model
│   │   ├── requirements.txt      # CNN dependencies
│   │   └── *.png                 # Performance reports and charts
│   ├── LSTM/                      # Long Short-Term Memory models
│   │   ├── train_lstm.py         # LSTM training
│   │   ├── LSTM.h5               # Trained LSTM model
│   │   └── *.png                 # Performance visualizations
│   ├── Transformer/               # Transformer models
│   │   ├── train_transformer.py  # Transformer training
│   │   ├── Transformer.h5        # Trained Transformer model
│   │   └── *.png                 # Results and analytics
│   ├── metrics/                   # Model evaluation metrics
│   │   ├── metric.py             # Comprehensive evaluation suite
│   │   └── trained models        # Cross-validation models
│   └── manualish_test.py         # Manual testing utilities
├── 
├── 📡 Protocol Layer
├── protocol/
│   └── packet_formatter.py       # Packet encoding/decoding
├── 
├── 📊 Generated Outputs
├── outputs/
│   ├── standard_simulation/       # Standard CSV exports
│   ├── ml_training_data/          # ML-optimized datasets
│   └── legacy_data/               # Historical data files
├── 
├── 🔬 Physics Testing & Validation
├── test_corrected_physics.py     # Physics model validation
├── test_physics_integration.py   # Integration testing
├── debug_physics_values.py       # Physics debugging tools
└── comprehensive_simulation_report.txt  # Validation results
```

## 🎮 GUI Features

### **Professional Interface**
- **🏠 Main Dashboard**: Welcome screen with quick start options
- **🔧 Configuration Manager**: 6 preset configurations + custom builder
- **📊 Simulation Control**: Single simulation or comparison studies
- **📈 Real-time Monitoring**: Live statistics and console output
- **📋 Results Analysis**: Comprehensive reports with export capabilities

### **6 Preset Acoustic Configurations**
1. **🌊 Default** - Optimal conditions (170 dB, 12 kHz)
2. **🏖️ Shallow Water** - High frequency, cylindrical spreading
3. **🌊 Deep Water** - Low frequency, spherical spreading  
4. **📢 High Noise** - Compensated power for noisy environments
5. **🔋 Low Power** - Efficient operation settings
6. **⚡ Harsh Environment** - Challenging conditions for testing

### **Interactive Parameter Control**
- Real-time parameter sliders with physics validation
- Custom configuration builder with immediate preview
- Configuration comparison studies
- Export capabilities for all results

## 🌊 Advanced Physics Model

### **Sophisticated Acoustic Configuration System**

**Configurable Parameters:**
- **Transmission Power**: 150-190 dB re 1 μPa at 1m
- **Frequency Range**: 5-50 kHz with optimized selections
- **Noise Levels**: 30-80 dB re 1 μPa (ambient conditions)
- **SNR Requirements**: 5-20 dB (communication thresholds)
- **Spreading Models**: 1.0 (cylindrical) to 2.0 (spherical)
- **Site Anomalies**: -10 to +10 dB (environmental effects)

**Physics-Based Modeling:**
- **Thorp's Absorption**: Frequency-dependent signal loss
- **Multi-path Propagation**: Surface and bottom reflections
- **Geometric Spreading**: Distance-based signal attenuation
- **Environmental Factors**: Temperature, salinity, pressure effects
- **Packet Size Penalties**: Realistic transmission time effects

### **Comprehensive Physics Validation**

The system includes extensive physics validation:
```bash
# Run comprehensive physics validation (1M tests)
python3 comprehensive_physics_simulation.py

# Test specific physics calculations
python3 test_corrected_physics.py

# Debug physics integration
python3 test_physics_integration.py
```

**Validation Results:**
- SNR calculations match underwater acoustic theory
- Propagation delays consistent with sound velocity (1497-1500 m/s)
- Multi-path effects realistic for shallow water environments
- Environmental factors properly weighted according to literature

## 🤖 Complete Machine Learning Pipeline

### **Three Advanced Model Architectures**

#### **1. Convolutional Neural Network (CNN)**
```bash
cd machine-learning/CNN
python3 main.py  # Train and evaluate CNN model
python3 predict.py  # Use trained model for predictions
```
- **Architecture**: Multi-layer CNN with dropout regularization
- **Performance**: High accuracy on spatial feature patterns
- **Use Case**: Pattern recognition in communication data

#### **2. Long Short-Term Memory (LSTM)**
```bash
cd machine-learning/LSTM  
python3 train_lstm.py  # Train sequence-based model
```
- **Architecture**: Multi-layer LSTM with attention mechanism
- **Performance**: Excellent for temporal sequence prediction
- **Use Case**: Time series forecasting of packet loss

#### **3. Transformer Model**
```bash
cd machine-learning/Transformer
python3 train_transformer.py  # Train transformer model
```
- **Architecture**: Multi-head attention transformer
- **Performance**: State-of-the-art sequence modeling
- **Use Case**: Complex pattern recognition in communication sequences

### **Comprehensive Model Evaluation**
```bash
cd machine-learning/metrics
python3 metric.py  # Generate comprehensive evaluation reports
```

**Evaluation Metrics:**
- Classification accuracy, precision, recall, F1-score
- ROC-AUC curves and confusion matrices
- Cosine similarity for parameter prediction
- Cross-validation performance analysis

### **Generated ML Datasets**

#### **1. Main Training Dataset** (`packet_prediction.csv`)
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

#### **2. Sequence Dataset** (`packet_prediction_sequences.csv`)
**Time Series Analysis:**
- Packet sequences with temporal patterns
- Cumulative loss rates over time
- Inter-packet timing analysis
- Ideal for LSTM/RNN/Transformer models

#### **3. Quality Timeline** (`packet_prediction_quality_timeline.csv`)
**Communication Trends:**
- SNR and propagation loss over time
- Environmental condition changes
- Quality improvement/degradation patterns

### **Data Preprocessing Pipeline**
```bash
python3 preprocess.py  # Advanced preprocessing with bit encoding
```
- Command encoding to binary representation
- Parameter binning for size-5 ranges
- Success/failure flag conversion
- Feature engineering and normalization

## 📊 Professional Data Analysis

### **Built-in Analysis Tools**
```bash
python3 analyze_simulation.py  # Comprehensive data analysis
```

**Analysis Features:**
- Communication performance metrics with statistical significance
- Object detection efficiency analysis
- Environmental correlation studies
- Packet loss pattern identification with root cause analysis
- Timing and delay distribution analysis
- Configuration comparison with recommendation engine

### **Export Capabilities**
- **CSV Exports**: Standard and ML-optimized formats
- **Report Generation**: Comprehensive text and statistical reports  
- **Visualization**: Charts and graphs (via GUI)
- **Batch Processing**: Automated analysis for multiple configurations

## 🍎 macOS Application

### **Native Application Build**
```bash
# Build macOS application bundle
./build_app.sh

# The resulting app will be in dist/
# Double-click to launch or:
open "dist/UUV Communication Simulator.app"
```

**Application Features:**
- **Native macOS Integration**: Proper app bundle with metadata
- **No Dependencies**: Self-contained application
- **Professional UI**: Native look and feel
- **Crash Prevention**: Enhanced stability for macOS
- **Accessibility**: High-resolution display support

**Technical Details:**
- Built with py2app for native packaging
- Version 1.0.2 with comprehensive metadata
- Optimized for macOS 10.14+ with automatic graphics switching
- Includes all necessary models and dependencies

## 🔧 Advanced Configuration System

### **Acoustic Physics Configuration**

The simulation uses a sophisticated configuration system defined in `models/acoustic_config.py`:

```python
# Example: Create custom configuration
from models.acoustic_config import AcousticPhysicsConfig

custom_config = AcousticPhysicsConfig(
    transmission_power_db=175.0,  # High power military modem
    frequency_hz=10000.0,         # 10 kHz frequency
    noise_level_db=55.0,          # Moderate noise
    required_snr_db=12.0,         # Realistic SNR requirement
    spreading_exponent=1.8,       # Intermediate spreading
    site_anomaly_db=2.0           # Slight propagation degradation
)
```

**Available Preset Configurations:**
- `DEFAULT_CONFIG` - Balanced performance (170 dB, 12 kHz)
- `SHALLOW_WATER_CONFIG` - Optimized for shallow operations
- `DEEP_WATER_CONFIG` - Long-range deep ocean operations
- `HIGH_NOISE_CONFIG` - High ambient noise compensation
- `LOW_POWER_CONFIG` - Energy-efficient operations
- `HARSH_ENVIRONMENT_CONFIG` - Challenging condition testing

## 🎯 Research Applications

### **Packet Loss Prediction Research**
1. **Binary Classification**: Predict communication success/failure
2. **Multi-class Classification**: Classify failure reasons and types
3. **Regression Analysis**: Predict communication delay and quality
4. **Time Series Forecasting**: Predict future communication patterns

### **Operational Applications**
1. **Mission Planning**: Optimal positioning for reliable communication
2. **Environmental Adaptation**: Adjust parameters based on conditions
3. **Communication Scheduling**: Timing optimization for critical messages
4. **Range Prediction**: Maximum reliable communication distances

### **Academic Research**
1. **Underwater Acoustics**: Validate theoretical models
2. **Machine Learning**: Benchmark ML algorithms on realistic data
3. **Communication Theory**: Test protocol efficiency
4. **Environmental Modeling**: Study impact of oceanic conditions

## 📈 Sample Results

### **Realistic Performance Metrics**
From a 5000-tick full mission with default configuration:

```
🎯 Mission Results:
   Configuration: DEFAULT (170 dB, 12 kHz)
   Total ticks: 5,000
   Distance traveled: 8,250.0m
   Objects detected: 3/12 (25.0%)
   Max distance from ship: 387.2m

📡 Communication Performance:
   Overall success rate: 94.2%
   Command success rate: 94.8%
   Status success rate: 93.6%
   Average propagation delay: 24.3ms
   Average total delay: 29.8ms
   Total communication events: 10,000

🔊 Acoustic Analysis:
   Average SNR: 15.2 dB
   Transmission loss range: 45.2-67.8 dB
   Multi-path delay contribution: 5.5ms
   Environmental impact: Moderate
```

### **Configuration Comparison Example**
```
📊 CONFIGURATION COMPARISON SUMMARY
============================================================
Configuration        Success Rate   Avg Delay   Detections
------------------------------------------------------------
OPTIMAL                     96.5%     22.1ms         8
SHALLOW_WATER              97.8%     18.7ms        12
DEEP_WATER                 89.2%     31.4ms         5
HIGH_NOISE                 91.1%     26.8ms         7
HARSH_ENVIRONMENT          82.3%     38.2ms         3
```

## 🛠️ Installation & Setup

### **System Requirements**
- **Python 3.8+** (3.9+ recommended for best GUI performance)
- **macOS 10.14+** (for native app builds)
- **Memory**: 2GB+ RAM (4GB+ for large ML training)
- **Storage**: 1GB+ free space (more for generated datasets)

### **Dependencies**
```bash
# Core simulation (no external dependencies)
python3 complex_simulation.py demo

# GUI interface (tkinter - included with Python)
python3 launch_gui.py

# Machine learning components
cd machine-learning/CNN
pip install -r requirements.txt  # TensorFlow, scikit-learn, etc.
```

### **Optional ML Dependencies**
```bash
# For ML model development
pip install pandas numpy scikit-learn tensorflow matplotlib seaborn

# For advanced analysis
pip install jupyter scipy statsmodels
```

## 🚀 Performance & Scalability

### **Simulation Performance**
- **Standard Simulation**: 1000 ticks/second on modern hardware
- **Physics Calculations**: Optimized for real-time processing
- **Memory Usage**: ~50MB for standard missions, ~200MB for ML training
- **Parallel Processing**: Multi-threaded GUI with background simulation

### **ML Training Performance**
- **CNN Training**: ~5-10 minutes on modern GPU
- **LSTM Training**: ~10-15 minutes for sequence models
- **Transformer Training**: ~15-30 minutes for complex models
- **Dataset Generation**: 15,000 ticks in ~2-3 minutes

### **Scalability Options**
```bash
# Large-scale physics validation
python3 comprehensive_physics_simulation.py  # 1M communication tests

# Extended ML training missions
python3 complex_simulation.py autorun 50000 2000 harsh  # 50k ticks
```

## 🔮 Future Enhancements

### **Planned Features**
- **Advanced Visualization**: 3D trajectory plotting and real-time charts
- **Distributed Simulation**: Multi-node processing for large studies
- **Real-time ML Integration**: Live prediction during simulation
- **Advanced Protocols**: Implementation of real underwater communication protocols
- **Environmental Data Integration**: Real oceanographic data sources
- **Multi-Vehicle Scenarios**: Swarm communication simulation

### **Research Extensions**
- **Doppler Effects**: Moving platform communication modeling  
- **Network Protocols**: Multi-hop underwater networks
- **Energy Modeling**: Battery consumption and power management
- **Advanced Sensors**: Integration of additional sensor types
- **Mission Planning AI**: Intelligent autonomous mission planning

## 📚 Documentation

### **Comprehensive Documentation**
- **README.md** - This comprehensive overview
- **GUI_README.md** - Detailed GUI documentation with screenshots
- **comprehensive_simulation_report.txt** - Physics validation results
- **Code Documentation** - Extensive inline documentation throughout

### **Academic References**
The simulation is based on established underwater acoustic principles:
- Thorp's absorption formula for frequency-dependent attenuation
- Standard geometric spreading models for signal propagation
- Environmental parameter effects based on oceanographic literature
- SNR calculations following underwater communication standards

## 🎉 Key Achievements

✅ **Complete GUI System**: Professional interface with real-time monitoring  
✅ **Native macOS App**: Fully packaged application with build system  
✅ **Advanced ML Pipeline**: CNN, LSTM, and Transformer models  
✅ **Physics Validation**: Comprehensive testing with 1M+ simulation runs  
✅ **Configuration System**: 6 preset scenarios + custom configuration  
✅ **Professional Analysis**: Advanced statistics and comparison tools  
✅ **Scalable Architecture**: From quick demos to large-scale research  
✅ **Academic Quality**: Publication-ready results and documentation  
✅ **Cross-Platform**: Works on macOS, Linux, and Windows  
✅ **Production Ready**: Robust error handling and user experience  

## 📄 License

This project is developed for research purposes. Please cite appropriately if used in academic work.

## 🤝 Contributing

Contributions are welcome! Focus areas:
- **ML Model Improvements**: New architectures and optimization
- **Physics Enhancements**: Additional environmental factors
- **GUI Features**: Advanced visualization and user experience
- **Performance Optimization**: Simulation speed and memory usage
- **Documentation**: Examples, tutorials, and guides

## 🆘 Support

### **Getting Help**
1. **GUI Issues**: Check GUI_README.md for detailed interface documentation
2. **Physics Questions**: Review comprehensive_physics_simulation.py results
3. **ML Model Training**: See machine-learning/ directory documentation
4. **Configuration Problems**: Reference models/acoustic_config.py examples

### **Common Issues**
- **macOS Permission**: Grant accessibility permissions for GUI
- **Python Version**: Ensure Python 3.8+ for best compatibility
- **Memory Issues**: Use smaller tick counts for limited RAM systems
- **GUI Performance**: Close other applications for smooth operation

---

**🌊 For questions, support, or collaboration opportunities, please refer to the comprehensive code documentation or create an issue.** 

*Military-grade underwater acoustic communication simulation for research and development.* 