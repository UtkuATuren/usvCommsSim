#!/usr/bin/env python3
"""
Complex UUV Communication Simulation with Realistic Loss Function

This simulation creates a realistic underwater environment where:
- A ship and submarine operate in a simulated world with realistic physics
- The submarine searches for and detects random objects (5-15 objects)
- All new commands (ASCEND, DESCEND, REPORT_STATUS) are implemented
- Realistic underwater acoustic communication with multi-path propagation
- Environmental sensors provide comprehensive status reporting
- ML-optimized data export for packet loss prediction models
- Safety constraints prevent submarine from going too far from ship
"""

import json
import time
from models.simulation_controller import SimulationController
from models.csv_logger import CSVLogger
from models.ml_csv_logger import MLOptimizedCSVLogger

def print_simulation_banner():
    """Print a nice banner for the simulation"""
    print("=" * 80)
    print("🌊 ADVANCED UUV COMMUNICATION SIMULATION 🌊")
    print("=" * 80)
    print("Features:")
    print("  • Realistic 3D underwater environment with physics")
    print("  • Ship and submarine with environmental sensors")
    print("  • Random object detection (5-15 objects per mission)")
    print("  • All command types: MOVE, TURN, STOP, ASCEND, DESCEND, REPORT_STATUS")
    print("  • Realistic underwater acoustic communication model")
    print("  • Multi-path propagation and environmental attenuation")
    print("  • Packet timing and delay simulation")
    print("  • Safety constraints and intelligent mission planning")
    print("  • ML-optimized data export for packet loss prediction")
    print("=" * 80)

def run_complex_simulation(num_ticks: int = 5000, world_size: float = 1000.0):
    """Run the complex simulation with all features"""
    
    print_simulation_banner()
    
    # Initialize simulation
    print(f"\n🚀 Initializing simulation...")
    print(f"   World size: {world_size}m x {world_size}m")
    print(f"   Simulation duration: {num_ticks} ticks")
    
    controller = SimulationController(world_size=world_size)
    
    # Print initial state
    print(f"\n📍 Initial State:")
    print(f"   Ship position: (0, 0, 0)")
    print(f"   Submarine position: ({controller.game_state.submarine.position.x:.1f}, "
          f"{controller.game_state.submarine.position.y:.1f}, "
          f"{controller.game_state.submarine.position.z:.1f})")
    print(f"   Submarine depth: {controller.game_state.submarine.depth:.1f}m")
    print(f"   Objects to detect: {len(controller.game_state.objects)}")
    print(f"   Max safe distance: {controller.game_state.submarine.max_safe_distance_from_ship}m")
    
    # Show object types
    object_types = {}
    for obj in controller.game_state.objects:
        object_types[obj.object_type] = object_types.get(obj.object_type, 0) + 1
    
    print(f"   Object distribution: {dict(object_types)}")
    
    # Print communication model parameters
    comm_model = controller.communication_model
    print(f"\n📡 Communication Model:")
    print(f"   Frequency: {comm_model.frequency/1000:.1f} kHz")
    print(f"   Transmission power: {comm_model.transmission_power} dB re 1 μPa")
    print(f"   Noise level: {comm_model.noise_level} dB re 1 μPa")
    print(f"   Max reliable range: {comm_model.max_reliable_range}m")
    print(f"   Data rate: {comm_model.data_rate} bps")
    
    # Print environmental conditions
    env = comm_model.environment
    print(f"\n🌊 Environmental Conditions:")
    print(f"   Water temperature: {env.water_temperature}°C")
    print(f"   Sea state: {controller.game_state.sea_state}")
    print(f"   Salinity: {env.salinity} ppt")
    print(f"   Sound velocity: {env.sound_velocity} m/s")
    
    # Run simulation
    print(f"\n🎯 Starting mission simulation...")
    start_time = time.time()
    
    try:
        final_report = controller.run_simulation(num_ticks)
        simulation_time = time.time() - start_time
        
        # Print results
        print(f"\n✅ Simulation completed in {simulation_time:.2f} seconds")
        print_final_report(final_report)
        
        # Export data
        print(f"\n📊 Exporting simulation data...")
        
        # Standard CSV exports
        logger = CSVLogger("uuv_simulation")
        logger.export_all(controller)
        
        # ML-optimized exports
        ml_logger = MLOptimizedCSVLogger("packet_prediction")
        ml_logger.export_all_ml_data(controller)
        
        return controller, final_report
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Simulation interrupted by user")
        simulation_time = time.time() - start_time
        print(f"   Ran for {simulation_time:.2f} seconds ({controller.game_state.tick} ticks)")
        
        # Still export partial data
        logger = CSVLogger("uuv_simulation_partial")
        logger.export_all(controller)
        
        ml_logger = MLOptimizedCSVLogger("packet_prediction_partial")
        ml_logger.export_all_ml_data(controller)
        
        return controller, None

