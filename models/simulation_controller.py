import random
import math
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from protocol.packet_formatter import PacketFormatter, CommandCode
from models.game_state import GameState, VehicleState, DetectableObject, Position
from models.communication_model import UnderwaterCommunicationModel, PacketTransmission

@dataclass
class SimulationEvent:
    tick: int
    event_type: str  # "command", "status", "detection", "mission_update", "communication"
    data: Dict
    success: bool = True
    timestamp: float = 0.0  # Simulation timestamp

class MissionPlanner:
    """Generates realistic mission commands for the submarine with safety constraints"""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.current_objective = None
        self.search_pattern = "spiral"  # "spiral", "grid", "random"
        self.search_radius = 0
        self.search_angle = 0
        self.commands_in_sequence = []
        self.sequence_index = 0
        self.last_ship_distance = 0.0
        
    def get_next_command(self) -> Tuple[CommandCode, int]:
        """Generate the next logical command based on mission state"""
        submarine = self.game_state.submarine
        ship_distance = self.game_state.get_communication_distance()
        self.last_ship_distance = ship_distance
        
        # Emergency check: if submarine is out of bounds, force immediate return
        if not self.game_state.is_submarine_in_bounds():
            return self._plan_emergency_return()
        
        # Safety check: if too far from ship, prioritize return
        # Use the effective max distance considering movement aggressiveness
        effective_max_distance = submarine.max_safe_distance_from_ship * submarine.movement_aggressiveness
        if ship_distance > effective_max_distance * 0.8:  # 80% of effective max distance
            return self._plan_return_to_ship()
        
        # If we have a command sequence, continue it
        if self.commands_in_sequence and self.sequence_index < len(self.commands_in_sequence):
            cmd, param = self.commands_in_sequence[self.sequence_index]
            self.sequence_index += 1
            
            # Safety check for the planned command
            is_safe, _ = submarine.is_safe_to_execute_command(cmd, param, Position(0, 0, 0))
            if is_safe:
                return cmd, param
            else:
                # Skip unsafe command and plan new sequence
                self.commands_in_sequence = []
                self.sequence_index = 0
        
        # Generate new command sequence based on current situation
        self._plan_next_sequence()
        
        if self.commands_in_sequence:
            cmd, param = self.commands_in_sequence[0]
            self.sequence_index = 1
            return cmd, param
        
        # Fallback to status report
        return CommandCode.REPORT_STATUS, 0
    
    def _plan_return_to_ship(self) -> Tuple[CommandCode, int]:
        """Plan commands to return submarine closer to ship"""
        submarine = self.game_state.submarine
        
        # Calculate bearing to ship (at origin)
        ship_bearing = submarine._calculate_ship_bearing(self.last_ship_distance)
        
        # Calculate turn needed to face ship
        heading_diff = (ship_bearing - submarine.heading + 360) % 360
        if heading_diff > 180:
            heading_diff -= 360
        
        # If not facing ship, turn towards it
        if abs(heading_diff) > 10:
            turn_amount = max(-submarine.turn_rate, min(submarine.turn_rate, heading_diff))
            return CommandCode.TURN, int(turn_amount)
        
        # If facing ship, move towards it
        move_distance = min(30, int(submarine.speed))
        return CommandCode.MOVE, int(move_distance)
    
    def _plan_emergency_return(self) -> Tuple[CommandCode, int]:
        """Emergency return when submarine is out of bounds"""
        submarine = self.game_state.submarine
        
        # Calculate direct bearing to ship (origin)
        dx = 0 - submarine.position.x
        dy = 0 - submarine.position.y
        ship_bearing = math.degrees(math.atan2(dy, dx))
        ship_bearing = (ship_bearing + 360) % 360
        
        # Calculate turn needed to face ship
        heading_diff = (ship_bearing - submarine.heading + 360) % 360
        if heading_diff > 180:
            heading_diff -= 360
        
        # If not facing ship, turn towards it
        if abs(heading_diff) > 5:  # Smaller tolerance for emergency
            turn_amount = max(-submarine.turn_rate, min(submarine.turn_rate, heading_diff))
            return CommandCode.TURN, int(turn_amount)
        
        # If facing ship, move towards it with maximum safe speed
        move_distance = min(submarine.speed, 10)  # Conservative movement
        return CommandCode.MOVE, int(move_distance)
    
    def _plan_next_sequence(self):
        """Plan the next sequence of commands with safety considerations"""
        submarine = self.game_state.submarine
        self.commands_in_sequence = []
        self.sequence_index = 0
        
        # Check if we need to adjust depth for better detection
        if submarine.depth < 10:
            self.commands_in_sequence.append((CommandCode.DESCEND, 10))
        elif submarine.depth > 80:
            self.commands_in_sequence.append((CommandCode.ASCEND, 20))
        
        # Implement search pattern with safety constraints
        if self.search_pattern == "spiral":
            self._plan_spiral_search()
        elif self.search_pattern == "grid":
            self._plan_grid_search()
        else:
            self._plan_random_search()
    
    def _plan_spiral_search(self):
        """Plan a spiral search pattern with distance constraints"""
        submarine = self.game_state.submarine
        
        # Calculate distance factor based on movement aggressiveness and max range
        effective_max_distance = submarine.max_safe_distance_from_ship * submarine.movement_aggressiveness
        distance_factor = max(0.2, 1.0 - (self.last_ship_distance / effective_max_distance))
        
        # Base movement distance scaled by submarine speed and aggressiveness
        base_move = submarine.speed * submarine.movement_aggressiveness
        move_distance = min(int(base_move * 2), int((10 + self.search_radius * 3) * distance_factor))
        
        self.commands_in_sequence.append((CommandCode.MOVE, move_distance))
        
        # Turn for spiral - larger angles for more aggressive exploration
        turn_angle = int(30 + (self.search_radius * 3 * submarine.movement_aggressiveness))
        self.commands_in_sequence.append((CommandCode.TURN, turn_angle))
        
        # Occasionally change depth
        if random.random() < 0.3:
            if random.random() < 0.5:
                self.commands_in_sequence.append((CommandCode.ASCEND, random.randint(5, 15)))
            else:
                self.commands_in_sequence.append((CommandCode.DESCEND, random.randint(5, 15)))
        
        self.search_radius += 1
        # Scale max search radius based on aggressiveness
        max_search_radius = int(15 + (submarine.movement_aggressiveness * 20))
        if self.search_radius > max_search_radius:
            self.search_radius = 0
    
    def _plan_grid_search(self):
        """Plan a grid search pattern with distance constraints"""
        submarine = self.game_state.submarine
        
        # Calculate distance factor based on movement aggressiveness and max range
        effective_max_distance = submarine.max_safe_distance_from_ship * submarine.movement_aggressiveness
        distance_factor = max(0.2, 1.0 - (self.last_ship_distance / effective_max_distance))
        
        # Base movement distance scaled by submarine speed and aggressiveness
        base_move = submarine.speed * submarine.movement_aggressiveness * 3
        move_distance = min(int(base_move * 2), int(80 * distance_factor))
        
        # Simple back-and-forth pattern
        if self.search_angle % 180 == 0:
            self.commands_in_sequence.append((CommandCode.MOVE, move_distance))
            self.commands_in_sequence.append((CommandCode.TURN, 90))
            self.commands_in_sequence.append((CommandCode.MOVE, int(submarine.speed * 2)))
            self.commands_in_sequence.append((CommandCode.TURN, 90))
        else:
            self.commands_in_sequence.append((CommandCode.MOVE, move_distance))
            self.commands_in_sequence.append((CommandCode.TURN, -90))
            self.commands_in_sequence.append((CommandCode.MOVE, int(submarine.speed * 2)))
            self.commands_in_sequence.append((CommandCode.TURN, -90))
        
        self.search_angle += 180
    
    def _plan_random_search(self):
        """Plan random exploration with distance constraints"""
        submarine = self.game_state.submarine
        
        # Calculate distance factor based on movement aggressiveness and max range
        effective_max_distance = submarine.max_safe_distance_from_ship * submarine.movement_aggressiveness
        distance_factor = max(0.2, 1.0 - (self.last_ship_distance / effective_max_distance))
        
        # Base movement distance scaled by submarine speed and aggressiveness
        base_move = submarine.speed * submarine.movement_aggressiveness * 4
        move_distance = min(int(base_move * 3), int(random.randint(30, 100) * distance_factor))
        
        # Random movement with some logic
        turn_range = int(90 * submarine.movement_aggressiveness)
        self.commands_in_sequence.append((CommandCode.TURN, random.randint(-turn_range, turn_range)))
        self.commands_in_sequence.append((CommandCode.MOVE, move_distance))
        
        # Random depth changes
        if random.random() < 0.4:
            if random.random() < 0.5:
                self.commands_in_sequence.append((CommandCode.ASCEND, random.randint(5, 20)))
            else:
                self.commands_in_sequence.append((CommandCode.DESCEND, random.randint(5, 20)))

