import csv
import time
import os
from typing import List, Dict, Optional
from models.simulation_controller import SimulationEvent, SimulationController

class MLOptimizedCSVLogger:
    """CSV logger optimized for machine learning model training on packet loss prediction"""
    
    def __init__(self, base_filename: str = "ml_training_data"):
        self.base_filename = base_filename
        # Ensure output directory exists
        os.makedirs("outputs/ml_training_data", exist_ok=True)
        
    def export_ml_training_data(self, controller: SimulationController, filename: str = None):
        """Export data optimized for ML training on packet loss prediction"""
        if filename is None:
            filename = f"outputs/ml_training_data/{self.base_filename}.csv"
            
        # Features for ML model
        fieldnames = [
            # Temporal features
            'tick', 'timestamp', 'time_since_last_transmission',
            
            # Packet information
            'packet_id', 'packet_type', 'packet_size_bytes', 'sender', 'receiver',
            
            # Transmission timing
            'transmission_time', 'expected_arrival_time', 'actual_arrival_time',
            'propagation_delay_ms', 'multipath_delay_ms', 'total_delay_ms',
            
            # Position and distance features
            'ship_x', 'ship_y', 'ship_z', 'submarine_x', 'submarine_y', 'submarine_z',
            'distance_2d', 'distance_3d', 'depth_difference', 'horizontal_distance',
            
            # Environmental features
            'water_temperature', 'sea_state', 'submarine_depth', 'pressure',
            'light_level', 'turbidity', 'current_speed', 'current_direction',
            'salinity', 'ph_level', 'dissolved_oxygen',
            
            # Communication quality features
            'signal_strength', 'snr_db', 'propagation_loss_db', 'sound_velocity',
            
            # Movement and state features
            'submarine_heading', 'submarine_state', 'submarine_speed',
            'distance_from_safe_zone', 'heading_to_ship', 'relative_velocity',
            
            # Historical features (sliding window)
            'packets_sent_last_10', 'packets_lost_last_10', 'success_rate_last_10',
            'avg_delay_last_10', 'distance_trend_last_5',
            
            # Target variables
            'packet_lost', 'loss_reason', 'packet_received', 'delay_category',
            
            # Additional context
            'command_type', 'command_param', 'execution_success', 'mission_phase'
        ]
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Track historical data for sliding window features
            transmission_history = []
            last_transmission_time = {}
            
            for event in controller.events:
                if event.event_type in ['command', 'status']:
                    # Extract basic packet information
                    packet_data = self._extract_packet_features(event, controller)
                    
                    # Calculate temporal features
                    temporal_features = self._calculate_temporal_features(
                        event, transmission_history, last_transmission_time)
                    
                    # Calculate environmental features
                    env_features = self._extract_environmental_features(event, controller)
                    
                    # Calculate communication quality features
                    comm_features = self._extract_communication_features(event, controller)
                    
                    # Calculate movement and state features
                    movement_features = self._calculate_movement_features(event, controller)
                    
                    # Calculate historical features
                    historical_features = self._calculate_historical_features(
                        transmission_history, event.tick)
                    
                    # Calculate target variables
                    target_features = self._calculate_target_variables(event)
                    
                    # Combine all features
                    row = {
                        **packet_data,
                        **temporal_features,
                        **env_features,
                        **comm_features,
                        **movement_features,
                        **historical_features,
                        **target_features
                    }
                    
                    writer.writerow(row)
                    
                    # Update history
                    transmission_history.append({
                        'tick': event.tick,
                        'lost': event.data.get('lost', False),
                        'delay': event.data.get('total_delay', 0),
                        'distance': event.data.get('distance', 0),
                        'packet_type': event.event_type
                    })
                    
                    # Keep only last 50 transmissions for efficiency
                    if len(transmission_history) > 50:
                        transmission_history.pop(0)
                    
                    # Update last transmission time
                    packet_type = event.event_type
                    last_transmission_time[packet_type] = event.data.get('transmission_time', 0)
        
        print(f"ML training data exported to {filename}")
    
    def _extract_packet_features(self, event: SimulationEvent, controller: SimulationController) -> Dict:
        """Extract basic packet information features"""
        return {
            'tick': event.tick,
            'timestamp': event.timestamp,
            'packet_id': event.data.get('packet_id', ''),
            'packet_type': event.event_type,
            'packet_size_bytes': event.data.get('raw_packet_size', 0),
            'sender': 'ship' if event.event_type == 'command' else 'submarine',
            'receiver': 'submarine' if event.event_type == 'command' else 'ship'
        }
    
    def _calculate_temporal_features(self, event: SimulationEvent, 
                                   history: List[Dict], 
                                   last_times: Dict) -> Dict:
        """Calculate temporal features"""
        packet_type = event.event_type
        current_time = event.data.get('transmission_time', 0)
        last_time = last_times.get(packet_type, 0)
        
        time_since_last = current_time - last_time if last_time > 0 else 0
        
        return {
            'time_since_last_transmission': time_since_last,
            'transmission_time': current_time,
            'expected_arrival_time': current_time + event.data.get('propagation_delay', 0),
            'actual_arrival_time': event.data.get('arrival_time', 0),
            'propagation_delay_ms': event.data.get('propagation_delay', 0) * 1000,
            'multipath_delay_ms': event.data.get('multipath_delay', 0) * 1000,
            'total_delay_ms': event.data.get('total_delay', 0) * 1000
        }
    
    def _extract_environmental_features(self, event: SimulationEvent, 
                                      controller: SimulationController) -> Dict:
        """Extract environmental sensor features"""
        env_data = event.data.get('environmental_sensors', {})
        
        return {
            'water_temperature': env_data.get('water_temperature', 15.0),
            'sea_state': getattr(controller.game_state, 'sea_state', 2),
            'submarine_depth': event.data.get('depth', 0),
            'pressure': env_data.get('pressure', 1013.25),
            'light_level': env_data.get('light_level', 0),
            'turbidity': env_data.get('turbidity', 1.0),
            'current_speed': env_data.get('current_speed', 0),
            'current_direction': env_data.get('current_direction', 0),
            'salinity': env_data.get('salinity', 35.0),
            'ph_level': env_data.get('ph_level', 8.1),
            'dissolved_oxygen': env_data.get('dissolved_oxygen', 6.5)
        }
    
    def _extract_communication_features(self, event: SimulationEvent, 
                                      controller: SimulationController) -> Dict:
        """Extract communication quality features"""
        distance = event.data.get('distance', 0)
        
        # Get communication quality from the model
        ship_pos = (0, 0, 0)  # Ship at origin
        sub_pos = event.data.get('position', (0, 0, 0))
        
        comm_quality = controller.communication_model.get_communication_quality(
            distance, ship_pos[2], sub_pos[2])
        
        return {
            'signal_strength': event.data.get('signal_strength', 1.0),
            'snr_db': comm_quality.get('snr_db', 0),
            'propagation_loss_db': comm_quality.get('propagation_loss_db', 0),
            'sound_velocity': comm_quality.get('sound_velocity', 1500)
        }
    
    def _calculate_movement_features(self, event: SimulationEvent, 
                                   controller: SimulationController) -> Dict:
        """Calculate movement and state features"""
        position = event.data.get('position', (0, 0, 0))
        ship_pos = (0, 0, 0)  # Ship at origin
        
        # Calculate distances
        distance_2d = ((position[0] - ship_pos[0])**2 + (position[1] - ship_pos[1])**2)**0.5
        distance_3d = event.data.get('distance', 0)
        depth_diff = abs(position[2] - ship_pos[2])
        
        # Calculate heading to ship
        import math
        dx = ship_pos[0] - position[0]
        dy = ship_pos[1] - position[1]
        heading_to_ship = math.degrees(math.atan2(dy, dx))
        heading_to_ship = (heading_to_ship + 360) % 360
        
        # Distance from safe zone
        max_safe_distance = getattr(controller.game_state.submarine, 'max_safe_distance_from_ship', 800)
        distance_from_safe_zone = max(0, distance_2d - max_safe_distance)
        
        return {
            'ship_x': ship_pos[0],
            'ship_y': ship_pos[1], 
            'ship_z': ship_pos[2],
            'submarine_x': position[0],
            'submarine_y': position[1],
            'submarine_z': position[2],
            'distance_2d': distance_2d,
            'distance_3d': distance_3d,
            'depth_difference': depth_diff,
            'horizontal_distance': distance_2d,
            'submarine_heading': event.data.get('heading', 0),
            'submarine_state': event.data.get('state', 'idle'),
            'submarine_speed': getattr(controller.game_state.submarine, 'speed', 5),
            'distance_from_safe_zone': distance_from_safe_zone,
            'heading_to_ship': heading_to_ship,
            'relative_velocity': 0  # Could be calculated from position history
        }
    
    def _calculate_historical_features(self, history: List[Dict], current_tick: int) -> Dict:
        """Calculate sliding window historical features"""
        if not history:
            return {
                'packets_sent_last_10': 0,
                'packets_lost_last_10': 0,
                'success_rate_last_10': 1.0,
                'avg_delay_last_10': 0,
                'distance_trend_last_5': 0
            }
        
        # Last 10 packets
        recent_10 = [h for h in history if current_tick - h['tick'] <= 10]
        packets_sent_10 = len(recent_10)
        packets_lost_10 = sum(1 for h in recent_10 if h['lost'])
        success_rate_10 = (packets_sent_10 - packets_lost_10) / packets_sent_10 if packets_sent_10 > 0 else 1.0
        avg_delay_10 = sum(h['delay'] for h in recent_10) / len(recent_10) if recent_10 else 0
        
        # Distance trend (last 5 packets)
        recent_5 = [h for h in history if current_tick - h['tick'] <= 5]
        if len(recent_5) >= 2:
            distance_trend = recent_5[-1]['distance'] - recent_5[0]['distance']
        else:
            distance_trend = 0
        
        return {
            'packets_sent_last_10': packets_sent_10,
            'packets_lost_last_10': packets_lost_10,
            'success_rate_last_10': success_rate_10,
            'avg_delay_last_10': avg_delay_10 * 1000,  # Convert to ms
            'distance_trend_last_5': distance_trend
        }
    
    def _calculate_target_variables(self, event: SimulationEvent) -> Dict:
        """Calculate target variables for ML training"""
        packet_lost = event.data.get('lost', False)
        loss_reason = event.data.get('loss_reason', 'none')
        packet_received = not packet_lost
        
        # Categorize delay for classification
        total_delay_ms = event.data.get('total_delay', 0) * 1000
        if total_delay_ms < 50:
            delay_category = 'very_fast'
        elif total_delay_ms < 100:
            delay_category = 'fast'
        elif total_delay_ms < 200:
            delay_category = 'normal'
        elif total_delay_ms < 500:
            delay_category = 'slow'
        else:
            delay_category = 'very_slow'
        
        # Determine mission phase based on tick
        tick = event.tick
        if tick < 100:
            mission_phase = 'initialization'
        elif tick < 500:
            mission_phase = 'exploration'
        elif tick < 1000:
            mission_phase = 'active_search'
        else:
            mission_phase = 'extended_mission'
        
        return {
            'packet_lost': packet_lost,
            'loss_reason': loss_reason,
            'packet_received': packet_received,
            'delay_category': delay_category,
            'command_type': event.data.get('command', ''),
            'command_param': event.data.get('param', 0),
            'execution_success': event.data.get('execution_reason', '') != 'packet_lost',
            'mission_phase': mission_phase
        }
    
    def export_packet_sequence_data(self, controller: SimulationController, filename: str = None):
        """Export packet sequence data for time series analysis"""
        if filename is None:
            filename = f"outputs/ml_training_data/{self.base_filename}_sequences.csv"
            
        fieldnames = [
            'sequence_id', 'packet_number', 'tick', 'packet_type', 'distance',
            'packet_lost', 'delay_ms', 'time_between_packets', 'cumulative_loss_rate'
        ]
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            sequence_id = 0
            packet_number = 0
            last_time = 0
            total_packets = 0
            lost_packets = 0
            
            for event in controller.events:
                if event.event_type in ['command', 'status']:
                    total_packets += 1
                    if event.data.get('lost', False):
                        lost_packets += 1
                    
                    current_time = event.data.get('transmission_time', 0)
                    time_between = current_time - last_time if last_time > 0 else 0
                    
                    cumulative_loss_rate = lost_packets / total_packets if total_packets > 0 else 0
                    
                    writer.writerow({
                        'sequence_id': sequence_id,
                        'packet_number': packet_number,
                        'tick': event.tick,
                        'packet_type': event.event_type,
                        'distance': event.data.get('distance', 0),
                        'packet_lost': event.data.get('lost', False),
                        'delay_ms': event.data.get('total_delay', 0) * 1000,
                        'time_between_packets': time_between,
                        'cumulative_loss_rate': cumulative_loss_rate
                    })
                    
                    packet_number += 1
                    last_time = current_time
                    
                    # Start new sequence every 100 packets
                    if packet_number % 100 == 0:
                        sequence_id += 1
                        packet_number = 0
        
        print(f"Packet sequence data exported to {filename}")
    
    def export_communication_quality_timeline(self, controller: SimulationController, filename: str = None):
        """Export communication quality metrics over time for trend analysis"""
        if filename is None:
            filename = f"outputs/ml_training_data/{self.base_filename}_quality_timeline.csv"
            
        fieldnames = [
            'tick', 'timestamp', 'distance', 'snr_db', 'propagation_loss_db',
            'packet_loss_probability', 'signal_strength', 'sea_state',
            'water_temperature', 'submarine_depth', 'quality_trend'
        ]
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            quality_history = []
            
            for event in controller.events:
                if event.event_type == 'communication':
                    quality_data = event.data
                    
                    # Calculate quality trend
                    current_loss_prob = quality_data.get('packet_loss_probability', 0)
                    if len(quality_history) >= 3:
                        recent_probs = [q['packet_loss_probability'] for q in quality_history[-3:]]
                        avg_recent = sum(recent_probs) / len(recent_probs)
                        quality_trend = 'improving' if current_loss_prob < avg_recent else 'degrading'
                    else:
                        quality_trend = 'stable'
                    
                    writer.writerow({
                        'tick': event.tick,
                        'timestamp': event.timestamp,
                        'distance': quality_data.get('distance', 0),
                        'snr_db': quality_data.get('snr_db', 0),
                        'propagation_loss_db': quality_data.get('propagation_loss_db', 0),
                        'packet_loss_probability': current_loss_prob,
                        'signal_strength': 1.0 - current_loss_prob,  # Inverse relationship
                        'sea_state': getattr(controller.game_state, 'sea_state', 2),
                        'water_temperature': getattr(controller.game_state, 'water_temperature', 15),
                        'submarine_depth': controller.game_state.submarine.depth,
                        'quality_trend': quality_trend
                    })
                    
                    quality_history.append(quality_data)
                    if len(quality_history) > 10:
                        quality_history.pop(0)
        
        print(f"Communication quality timeline exported to {filename}")
    
    def export_all_ml_data(self, controller: SimulationController):
        """Export all ML-optimized datasets"""
        print("Exporting ML-optimized datasets...")
        self.export_ml_training_data(controller)
        self.export_packet_sequence_data(controller)
        self.export_communication_quality_timeline(controller)
        print("All ML datasets exported!") 