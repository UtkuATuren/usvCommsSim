import csv
import os
from typing import List, Dict
from models.simulation_controller import SimulationEvent, SimulationController

class CSVLogger:
    """Logs simulation events to CSV files for analysis"""
    
    def __init__(self, base_filename: str = "simulation"):
        self.base_filename = base_filename
        # Ensure output directory exists
        os.makedirs("outputs/standard_simulation", exist_ok=True)
        
    def export_simulation_log(self, controller: SimulationController, filename: str = None):
        """Export all simulation events to a comprehensive CSV"""
        if filename is None:
            filename = f"outputs/standard_simulation/{self.base_filename}_log.csv"
            
        fieldnames = [
            'tick', 'event_type', 'success',
            # Command fields
            'command', 'command_param', 'command_lost',
            # Status fields  
            'status_code', 'depth', 'pressure', 'pos_x', 'pos_y', 'pos_z', 
            'heading', 'submarine_state', 'status_lost',
            # Detection fields
            'detected_object_id', 'detected_object_type', 'detected_object_distance',
            # Communication fields
            'communication_distance', 'packet_size',
            # Mission fields
            'objects_detected_total', 'distance_traveled', 'in_bounds'
        ]
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for event in controller.events:
                row = {
                    'tick': event.tick,
                    'event_type': event.event_type,
                    'success': event.success
                }
                
                # Add event-specific data
                if event.event_type == "command":
                    row.update({
                        'command': event.data.get('command'),
                        'command_param': event.data.get('param'),
                        'command_lost': event.data.get('lost'),
                        'communication_distance': event.data.get('distance'),
                        'packet_size': event.data.get('raw_packet_size')
                    })
                    
                elif event.event_type == "status":
                    row.update({
                        'status_code': f"0x{event.data.get('status_code', 0):02X}",
                        'depth': event.data.get('depth'),
                        'pressure': event.data.get('pressure'),
                        'pos_x': event.data.get('position', [0, 0, 0])[0],
                        'pos_y': event.data.get('position', [0, 0, 0])[1],
                        'pos_z': event.data.get('position', [0, 0, 0])[2],
                        'heading': event.data.get('heading'),
                        'submarine_state': event.data.get('state'),
                        'status_lost': event.data.get('lost'),
                        'communication_distance': event.data.get('distance'),
                        'packet_size': event.data.get('raw_packet_size')
                    })
                    
                elif event.event_type == "detection":
                    row.update({
                        'detected_object_id': event.data.get('object_id'),
                        'detected_object_type': event.data.get('object_type'),
                        'detected_object_distance': event.data.get('distance')
                    })
                    
                elif event.event_type == "mission_update":
                    row.update({
                        'objects_detected_total': event.data.get('objects_detected'),
                        'distance_traveled': event.data.get('distance_traveled'),
                        'in_bounds': event.data.get('in_bounds')
                    })
                
                writer.writerow(row)
                
        print(f"Simulation log exported to {filename}")
    
    def export_objects_summary(self, controller: SimulationController, filename: str = None):
        """Export a summary of all objects and their detection status"""
        if filename is None:
            filename = f"outputs/standard_simulation/{self.base_filename}_objects.csv"
            
        fieldnames = [
            'object_id', 'object_type', 'pos_x', 'pos_y', 'pos_z', 
            'size', 'detected', 'distance_from_ship'
        ]
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            ship_pos = controller.game_state.ship.position
            
            for obj in controller.game_state.objects:
                distance_from_ship = ship_pos.distance_to(obj.position)
                
                writer.writerow({
                    'object_id': obj.id,
                    'object_type': obj.object_type,
                    'pos_x': obj.position.x,
                    'pos_y': obj.position.y,
                    'pos_z': obj.position.z,
                    'size': obj.size,
                    'detected': obj.detected,
                    'distance_from_ship': distance_from_ship
                })
                
        print(f"Objects summary exported to {filename}")
    
    def export_detection_timeline(self, controller: SimulationController, filename: str = None):
        """Export a timeline of object detections"""
        if filename is None:
            filename = f"outputs/standard_simulation/{self.base_filename}_detections.csv"
            
        fieldnames = [
            'tick', 'object_id', 'object_type', 'submarine_pos_x', 
            'submarine_pos_y', 'submarine_pos_z', 'detection_distance',
            'object_pos_x', 'object_pos_y', 'object_pos_z'
        ]
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for event in controller.detection_events:
                if event.event_type == "detection":
                    # Find corresponding submarine position at that tick
                    submarine_events = [e for e in controller.events 
                                      if e.tick == event.tick and e.event_type == "status"]
                    
                    if submarine_events:
                        sub_pos = submarine_events[0].data.get('position', [0, 0, 0])
                    else:
                        sub_pos = [0, 0, 0]
                    
                    obj_pos = event.data.get('position', [0, 0, 0])
                    
                    writer.writerow({
                        'tick': event.tick,
                        'object_id': event.data.get('object_id'),
                        'object_type': event.data.get('object_type'),
                        'submarine_pos_x': sub_pos[0],
                        'submarine_pos_y': sub_pos[1],
                        'submarine_pos_z': sub_pos[2],
                        'detection_distance': event.data.get('distance'),
                        'object_pos_x': obj_pos[0],
                        'object_pos_y': obj_pos[1],
                        'object_pos_z': obj_pos[2]
                    })
                    
        print(f"Detection timeline exported to {filename}")
    
    def export_communication_stats(self, controller: SimulationController, filename: str = None):
        """Export communication statistics over time"""
        if filename is None:
            filename = f"outputs/standard_simulation/{self.base_filename}_communication.csv"
            
        fieldnames = [
            'tick', 'event_type', 'distance', 'packet_lost', 'packet_size',
            'cumulative_commands_sent', 'cumulative_commands_received',
            'cumulative_status_sent', 'cumulative_status_received'
        ]
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            commands_sent = 0
            commands_received = 0
            status_sent = 0
            status_received = 0
            
            for event in controller.events:
                if event.event_type in ["command", "status"]:
                    if event.event_type == "command":
                        commands_sent += 1
                        if event.success:
                            commands_received += 1
                    elif event.event_type == "status":
                        status_sent += 1
                        if event.success:
                            status_received += 1
                    
                    writer.writerow({
                        'tick': event.tick,
                        'event_type': event.event_type,
                        'distance': event.data.get('distance', 0),
                        'packet_lost': event.data.get('lost', False),
                        'packet_size': event.data.get('raw_packet_size', 0),
                        'cumulative_commands_sent': commands_sent,
                        'cumulative_commands_received': commands_received,
                        'cumulative_status_sent': status_sent,
                        'cumulative_status_received': status_received
                    })
                    
        print(f"Communication stats exported to {filename}")
    
    def export_all(self, controller: SimulationController):
        """Export all available logs"""
        print("Exporting all simulation data...")
        self.export_simulation_log(controller)
        self.export_objects_summary(controller)
        self.export_detection_timeline(controller)
        self.export_communication_stats(controller)
        print("All exports completed!") 