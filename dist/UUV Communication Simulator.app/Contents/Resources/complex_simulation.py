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
from models.acoustic_config import (
    DEFAULT_CONFIG, HARSH_ENVIRONMENT_CONFIG, SHALLOW_WATER_CONFIG, 
    DEEP_WATER_CONFIG, HIGH_NOISE_CONFIG, LOW_POWER_CONFIG, AcousticPhysicsConfig
)

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
    print("  • Configurable underwater acoustic physics models")
    print("=" * 80)

def display_available_configurations():
    """Display all available physics configurations"""
    print("\n📡 AVAILABLE ACOUSTIC CONFIGURATIONS:")
    print("=" * 60)
    
    configs = {
        '1': ('DEFAULT (Optimal)', DEFAULT_CONFIG),
        '2': ('SHALLOW WATER', SHALLOW_WATER_CONFIG),
        '3': ('DEEP WATER', DEEP_WATER_CONFIG),
        '4': ('HIGH NOISE ENVIRONMENT', HIGH_NOISE_CONFIG),
        '5': ('LOW POWER OPERATION', LOW_POWER_CONFIG),
        '6': ('HARSH ENVIRONMENT', HARSH_ENVIRONMENT_CONFIG)
    }
    
    for key, (name, config) in configs.items():
        print(f"{key}. {name}")
        print(f"   Power: {config.transmission_power_db} dB re 1 μPa")
        print(f"   Freq:  {config.frequency_hz/1000:.1f} kHz")
        print(f"   Noise: {config.noise_level_db} dB re 1 μPa")
        print(f"   SNR:   {config.required_snr_db} dB")
        print(f"   Spread:{config.spreading_exponent}")
        if config.site_anomaly_db != 0:
            print(f"   Anomaly: {config.site_anomaly_db:+.1f} dB")
        print()
    
    return configs

def select_configuration():
    """Interactive configuration selection"""
    configs = display_available_configurations()
    
    while True:
        try:
            choice = input("🎯 Select configuration (1-6) or 'c' for custom: ").strip().lower()
            
            if choice == 'c':
                return create_custom_configuration()
            elif choice in configs:
                selected_name, selected_config = configs[choice]
                print(f"\n✅ Selected: {selected_name}")
                return selected_config
            else:
                print("❌ Invalid choice. Please select 1-6 or 'c' for custom.")
        except KeyboardInterrupt:
            print("\n🚫 Configuration selection cancelled.")
            return DEFAULT_CONFIG

def create_custom_configuration():
    """Create a custom configuration interactively"""
    print("\n🛠️  CUSTOM CONFIGURATION BUILDER")
    print("=" * 40)
    print("Enter values (press Enter for defaults):")
    
    try:
        # Get user inputs with defaults
        power = input(f"Transmission power (default 170.0 dB re 1 μPa): ").strip()
        power = float(power) if power else 170.0
        
        freq = input(f"Frequency (default 12000 Hz): ").strip()
        freq = float(freq) if freq else 12000.0
        
        noise = input(f"Noise level (default 50.0 dB re 1 μPa): ").strip()
        noise = float(noise) if noise else 50.0
        
        snr = input(f"Required SNR (default 10.0 dB): ").strip()
        snr = float(snr) if snr else 10.0
        
        spreading = input(f"Spreading exponent (default 1.5): ").strip()
        spreading = float(spreading) if spreading else 1.5
        
        anomaly = input(f"Site anomaly (default 0.0 dB): ").strip()
        anomaly = float(anomaly) if anomaly else 0.0
        
        # Create custom configuration
        custom_config = AcousticPhysicsConfig(
            transmission_power_db=power,
            frequency_hz=freq,
            noise_level_db=noise,
            required_snr_db=snr,
            spreading_exponent=spreading,
            site_anomaly_db=anomaly
        )
        
        print(f"\n✅ Custom configuration created!")
        print(f"   Power: {custom_config.transmission_power_db} dB re 1 μPa")
        print(f"   Freq:  {custom_config.frequency_hz/1000:.1f} kHz")
        print(f"   Noise: {custom_config.noise_level_db} dB re 1 μPa")
        print(f"   SNR:   {custom_config.required_snr_db} dB")
        print(f"   Spread:{custom_config.spreading_exponent}")
        print(f"   Anomaly: {custom_config.site_anomaly_db:+.1f} dB")
        
        return custom_config
        
    except (ValueError, KeyboardInterrupt):
        print("\n❌ Invalid input or cancelled. Using default configuration.")
        return DEFAULT_CONFIG

