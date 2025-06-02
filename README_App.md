# 🌊 UUV Communication Simulator.app

## Overview

The **UUV Communication Simulator** is a macOS application for simulating underwater acoustic communication between unmanned underwater vehicles (UUVs) and surface ships. This application provides a comprehensive simulation environment with realistic physics-based acoustic propagation modeling.

## Features

### 🎯 **Complete Simulation Environment**
- **Real-time mission control dashboard** with live telemetry
- **Physics-based acoustic propagation** modeling
- **Interactive parameter configuration** with educational tooltips
- **Comprehensive data export** (7 CSV datasets + mission reports)

### 🔧 **Advanced Configuration Options**
- **7 acoustic presets**: Default, Shallow Water, Deep Water, High Noise, Low Power, Harsh Environment, Realistic Testing
- **Custom acoustic parameters**: Power, frequency, noise levels, SNR requirements
- **Experimental mission parameters**: Vehicle speeds, detection ranges, world size
- **Real-time parameter modification** without code changes

### 📊 **Professional Results & Analysis**
- **Mission control dashboard** with 12 live metrics
- **Sci-fi styled logging** with color-coded messages
- **Ultra-detailed mission reports** matching research standards
- **ML-ready datasets** for machine learning applications

## Installation

### Requirements
- **macOS 10.9** or later
- **No additional software required** - fully self-contained application

### Installation Steps

1. **Download** the `UUV Communication Simulator.app` from the releases
2. **Move** the application to your Applications folder
3. **Right-click** and select "Open" (first launch only, due to macOS security)
4. **Allow** the application to run when prompted by macOS

### Security Note
If macOS prevents the app from running due to security settings:
1. Go to **System Preferences** → **Security & Privacy**
2. Click **"Open Anyway"** for UUV Communication Simulator
3. Alternatively, run: `xattr -rd com.apple.quarantine "UUV Communication Simulator.app"`

## Usage Guide

### 🚀 **Quick Start**
1. Launch the application
2. Click **"🚀 Quick Demo"** on the home screen
3. Navigate to **Simulation** tab and click **"🚀 Start Simulation"**
4. Watch real-time progress in the **Monitor** tab
5. Review results in the **Results** tab

### 🔧 **Custom Configuration**
1. Go to **Configuration** tab
2. Select from **7 acoustic presets** or create custom settings
3. Adjust **🧪 Experimental Parameters** for advanced control
4. Click **"Apply Experimental Parameters"**
5. Run simulation with your custom settings

### 📊 **Data Export**
1. Complete a simulation
2. Go to **Results** tab
3. Click **"💾 Export All CSV Files"**
4. Choose export location
5. Access **7 CSV files** + mission report + metadata

## Application Structure

```
UUV Communication Simulator.app/
├── Contents/
│   ├── MacOS/              # Executable binaries
│   ├── Resources/          # Python runtime and modules
│   │   ├── models/         # Simulation models
│   │   └── lib/            # Python libraries
│   ├── Frameworks/         # Required frameworks
│   └── Info.plist         # Application metadata
```

## Exported Data Format

When you export simulation data, you'll get:

### **📁 Standard Simulation Data**
- `simulation_log.csv` - Complete event timeline
- `objects_summary.csv` - Detection results  
- `detections_timeline.csv` - Detection events
- `communication_stats.csv` - Communication metrics

### **🤖 ML Training Data**
- `packet_prediction.csv` - Packet success features
- `packet_prediction_sequences.csv` - Time series data
- `packet_prediction_quality_timeline.csv` - Signal quality

### **📋 Reports**
- `mission_report.txt` - Detailed analysis
- `simulation_results.json` - Complete results data
- `export_info.txt` - Export documentation

## Technical Specifications

### **Acoustic Physics Engine**
- **Transmission power**: 150-190 dB re 1 μPa
- **Frequency range**: 5-50 kHz
- **Noise modeling**: 30-80 dB ambient noise
- **Propagation models**: Spherical/cylindrical spreading
- **Environmental effects**: Site anomalies, absorption

### **Simulation Parameters**
- **World size**: 500-5000m configurable
- **Vehicle dynamics**: Realistic submarine movement
- **Detection range**: 20-150m sensors
- **Communication range**: Physics-based calculation
- **Mission duration**: 1k-100k simulation ticks

### **Real-time Monitoring**
- **Mission progress**: Live percentage tracking
- **Communication stats**: Success rates, packet loss
- **Vehicle telemetry**: Position, depth, heading
- **Environmental data**: Signal strength, range

## Troubleshooting

### **Application Won't Launch**
- Check macOS version (requires 10.9+)
- Run security bypass: `xattr -rd com.apple.quarantine "UUV Communication Simulator.app"`
- Try launching from Terminal: `open "UUV Communication Simulator.app"`

### **Simulation Issues**
- Ensure sufficient disk space for exports
- Check parameter ranges (use tooltips for guidance)
- Try Quick Demo first to verify functionality

### **Export Problems**
- Verify write permissions to export directory
- Ensure sufficient disk space (exports can be 10-50MB)
- Check that simulation completed successfully

## Support & Development

### **Thesis Project**
This application was developed as part of a thesis project on underwater acoustic communication simulation.

### **Technical Details**
- **Built with**: Python 3.11, tkinter, py2app
- **Physics engine**: Custom acoustic propagation modeling
- **Export formats**: CSV, JSON, TXT
- **Architecture**: Universal binary (Intel + Apple Silicon)

### **Contributing**
For technical issues or improvements, refer to the source code repository.

## Version Information

- **Version**: 1.0.0
- **Build date**: 2024
- **Compatibility**: macOS 10.9+
- **Architecture**: Universal (x86_64 + arm64)

---

**🌊 Dive into realistic underwater acoustic communication simulation!** 