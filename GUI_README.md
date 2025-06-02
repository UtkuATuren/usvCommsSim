# 🌊 UUV Communication Simulation GUI

**Beautiful graphical interface for physics-based underwater acoustic communication simulation**

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![GUI](https://img.shields.io/badge/GUI-tkinter-orange.svg)

## 🚀 Features

### 🏠 **Main Dashboard**
- Welcome screen with quick start options
- System status monitoring
- Easy navigation to all features

### 🔧 **Configuration Manager**
- **6 Preset Configurations:**
  - 🌊 Default (Optimal conditions)
  - 🏖️ Shallow Water (High frequency, cylindrical spreading)
  - 🌊 Deep Water (Low frequency, spherical spreading)
  - 📢 High Noise Environment (Compensated power)
  - 🔋 Low Power Operation (Efficient settings)
  - ⚡ Harsh Environment (Challenging conditions)

- **Custom Configuration Builder:**
  - Interactive sliders for all parameters
  - Real-time parameter updates
  - Physics validation

### 📊 **Simulation Control**
- Single simulation or configuration comparison
- Adjustable parameters (ticks, world size)
- Progress monitoring
- Start/stop controls

### 📈 **Real-time Monitoring**
- Live statistics display
- Simulation console with timestamped logs
- Progress tracking
- Performance metrics

### 📋 **Results Analysis**
- Comprehensive simulation summary
- Communication performance metrics
- Object detection statistics
- Export capabilities (CSV, reports)
- Future: Interactive charts and visualizations

## 🎯 Quick Start

### **Method 1: Simple Launcher**
```bash
python3 launch_gui.py
```

### **Method 2: Direct Launch**
```bash
python3 simulation_gui.py
```

### **Method 3: From Command Line**
```bash
# For help
python3 complex_simulation.py --help

# For automated runs
python3 complex_simulation.py autorun 1000 1500 harsh
```

## 🎮 How to Use

### **1. Getting Started**
1. Launch the GUI using one of the methods above
2. Start on the **🏠 Home** tab for an overview
3. Use **Quick Start** buttons or navigate manually

### **2. Configure Your Simulation**
1. Go to **🔧 Configuration** tab
2. Choose a preset configuration or create custom
3. Adjust parameters using the interactive sliders
4. Click **📝 Apply Custom Configuration**

### **3. Run Simulation**
1. Switch to **📊 Simulation** tab
2. Set number of ticks and world size
3. Choose single simulation or comparison study
4. Click **🚀 Start Simulation**

### **4. Monitor Progress**
1. The **📈 Monitor** tab shows real-time stats
2. Watch the console for detailed logs
3. Track progress with the progress bar

### **5. Analyze Results**
1. View results in the **📋 Results** tab
2. Export data using the export buttons
3. Review comprehensive statistics

## 🔧 Configuration Parameters

| Parameter | Range | Description |
|-----------|-------|-------------|
| **Transmission Power** | 150-190 dB | Source level (dB re 1 μPa) |
| **Frequency** | 5-50 kHz | Carrier frequency |
| **Noise Level** | 30-80 dB | Ambient noise (dB re 1 μPa) |
| **Required SNR** | 5-20 dB | Minimum SNR for success |
| **Spreading Exponent** | 1.0-2.0 | Geometric spreading (1.0=cylindrical, 2.0=spherical) |
| **Site Anomaly** | -10 to +10 dB | Environmental propagation effects |

## 📊 Simulation Types

### **🎯 Single Simulation**
- Run one simulation with current configuration
- Detailed results and statistics
- Export capabilities

### **🔬 Configuration Comparison**
- Test multiple configurations automatically
- Side-by-side performance comparison
- Optimal for research and analysis

## 💾 Output Files

The GUI automatically generates organized output files:

```
outputs/
├── standard_simulation/
│   ├── uuv_simulation_[config]_log.csv
│   ├── uuv_simulation_[config]_objects.csv
│   ├── uuv_simulation_[config]_detections.csv
│   └── uuv_simulation_[config]_communication.csv
└── ml_training_data/
    ├── packet_prediction_[config].csv
    ├── packet_prediction_[config]_sequences.csv
    └── packet_prediction_[config]_quality_timeline.csv
```

## 🎨 GUI Design

### **Dark Theme**
- Modern dark interface easy on the eyes
- Color-coded elements for clarity
- Professional appearance

### **Responsive Layout**
- Tabbed interface for organized workflow
- Real-time updates
- Intuitive navigation

### **Interactive Elements**
- Sliders for parameter adjustment
- Progress indicators
- Status displays
- Console output

## 🔮 Future Enhancements

### **Charts & Visualization**
- Real-time plotting with matplotlib
- Interactive distance vs. success rate graphs
- Communication quality heatmaps
- 3D trajectory visualization

### **Advanced Features**
- Simulation templates and saving
- Batch simulation processing
- Advanced export formats
- Integration with external tools

### **Performance Optimization**
- Simulation speed controls
- Memory usage optimization
- Larger scale simulations

## 🎯 Use Cases

### **Research & Development**
- Test different underwater acoustic scenarios
- Validate communication algorithms
- Generate training data for ML models

### **Education & Training**
- Demonstrate underwater acoustics principles
- Interactive learning environment
- Physics-based simulation understanding

### **Operational Planning**
- Mission parameter optimization
- Range prediction
- Environmental impact assessment

## 🛠️ Technical Details

### **Architecture**
- **Frontend:** tkinter-based GUI with threaded simulation
- **Backend:** Physics-based simulation engine
- **Configuration:** Modular acoustic parameter system
- **Export:** CSV and text format support

### **Performance**
- Non-blocking simulation execution
- Real-time progress monitoring
- Memory-efficient data handling
- Cross-platform compatibility

### **Requirements**
- Python 3.7+
- tkinter (included with Python)
- numpy (for statistics)
- All simulation modules (models/, protocol/)

## 🎉 Getting the Most Out of the GUI

### **🔬 For Research**
1. Use **Configuration Comparison** to test multiple scenarios
2. Export ML training data for algorithm development
3. Analyze communication patterns with different parameters

### **📚 For Learning**
1. Start with **Quick Demo** to see basic functionality
2. Experiment with different configurations
3. Observe how physics parameters affect performance

### **🎯 For Operations**
1. Configure realistic operational parameters
2. Run extended simulations for mission planning
3. Export results for integration with other tools

---

## 🎊 Enjoy Your Beautiful GUI!

This interface transforms the powerful underwater acoustic simulation into an intuitive, visual experience. Whether you're conducting research, learning about underwater acoustics, or planning missions, the GUI provides all the tools you need in a beautiful, easy-to-use package!

**Happy Simulating! 🌊🔬📊** 