def run_complex_simulation(num_ticks: int = 5000, world_size: float = 1000.0, config: AcousticPhysicsConfig = None):
    """Run the complex simulation with all features"""
    
    print_simulation_banner()
    
    # Initialize simulation
    print(f"\n🚀 Initializing simulation...")
    print(f"   World size: {world_size}m x {world_size}m")
    print(f"   Simulation duration: {num_ticks} ticks")
    
    controller = SimulationController(world_size=world_size)
    
    # Apply selected configuration if provided
    if config is not None:
        print(f"\n🔧 Applying custom acoustic configuration...")
        controller.communication_model.update_physics_config(config)
        print(f"   ✅ Configuration applied successfully!")
    
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
    print(f"\n📡 Active Communication Configuration:")
    print(f"   Frequency: {comm_model.frequency/1000:.1f} kHz")
    print(f"   Transmission power: {comm_model.transmission_power} dB re 1 μPa")
    print(f"   Noise level: {comm_model.noise_level} dB re 1 μPa")
    print(f"   Required SNR: {comm_model.physics_config.required_snr_db} dB")
    print(f"   Spreading exponent: {comm_model.physics_config.spreading_exponent}")
    print(f"   Site anomaly: {comm_model.physics_config.site_anomaly_db:+.1f} dB")
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
        
        # Export data with configuration info
        config_name = get_config_name(config) if config else "default"
        print(f"\n📊 Exporting simulation data...")
        
        # Standard CSV exports
        logger = CSVLogger(f"uuv_simulation_{config_name}")
        logger.export_all(controller)
        
        # ML-optimized exports  
        ml_logger = MLOptimizedCSVLogger(f"packet_prediction_{config_name}")
        ml_logger.export_all_ml_data(controller)
        
        return controller, final_report
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Simulation interrupted by user")
        simulation_time = time.time() - start_time
        print(f"   Ran for {simulation_time:.2f} seconds ({controller.game_state.tick} ticks)")
        
        # Still export partial data
        config_name = get_config_name(config) if config else "default"
        logger = CSVLogger(f"uuv_simulation_{config_name}_partial")
        logger.export_all(controller)
        
        ml_logger = MLOptimizedCSVLogger(f"packet_prediction_{config_name}_partial")
        ml_logger.export_all_ml_data(controller)
        
        return controller, None

def get_config_name(config: AcousticPhysicsConfig) -> str:
    """Get a descriptive name for the configuration"""
    if config == DEFAULT_CONFIG:
        return "default"
    elif config == SHALLOW_WATER_CONFIG:
        return "shallow_water"
    elif config == DEEP_WATER_CONFIG:
        return "deep_water"
    elif config == HIGH_NOISE_CONFIG:
        return "high_noise"
    elif config == LOW_POWER_CONFIG:
        return "low_power"
    elif config == HARSH_ENVIRONMENT_CONFIG:
        return "harsh_environment"
    else:
        return "custom"

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
    config = select_configuration()
    return run_complex_simulation(num_ticks=1000, world_size=800.0, config=config)

def run_full_mission():
    """Run a full mission simulation"""
    print("🚀 Running full mission (5000 ticks)...")
    config = select_configuration()
    return run_complex_simulation(num_ticks=5000, world_size=1000.0, config=config)

def run_extended_mission():
    """Run an extended mission for comprehensive analysis"""
    print("🚀 Running extended mission (10000 ticks)...")
    config = select_configuration()
    return run_complex_simulation(num_ticks=10000, world_size=1200.0, config=config)

def run_ml_training_mission():
    """Run a mission optimized for ML training data collection"""
    print("🚀 Running ML training mission (15000 ticks)...")
    config = select_configuration()
    return run_complex_simulation(num_ticks=15000, world_size=1500.0, config=config)

def run_custom_mission():
    """Run a custom mission with user-defined parameters"""
    print("🚀 Custom Mission Setup")
    print("=" * 30)
    
    try:
        # Get simulation parameters
        num_ticks = input("Number of ticks (default 5000): ").strip()
        num_ticks = int(num_ticks) if num_ticks else 5000
        
        world_size = input("World size in meters (default 1000): ").strip()
        world_size = float(world_size) if world_size else 1000.0
        
        # Get configuration
        config = select_configuration()
        
        print(f"\n🎯 Starting custom mission:")
        print(f"   Ticks: {num_ticks:,}")
        print(f"   World size: {world_size:.0f}m")
        
        return run_complex_simulation(num_ticks=num_ticks, world_size=world_size, config=config)
        
    except (ValueError, KeyboardInterrupt):
        print("\n❌ Invalid input or cancelled. Running default mission.")
        return run_full_mission()

def run_configuration_comparison():
    """Run multiple simulations with different configurations for comparison"""
    print("🔬 CONFIGURATION COMPARISON STUDY")
    print("=" * 50)
    print("This will run multiple simulations with different configurations")
    print("for performance comparison. Results will be saved separately.")
    
    try:
        num_ticks = input("\nNumber of ticks per simulation (default 2000): ").strip()
        num_ticks = int(num_ticks) if num_ticks else 2000
        
        world_size = input("World size in meters (default 1000): ").strip()
        world_size = float(world_size) if world_size else 1000.0
        
    except (ValueError, KeyboardInterrupt):
        print("❌ Invalid input. Using defaults.")
        num_ticks = 2000
        world_size = 1000.0
    
    configs_to_test = [
        ("OPTIMAL", DEFAULT_CONFIG),
        ("SHALLOW_WATER", SHALLOW_WATER_CONFIG),
        ("DEEP_WATER", DEEP_WATER_CONFIG),
        ("HIGH_NOISE", HIGH_NOISE_CONFIG),
        ("HARSH_ENVIRONMENT", HARSH_ENVIRONMENT_CONFIG)
    ]
    
    results = {}
    
    for config_name, config in configs_to_test:
        print(f"\n🧪 Testing {config_name} configuration...")
        print(f"   Ticks: {num_ticks:,}, World: {world_size:.0f}m")
        
        try:
            controller, final_report = run_complex_simulation(
                num_ticks=num_ticks, 
                world_size=world_size, 
                config=config
            )
            
            if final_report:
                results[config_name] = {
                    'config': config,
                    'report': final_report,
                    'controller': controller
                }
                
                # Quick summary
                comm_stats = final_report['communication_stats']
                print(f"   ✅ Success rate: {comm_stats['overall_communication_success']:.1%}")
        
        except KeyboardInterrupt:
            print(f"\n⚠️  {config_name} test interrupted by user")
            break
    
    # Print comparison summary
    if results:
        print_comparison_summary(results)
    
    return results