def print_final_report(report: dict):
    """Print a formatted final report"""
    sim_summary = report["simulation_summary"]
    comm_stats = report["communication_stats"]
    
    print("\n" + "=" * 60)
    print("📋 MISSION REPORT")
    print("=" * 60)
    
    print(f"🎯 Mission Results:")
    print(f"   Total ticks: {sim_summary['total_ticks']:,}")
    print(f"   Distance traveled: {sim_summary['total_distance_traveled']:.1f}m")
    print(f"   Objects detected: {sim_summary['objects_detected']}/{sim_summary['total_objects']}")
    print(f"   Detection rate: {sim_summary['detection_rate']:.1%}")
    print(f"   Max distance from ship: {sim_summary['max_distance_from_ship']:.1f}m")
    
    print(f"\n📍 Final Position:")
    final_pos = sim_summary['final_position']
    print(f"   Position: ({final_pos[0]:.1f}, {final_pos[1]:.1f}, {final_pos[2]:.1f})")
    print(f"   Depth: {sim_summary['final_depth']:.1f}m")
    print(f"   Heading: {sim_summary['final_heading']:.1f}°")
    
    print(f"\n📡 Communication Performance:")
    print(f"   Overall success rate: {comm_stats['overall_communication_success']:.1%}")
    print(f"   Command success rate: {comm_stats['command_success_rate']:.1%}")
    print(f"   Status success rate: {comm_stats['status_success_rate']:.1%}")
    print(f"   Commands sent/received: {comm_stats['commands_sent']}/{comm_stats['commands_received']}")
    print(f"   Status sent/received: {comm_stats['status_sent']}/{comm_stats['status_received']}")
    print(f"   Average propagation delay: {comm_stats['average_propagation_delay_ms']:.1f}ms")
    print(f"   Average total delay: {comm_stats['average_total_delay_ms']:.1f}ms")
    print(f"   Total communication events: {comm_stats['total_communication_events']:,}")
    
    print(f"\n🔍 Object Detection Details:")
    detected_objects = [obj for obj in report["objects"] if obj["detected"]]
    undetected_objects = [obj for obj in report["objects"] if not obj["detected"]]
    
    if detected_objects:
        print(f"   Detected objects:")
        for obj in detected_objects:
            pos = obj["position"]
            print(f"     • {obj['type']} #{obj['id']} at ({pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f})")
    
    if undetected_objects:
        print(f"   Missed objects:")
        for obj in undetected_objects[:5]:  # Show first 5
            pos = obj["position"]
            print(f"     • {obj['type']} #{obj['id']} at ({pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f})")
        if len(undetected_objects) > 5:
            print(f"     ... and {len(undetected_objects) - 5} more")
    
    print(f"\n📈 Statistics:")
    print(f"   Total events logged: {report['total_events']:,}")
    print(f"   Detection events: {report['detection_events']}")
    
    print("=" * 60)

def run_quick_demo():
    """Run a quick demonstration of the simulation"""
    print("🚀 Running quick demo (1000 ticks)...")
    return run_complex_simulation(num_ticks=1000, world_size=800.0)

def run_full_mission():
    """Run a full mission simulation"""
    print("🚀 Running full mission (5000 ticks)...")
    return run_complex_simulation(num_ticks=5000, world_size=1000.0)

def run_extended_mission():
    """Run an extended mission for comprehensive analysis"""
    print("🚀 Running extended mission (10000 ticks)...")
    return run_complex_simulation(num_ticks=10000, world_size=1200.0)

def run_ml_training_mission():
    """Run a mission optimized for ML training data collection"""
    print("🚀 Running ML training mission (15000 ticks)...")
    return run_complex_simulation(num_ticks=15000, world_size=1500.0)

def print_ml_data_info():
    """Print information about the ML datasets generated"""
    print("\n" + "=" * 60)
    print("🤖 MACHINE LEARNING DATASETS")
    print("=" * 60)
    print("The following datasets have been generated for ML model training:")
    print()
    print("📁 outputs/ml_training_data/")
    print()
    print("1. 📊 packet_prediction.csv")
    print("   • Main training dataset with 50+ features")
    print("   • Target: packet_lost (binary classification)")
    print("   • Features: temporal, environmental, communication, movement")
    print("   • Use for: Packet loss prediction models")
    print()
    print("2. 📈 packet_prediction_sequences.csv")
    print("   • Time series data for sequence analysis")
    print("   • Target: packet_lost, delay_ms")
    print("   • Use for: LSTM/RNN models, time series forecasting")
    print()
    print("3. 📉 packet_prediction_quality_timeline.csv")
    print("   • Communication quality trends over time")
    print("   • Target: packet_loss_probability, quality_trend")
    print("   • Use for: Communication quality prediction")
    print()
    print("📁 outputs/standard_simulation/")
    print("   • uuv_simulation_log.csv - Complete event log")
    print("   • uuv_simulation_objects.csv - Object detection summary")
    print("   • uuv_simulation_detections.csv - Detection timeline")
    print("   • uuv_simulation_communication.csv - Communication stats")
    print()
    print("🎯 Recommended ML Approaches:")
    print("   • Random Forest/XGBoost for packet loss prediction")
    print("   • LSTM for sequence-based prediction")
    print("   • Time series analysis for communication quality trends")
    print("   • Multi-class classification for loss_reason prediction")
    print("=" * 60)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == "demo":
            controller, report = run_quick_demo()
            print_ml_data_info()
        elif mode == "full":
            controller, report = run_full_mission()
            print_ml_data_info()
        elif mode == "extended":
            controller, report = run_extended_mission()
            print_ml_data_info()
        elif mode == "ml":
            controller, report = run_ml_training_mission()
            print_ml_data_info()
        elif mode == "custom":
            if len(sys.argv) >= 4:
                ticks = int(sys.argv[2])
                world_size = float(sys.argv[3])
                controller, report = run_complex_simulation(ticks, world_size)
                print_ml_data_info()
            else:
                print("Usage: python complex_simulation.py custom <ticks> <world_size>")
        else:
            print("Available modes: demo, full, extended, ml, custom")
    else:
        # Default: run demo
        controller, report = run_quick_demo()
        print_ml_data_info() 