class SimulationController:
    """Controls the complex simulation with realistic communication and timing"""
    
    def __init__(self, world_size: float = 1000.0):
        self.game_state = GameState(world_size)
        self.mission_planner = MissionPlanner(self.game_state)
        self.communication_model = UnderwaterCommunicationModel()
        self.events: List[SimulationEvent] = []
        
        # Statistics
        self.total_commands_sent = 0
        self.total_commands_received = 0
        self.total_status_sent = 0
        self.total_status_received = 0
        self.detection_events = []
        self.communication_events = []
        
        # Timing
        self.simulation_start_time = time.time()
        self.current_simulation_time = 0.0  # Simulation time in seconds
        
    def get_simulation_timestamp(self) -> float:
        """Get current simulation timestamp"""
        return self.simulation_start_time + self.current_simulation_time
    
    def simulate_tick(self) -> List[SimulationEvent]:
        """Simulate one tick of the game with realistic communication"""
        tick_events = []
        current_tick = self.game_state.tick
        self.current_simulation_time = current_tick * 1.0  # 1 second per tick
        
        # Update communication environment
        self.communication_model.update_environment(
            sea_state=self.game_state.sea_state,
            temperature=self.game_state.water_temperature
        )
        
        # Get next command from mission planner
        cmd, param = self.mission_planner.get_next_command()
        
        # Get positions for communication simulation
        ship_pos = (self.game_state.ship.position.x, 
                   self.game_state.ship.position.y, 
                   self.game_state.ship.position.z)
        sub_pos = (self.game_state.submarine.position.x,
                  self.game_state.submarine.position.y,
                  self.game_state.submarine.position.z)
        
        # Build command packet
        raw_cmd = PacketFormatter.build_cmd_packet(cmd, param)
        
        # Simulate command transmission using realistic model
        cmd_transmission = self.communication_model.simulate_transmission(
            sender="ship",
            receiver="submarine", 
            packet_type="command",
            data_size=len(raw_cmd),
            ship_pos=ship_pos,
            sub_pos=sub_pos
        )
        
        self.total_commands_sent += 1
        
        # Create command event with timing information
        command_event = SimulationEvent(
            tick=current_tick,
            event_type="command",
            data={
                "packet_id": cmd_transmission.packet_id,
                "command": cmd.name,
                "param": param,
                "distance": self.game_state.get_communication_distance(),
                "lost": cmd_transmission.is_lost,
                "loss_reason": cmd_transmission.loss_reason,
                "raw_packet_size": len(raw_cmd),
                "transmission_time": cmd_transmission.transmission_time,
                "arrival_time": cmd_transmission.arrival_time,
                "propagation_delay": cmd_transmission.propagation_delay,
                "multipath_delay": cmd_transmission.multipath_delay,
                "total_delay": cmd_transmission.total_delay,
                "signal_strength": cmd_transmission.signal_strength
            },
            success=not cmd_transmission.is_lost,
            timestamp=self.get_simulation_timestamp()
        )
        tick_events.append(command_event)
        self.communication_events.append(command_event)
        
        # Execute command if not lost
        command_executed = False
        execution_reason = "packet_lost"
        if not cmd_transmission.is_lost:
            self.total_commands_received += 1
            command_executed, execution_reason = self.game_state.submarine.execute_command(
                cmd, param, self.game_state.ship.position)
        
        # Check for object detections
        detected_objects = self.game_state.submarine.detect_objects(self.game_state.objects)
        if detected_objects:
            for obj in detected_objects:
                detection_event = SimulationEvent(
                    tick=current_tick,
                    event_type="detection",
                    data={
                        "object_id": obj.id,
                        "object_type": obj.object_type,
                        "position": (obj.position.x, obj.position.y, obj.position.z),
                        "size": obj.size,
                        "distance": self.game_state.submarine.position.distance_to(obj.position),
                        "bearing": self.game_state.submarine._calculate_bearing(obj.position)
                    },
                    timestamp=self.get_simulation_timestamp()
                )
                tick_events.append(detection_event)
                self.detection_events.append(detection_event)
        
        # Update game state
        self.game_state.update_tick()
        
        # Generate comprehensive status response
        submarine = self.game_state.submarine
        surroundings = submarine.get_surroundings_report(
            self.game_state.objects, 
            self.game_state.get_communication_distance()
        )
        
        # Build status packet with comprehensive data
        raw_status = PacketFormatter.build_status_packet(
            status=0x01 if command_executed else 0x00,
            depth=int(submarine.depth),
            pressure=int(submarine.pressure),
            missing_cmd_seqs=[],  # Simplified for now
            x=int(submarine.position.x),
            y=int(submarine.position.y),
            z=int(submarine.position.z),
            heading=int(submarine.heading)
        )
        
        # Simulate status transmission
        status_transmission = self.communication_model.simulate_transmission(
            sender="submarine",
            receiver="ship",
            packet_type="status", 
            data_size=len(raw_status),
            ship_pos=ship_pos,
            sub_pos=sub_pos
        )
        
        self.total_status_sent += 1
        if not status_transmission.is_lost:
            self.total_status_received += 1
        
        # Create status event with comprehensive data
        status_event = SimulationEvent(
            tick=current_tick,
            event_type="status",
            data={
                "packet_id": status_transmission.packet_id,
                "status_code": 0x01 if command_executed else 0x00,
                "execution_reason": execution_reason,
                "position": (submarine.position.x, submarine.position.y, submarine.position.z),
                "heading": submarine.heading,
                "depth": submarine.depth,
                "pressure": submarine.pressure,
                "state": submarine.state.value,
                "distance": self.game_state.get_communication_distance(),
                "lost": status_transmission.is_lost,
                "loss_reason": status_transmission.loss_reason,
                "raw_packet_size": len(raw_status),
                "transmission_time": status_transmission.transmission_time,
                "arrival_time": status_transmission.arrival_time,
                "propagation_delay": status_transmission.propagation_delay,
                "multipath_delay": status_transmission.multipath_delay,
                "total_delay": status_transmission.total_delay,
                "signal_strength": status_transmission.signal_strength,
                "environmental_sensors": surroundings['environmental'],
                "navigation_data": surroundings['navigation'],
                "detections": surroundings['detections'],
                "vehicle_status": surroundings['vehicle_status']
            },
            success=not status_transmission.is_lost,
            timestamp=self.get_simulation_timestamp()
        )
        tick_events.append(status_event)
        self.communication_events.append(status_event)
        
        # Add mission update event every 10 ticks
        if current_tick % 10 == 0:
            mission_event = SimulationEvent(
                tick=current_tick,
                event_type="mission_update",
                data=self.game_state.get_status_summary(),
                timestamp=self.get_simulation_timestamp()
            )
            tick_events.append(mission_event)
        
        # Add communication quality event every 5 ticks
        if current_tick % 5 == 0:
            comm_quality = self.communication_model.get_communication_quality(
                self.game_state.get_communication_distance(),
                ship_pos[2], sub_pos[2]
            )
            
            comm_event = SimulationEvent(
                tick=current_tick,
                event_type="communication",
                data=comm_quality,
                timestamp=self.get_simulation_timestamp()
            )
            tick_events.append(comm_event)
        
        # Store events
        self.events.extend(tick_events)
        
        return tick_events
    
    def run_simulation(self, num_ticks: int) -> Dict:
        """Run the simulation for a specified number of ticks"""
        print(f"Starting complex simulation for {num_ticks} ticks...")
        print(f"Initial objects to detect: {len(self.game_state.objects)}")
        print(f"Max safe distance from ship: {self.game_state.submarine.max_safe_distance_from_ship}m")
        
        out_of_bounds_warning_count = 0
        last_bounds_warning_tick = -100
        
        for tick in range(num_ticks):
            if tick % 1000 == 0 and tick > 0:
                distance = self.game_state.get_communication_distance()
                print(f"Tick {tick}: Objects detected: {self.game_state.objects_detected}/{len(self.game_state.objects)}, Distance: {distance:.1f}m")
            
            self.simulate_tick()
            
            # Check if submarine is out of bounds (limit warnings)
            if not self.game_state.is_submarine_in_bounds():
                if tick - last_bounds_warning_tick >= 100:  # Only warn every 100 ticks
                    print(f"Warning: Submarine out of bounds at tick {tick} (position: {self.game_state.submarine.position.x:.1f}, {self.game_state.submarine.position.y:.1f})")
                    last_bounds_warning_tick = tick
                    out_of_bounds_warning_count += 1
                    
                    # If out of bounds for too long, abort simulation
                    if out_of_bounds_warning_count > 10:
                        print(f"Error: Submarine stuck out of bounds for too long. Aborting simulation at tick {tick}")
                        break
            else:
                # Reset warning count if back in bounds
                out_of_bounds_warning_count = 0
            
            # Check if submarine is too far from ship
            distance = self.game_state.get_communication_distance()
            if distance > self.game_state.submarine.max_safe_distance_from_ship:
                if tick - last_bounds_warning_tick >= 100:  # Only warn every 100 ticks
                    print(f"Warning: Submarine beyond safe distance ({distance:.1f}m) at tick {tick}")
        
        # Generate final report
        return self._generate_final_report()
    
    def _generate_final_report(self) -> Dict:
        """Generate a comprehensive simulation report"""
        total_objects = len(self.game_state.objects)
        detected_objects = self.game_state.objects_detected
        
        command_success_rate = (self.total_commands_received / self.total_commands_sent) if self.total_commands_sent > 0 else 0
        status_success_rate = (self.total_status_received / self.total_status_sent) if self.total_status_sent > 0 else 0
        
        # Calculate communication statistics
        total_comm_events = len(self.communication_events)
        successful_comm = len([e for e in self.communication_events if e.success])
        overall_comm_success = successful_comm / total_comm_events if total_comm_events > 0 else 0
        
        # Calculate average delays
        successful_transmissions = [e for e in self.communication_events if e.success]
        avg_propagation_delay = sum(e.data.get('propagation_delay', 0) for e in successful_transmissions) / len(successful_transmissions) if successful_transmissions else 0
        avg_total_delay = sum(e.data.get('total_delay', 0) for e in successful_transmissions) / len(successful_transmissions) if successful_transmissions else 0
        
        return {
            "simulation_summary": {
                "total_ticks": self.game_state.tick,
                "total_distance_traveled": self.game_state.total_distance_traveled,
                "objects_detected": detected_objects,
                "total_objects": total_objects,
                "detection_rate": detected_objects / total_objects if total_objects > 0 else 0,
                "final_position": (
                    self.game_state.submarine.position.x,
                    self.game_state.submarine.position.y,
                    self.game_state.submarine.position.z
                ),
                "final_depth": self.game_state.submarine.depth,
                "final_heading": self.game_state.submarine.heading,
                "max_distance_from_ship": max([e.data.get('distance', 0) for e in self.events if 'distance' in e.data], default=0)
            },
            "communication_stats": {
                "commands_sent": self.total_commands_sent,
                "commands_received": self.total_commands_received,
                "command_success_rate": command_success_rate,
                "status_sent": self.total_status_sent,
                "status_received": self.total_status_received,
                "status_success_rate": status_success_rate,
                "overall_communication_success": overall_comm_success,
                "average_propagation_delay_ms": avg_propagation_delay * 1000,
                "average_total_delay_ms": avg_total_delay * 1000,
                "total_communication_events": total_comm_events
            },
            "objects": [
                {
                    "id": obj.id,
                    "type": obj.object_type,
                    "position": (obj.position.x, obj.position.y, obj.position.z),
                    "detected": obj.detected
                }
                for obj in self.game_state.objects
            ],
            "detection_events": len(self.detection_events),
            "total_events": len(self.events)
        } 