def print_comparison_summary(results: dict):
    """Print a summary comparison of different configurations"""
    print("\n📊 CONFIGURATION COMPARISON SUMMARY")
    print("=" * 60)
    print(f"{'Configuration':<20} {'Success Rate':<12} {'Avg Delay':<10} {'Detections':<10}")
    print("-" * 60)
    
    for config_name, result in results.items():
        comm_stats = result['report']['communication_stats']
        sim_summary = result['report']['simulation_summary']
        
        success_rate = comm_stats['overall_communication_success'] * 100
        avg_delay = comm_stats['average_total_delay_ms']
        detections = sim_summary['objects_detected']
        
        print(f"{config_name:<20} {success_rate:>10.1f}% {avg_delay:>8.1f}ms {detections:>8d}")

def interactive_simulation_launcher():
    """Interactive menu for launching different types of simulations"""
    while True:
        print("\n🌊 UUV COMMUNICATION SIMULATION LAUNCHER 🌊")
        print("=" * 50)
        print("1. Quick Demo (1000 ticks)")
        print("2. Full Mission (5000 ticks)")
        print("3. Extended Mission (10000 ticks)")
        print("4. ML Training Mission (15000 ticks)")
        print("5. Custom Mission (user-defined)")
        print("6. Configuration Comparison Study")
        print("7. View Available Configurations")
        print("0. Exit")
        print("-" * 50)
        
        try:
            choice = input("🎯 Select option (0-7): ").strip()
            
            if choice == '0':
                print("👋 Goodbye!")
                break
            elif choice == '1':
                run_quick_demo()
            elif choice == '2':
                run_full_mission()
            elif choice == '3':
                run_extended_mission()
            elif choice == '4':
                run_ml_training_mission()
            elif choice == '5':
                run_custom_mission()
            elif choice == '6':
                run_configuration_comparison()
            elif choice == '7':
                display_available_configurations()
                input("\nPress Enter to continue...")
            else:
                print("❌ Invalid choice. Please select 0-7.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Simulation launcher exited.")
            break

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
            run_quick_demo()
        elif mode == "full":
            run_full_mission()
        elif mode == "extended":
            run_extended_mission()
        elif mode == "ml":
            run_ml_training_mission()
        elif mode == "custom":
            run_custom_mission()
        elif mode == "compare":
            run_configuration_comparison()
        elif mode == "interactive":
            interactive_simulation_launcher()
        elif mode == "autorun":
            # Non-interactive mode for automation
            if len(sys.argv) >= 4:
                ticks = int(sys.argv[2])
                world_size = float(sys.argv[3])
                config_name = sys.argv[4] if len(sys.argv) > 4 else "default"
                
                # Select config based on name
                config_map = {
                    "default": DEFAULT_CONFIG,
                    "shallow": SHALLOW_WATER_CONFIG,
                    "deep": DEEP_WATER_CONFIG,
                    "noise": HIGH_NOISE_CONFIG,
                    "low_power": LOW_POWER_CONFIG,
                    "harsh": HARSH_ENVIRONMENT_CONFIG
                }
                
                config = config_map.get(config_name, DEFAULT_CONFIG)
                print(f"🤖 Automated run: {ticks} ticks, {world_size}m world, {config_name} config")
                controller, report = run_complex_simulation(ticks, world_size, config)
                print_ml_data_info()
            else:
                print("Usage: python complex_simulation.py autorun <ticks> <world_size> [config_name]")
                print("Config names: default, shallow, deep, noise, low_power, harsh")
        else:
            print("🌊 UUV Communication Simulation")
            print("Available modes:")
            print("  demo      - Quick demo (1000 ticks)")
            print("  full      - Full mission (5000 ticks)")
            print("  extended  - Extended mission (10000 ticks)")
            print("  ml        - ML training mission (15000 ticks)")
            print("  custom    - Custom mission (interactive)")
            print("  compare   - Configuration comparison study")
            print("  interactive - Launch interactive menu")
            print("  autorun   - Non-interactive automation mode")
            print("\nExample:")
            print("  python complex_simulation.py demo")
            print("  python complex_simulation.py autorun 2000 800 harsh")
    else:
        # Default: launch interactive menu
        interactive_simulation_launcher() 