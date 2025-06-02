import math
import random
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from enum import Enum

from protocol.packet_formatter import CommandCode

@dataclass
class Position:
    x: float
    y: float
    z: float
    
    def distance_to(self, other: 'Position') -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)
    
    def distance_2d_to(self, other: 'Position') -> float:
        """2D distance ignoring Z coordinate"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

@dataclass
class EnvironmentalSensors:
    """Environmental sensor readings from the submarine"""
    water_temperature: float = 15.0  # Celsius
    pressure: float = 1013.25  # mbar
    light_level: float = 0.0  # lux (0-100, decreases with depth)
    turbidity: float = 1.0  # NTU (Nephelometric Turbidity Units)
    current_speed: float = 0.0  # m/s
    current_direction: float = 0.0  # degrees
    salinity: float = 35.0  # ppt
    ph_level: float = 8.1  # pH
    dissolved_oxygen: float = 6.5  # mg/L
    
    def update_from_depth(self, depth: float):
        """Update sensor readings based on depth"""
        # Temperature decreases with depth (thermocline effect)
        if depth < 30:
            self.water_temperature = 15.0 - (depth * 0.1)  # Gradual decrease
        else:
            self.water_temperature = 12.0 - ((depth - 30) * 0.05)  # Slower decrease below thermocline
        
        # Pressure increases with depth (1 atm per 10m)
        self.pressure = 1013.25 + (depth * 101.325)
        
        # Light decreases exponentially with depth
        self.light_level = 100.0 * math.exp(-depth / 20.0)  # Exponential decay
        
        # Turbidity varies randomly but tends to increase with depth
        base_turbidity = 1.0 + (depth / 100.0)
        self.turbidity = base_turbidity + random.uniform(-0.5, 0.5)
        self.turbidity = max(0.1, self.turbidity)
        
        # Current varies with depth and location
        self.current_speed = random.uniform(0.1, 0.8) + (depth / 200.0)
        self.current_direction = random.uniform(0, 360)
        
        # Dissolved oxygen decreases with depth
        self.dissolved_oxygen = 8.0 - (depth / 50.0)
        self.dissolved_oxygen = max(2.0, self.dissolved_oxygen)

@dataclass
class DetectableObject:
    id: int
    position: Position
    object_type: str
    size: float  # radius in meters
    detected: bool = False
    
class VehicleState(Enum):
    IDLE = "idle"
    MOVING = "moving"
    TURNING = "turning"
    ASCENDING = "ascending"
    DESCENDING = "descending"
    STOPPED = "stopped"

@dataclass
class Ship:
    position: Position
    heading: float  # degrees: 0=east, +CCW
    communication_range: float = 1000.0  # meters
    
    def distance_to_submarine(self, submarine: 'Submarine') -> float:
        return self.position.distance_2d_to(submarine.position)

@dataclass
class Submarine:
    position: Position
    heading: float  # degrees: 0=east, +CCW
    depth: float  # meters (positive = deeper)
    pressure: float = 0.0  # simulated pressure based on depth
    state: VehicleState = VehicleState.IDLE
    max_depth: float = 200.0
    min_depth: float = 0.0
    detection_range: float = 50.0  # meters
    speed: float = 5.0  # meters per tick
    turn_rate: float = 10.0  # degrees per tick
    ascent_descent_rate: float = 2.0  # meters per tick
    
    # Environmental sensors
    sensors: EnvironmentalSensors = None
    
    # Navigation and safety
    max_safe_distance_from_ship: float = 2000.0  # meters (increased for realistic testing)
    
    def __post_init__(self):
        if self.sensors is None:
            self.sensors = EnvironmentalSensors()
        self.update_sensors()
    
    def update_sensors(self):
        """Update all environmental sensors based on current position and depth"""
        self.sensors.update_from_depth(self.depth)
        self.update_pressure()
    
    def update_pressure(self):
        """Update pressure based on depth (rough approximation)"""
        # 1 atm at surface + 1 atm per 10m depth
        self.pressure = 1013.25 + (self.depth * 101.325)
    
    def get_surroundings_report(self, objects: List[DetectableObject], ship_distance: float) -> Dict:
        """Generate a comprehensive surroundings report"""
        # Detect nearby objects
        nearby_objects = []
        for obj in objects:
            distance = self.position.distance_to(obj.position)
            if distance <= self.detection_range:
                nearby_objects.append({
                    'id': obj.id,
                    'type': obj.object_type,
                    'distance': distance,
                    'bearing': self._calculate_bearing(obj.position),
                    'depth_diff': obj.position.z - self.position.z
                })
        
        # Calculate terrain/bottom proximity (assuming flat bottom at 100m)
        bottom_depth = 100.0
        bottom_clearance = bottom_depth - self.depth
        
        return {
            'position': {
                'x': self.position.x,
                'y': self.position.y,
                'z': self.position.z,
                'depth': self.depth
            },
            'orientation': {
                'heading': self.heading
            },
            'environmental': {
                'water_temperature': self.sensors.water_temperature,
                'pressure': self.sensors.pressure,
                'light_level': self.sensors.light_level,
                'turbidity': self.sensors.turbidity,
                'current_speed': self.sensors.current_speed,
                'current_direction': self.sensors.current_direction,
                'salinity': self.sensors.salinity,
                'ph_level': self.sensors.ph_level,
                'dissolved_oxygen': self.sensors.dissolved_oxygen
            },
            'navigation': {
                'ship_distance': ship_distance,
                'ship_bearing': self._calculate_ship_bearing(ship_distance),
                'bottom_clearance': bottom_clearance,
                'max_safe_distance': self.max_safe_distance_from_ship
            },
            'detections': {
                'nearby_objects': nearby_objects,
                'total_nearby': len(nearby_objects),
                'detection_range': self.detection_range
            },
            'vehicle_status': {
                'state': self.state.value,
                'speed_capability': self.speed,
                'turn_rate': self.turn_rate,
                'depth_limits': {
                    'min': self.min_depth,
                    'max': self.max_depth,
                    'current': self.depth
                }
            }
        }
    
    def _calculate_bearing(self, target_pos: Position) -> float:
        """Calculate bearing to target position"""
        dx = target_pos.x - self.position.x
        dy = target_pos.y - self.position.y
        bearing = math.degrees(math.atan2(dy, dx))
        return (bearing + 360) % 360
    
    def _calculate_ship_bearing(self, ship_distance: float) -> float:
        """Calculate bearing to ship (assuming ship at origin)"""
        return self._calculate_bearing(Position(0, 0, 0))
    
    def is_safe_to_execute_command(self, cmd: CommandCode, param: int, ship_position: Position) -> Tuple[bool, str]:
        """Check if command execution would keep submarine in safe communication range and world bounds"""
        if cmd == CommandCode.MOVE:
            # Simulate the move
            rad = math.radians(self.heading)
            new_x = self.position.x + param * math.cos(rad)
            new_y = self.position.y + param * math.sin(rad)
            new_distance = math.sqrt(new_x**2 + new_y**2)  # Distance from ship at origin
            
            # Check communication range
            if new_distance > self.max_safe_distance_from_ship:
                return False, f"move_would_exceed_safe_distance_{new_distance:.1f}m"
            
            # Check world bounds (assuming world_size from game state context)
            # Use a conservative estimate of world size
            world_boundary = 400.0  # Conservative boundary
            if abs(new_x) > world_boundary or abs(new_y) > world_boundary:
                return False, f"move_would_exceed_world_bounds_x{new_x:.1f}_y{new_y:.1f}"
        
        elif cmd == CommandCode.DESCEND:
            new_depth = self.depth + param
            if new_depth > self.max_depth:
                return False, f"descend_would_exceed_max_depth_{new_depth:.1f}m"
        
        elif cmd == CommandCode.ASCEND:
            new_depth = self.depth - param
            if new_depth < self.min_depth:
                return False, f"ascend_would_exceed_min_depth_{new_depth:.1f}m"
        
        return True, "safe_to_execute"
    
    def execute_command(self, cmd: CommandCode, param: int, ship_position: Position = None) -> Tuple[bool, str]:
        """Execute a command and return success status with reason"""
        if ship_position is None:
            ship_position = Position(0, 0, 0)  # Default ship at origin
        
        # Safety check
        is_safe, safety_reason = self.is_safe_to_execute_command(cmd, param, ship_position)
        if not is_safe:
            return False, safety_reason
        
        # Execute command
        if cmd == CommandCode.MOVE:
            if self.state in [VehicleState.IDLE, VehicleState.STOPPED]:
                self.state = VehicleState.MOVING
                # Move in current heading direction
                rad = math.radians(self.heading)
                distance = min(param, self.speed)  # Limit movement per tick
                self.position.x += distance * math.cos(rad)
                self.position.y += distance * math.sin(rad)
                self.update_sensors()
                return True, "move_executed"
                
        elif cmd == CommandCode.TURN:
            if self.state in [VehicleState.IDLE, VehicleState.STOPPED]:
                self.state = VehicleState.TURNING
                # Limit turn rate per tick
                turn_amount = max(-self.turn_rate, min(self.turn_rate, param))
                self.heading = (self.heading + turn_amount) % 360
                return True, f"turn_executed_{turn_amount}deg"
                
        elif cmd == CommandCode.STOP:
            self.state = VehicleState.STOPPED
            return True, "stop_executed"
            
        elif cmd == CommandCode.ASCEND:
            if self.depth > self.min_depth:
                self.state = VehicleState.ASCENDING
                ascent = min(param, self.ascent_descent_rate)
                self.depth = max(self.min_depth, self.depth - ascent)
                self.update_sensors()
                return True, f"ascend_executed_{ascent}m"
                
        elif cmd == CommandCode.DESCEND:
            if self.depth < self.max_depth:
                self.state = VehicleState.DESCENDING
                descent = min(param, self.ascent_descent_rate)
                self.depth = min(self.max_depth, self.depth + descent)
                self.update_sensors()
                return True, f"descend_executed_{descent}m"
                
        elif cmd == CommandCode.REPORT_STATUS:
            # This command doesn't change state, just triggers status report
            return True, "status_report_requested"
            
        return False, "command_not_executed"
    
    def detect_objects(self, objects: List[DetectableObject]) -> List[DetectableObject]:
        """Detect objects within detection range"""
        detected = []
        for obj in objects:
            distance = self.position.distance_to(obj.position)
            if distance <= self.detection_range:
                obj.detected = True
                detected.append(obj)
        return detected
    
    def distance_to_ship(self, ship: Ship) -> float:
        return self.position.distance_2d_to(ship.position)

class GameState:
    def __init__(self, world_size: float = 1000.0):
        self.world_size = world_size
        self.tick = 0
        
        # Initialize ship at origin
        self.ship = Ship(
            position=Position(0.0, 0.0, 0.0),
            heading=0.0
        )
        
        # Initialize submarine near ship
        self.submarine = Submarine(
            position=Position(
                random.uniform(-50, 50),
                random.uniform(-50, 50),
                random.uniform(10, 50)
            ),
            heading=random.uniform(0, 360),
            depth=random.uniform(10, 50)
        )
        
        # Generate random detectable objects
        self.objects = self._generate_objects()
        
        # Mission tracking
        self.objects_detected = 0
        self.total_distance_traveled = 0.0
        self.last_position = Position(self.submarine.position.x, 
                                    self.submarine.position.y, 
                                    self.submarine.position.z)
        
        # Environmental conditions
        self.sea_state = random.randint(1, 4)  # 1-4 scale for moderate conditions
        self.water_temperature = 15.0 + random.uniform(-3, 3)  # 12-18°C
    
    def _generate_objects(self) -> List[DetectableObject]:
        """Generate 5-15 random objects near the ship within submarine's operational range"""
        num_objects = random.randint(5, 15)
        objects = []
        
        for i in range(num_objects):
            # Place objects within a reasonable range of the ship
            # but ensure they're within potential submarine detection range
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(20, min(400, self.ship.communication_range * 0.8))
            
            x = self.ship.position.x + distance * math.cos(angle)
            y = self.ship.position.y + distance * math.sin(angle)
            z = random.uniform(5, 100)  # Objects at various depths
            
            obj_types = ["wreck", "rock", "debris", "mine", "artifact"]
            
            objects.append(DetectableObject(
                id=i + 1,
                position=Position(x, y, z),
                object_type=random.choice(obj_types),
                size=random.uniform(1.0, 5.0)
            ))
        
        return objects
    
    def update_tick(self):
        """Update the game state for one tick"""
        # Track distance traveled
        current_pos = Position(self.submarine.position.x, 
                             self.submarine.position.y, 
                             self.submarine.position.z)
        distance_moved = self.last_position.distance_to(current_pos)
        self.total_distance_traveled += distance_moved
        self.last_position = current_pos
        
        # Check for object detection
        detected = self.submarine.detect_objects(self.objects)
        if detected:
            self.objects_detected = len([obj for obj in self.objects if obj.detected])
        
        # Update submarine state (return to idle after actions)
        if self.submarine.state in [VehicleState.MOVING, VehicleState.TURNING, 
                                   VehicleState.ASCENDING, VehicleState.DESCENDING]:
            self.submarine.state = VehicleState.IDLE
        
        # Update environmental conditions occasionally
        if self.tick % 100 == 0:  # Every 100 ticks
            self.sea_state = max(1, min(6, self.sea_state + random.randint(-1, 1)))
            self.water_temperature += random.uniform(-0.1, 0.1)
        
        self.tick += 1
    
    def is_submarine_in_bounds(self) -> bool:
        """Check if submarine is within world bounds with safety margin"""
        pos = self.submarine.position
        # Use a safety margin of 10% of world size
        safety_margin = self.world_size * 0.1
        safe_boundary = (self.world_size / 2) - safety_margin
        
        return (abs(pos.x) <= safe_boundary and 
                abs(pos.y) <= safe_boundary and 
                0 <= pos.z <= self.submarine.max_depth)
    
    def get_communication_distance(self) -> float:
        """Get current communication distance between ship and submarine"""
        return self.ship.distance_to_submarine(self.submarine)
    
    def get_status_summary(self) -> Dict:
        """Get a summary of current game state"""
        ship_distance = self.get_communication_distance()
        surroundings = self.submarine.get_surroundings_report(self.objects, ship_distance)
        
        return {
            'tick': self.tick,
            'submarine_position': (self.submarine.position.x, 
                                 self.submarine.position.y, 
                                 self.submarine.position.z),
            'submarine_heading': self.submarine.heading,
            'submarine_depth': self.submarine.depth,
            'submarine_pressure': self.submarine.pressure,
            'submarine_state': self.submarine.state.value,
            'communication_distance': ship_distance,
            'objects_detected': self.objects_detected,
            'total_objects': len(self.objects),
            'distance_traveled': self.total_distance_traveled,
            'in_bounds': self.is_submarine_in_bounds(),
            'environmental': {
                'sea_state': self.sea_state,
                'water_temperature': self.water_temperature,
                'sensors': surroundings['environmental']
            },
            'surroundings': surroundings
        } 