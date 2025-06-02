import math
import random
import time
from typing import Tuple, Dict, Optional
from dataclasses import dataclass
from enum import Enum

# Import physics-based acoustic functions
from .acoustic_physics import (
    alpha_thorp, transmission_loss, linear_attenuation, 
    compute_gamma_mean, packet_loss_probability as physics_packet_loss_probability
)
from .acoustic_config import AcousticPhysicsConfig, DEFAULT_CONFIG

@dataclass
class CommunicationEnvironment:
    """Environmental factors affecting underwater communication"""
    water_temperature: float = 15.0  # Celsius
    salinity: float = 35.0  # ppt (parts per thousand)
    depth: float = 50.0  # meters
    sea_state: int = 2  # 0-6 scale (0=calm, 6=very rough)
    thermocline_depth: float = 30.0  # meters
    sound_velocity: float = 1500.0  # m/s base
    
    def calculate_sound_velocity(self, depth: float, temp: float) -> float:
        """Calculate sound velocity based on depth and temperature"""
        # Simplified Mackenzie equation for sound velocity
        # V = 1448.96 + 4.591*T - 5.304e-2*T^2 + 2.374e-4*T^3 + 1.340*(S-35) + 1.630e-2*D + 1.675e-7*D^2
        T = temp
        S = self.salinity
        D = depth
        
        velocity = (1448.96 + 4.591*T - 5.304e-2*T**2 + 2.374e-4*T**3 + 
                   1.340*(S-35) + 1.630e-2*D + 1.675e-7*D**2)
        return velocity

@dataclass
class PacketTransmission:
    """Represents a packet transmission with timing and path information"""
    packet_id: str
    sender: str  # "ship" or "submarine"
    receiver: str  # "ship" or "submarine"
    packet_type: str  # "command" or "status"
    data_size: int  # bytes
    transmission_time: float  # timestamp when sent
    arrival_time: Optional[float] = None  # timestamp when received
    propagation_delay: float = 0.0  # seconds
    is_lost: bool = False
    loss_reason: str = ""
    signal_strength: float = 1.0  # 0-1 scale
    multipath_delay: float = 0.0  # additional delay from multipath
    
    @property
    def total_delay(self) -> float:
        """Total delay including propagation and multipath"""
        return self.propagation_delay + self.multipath_delay
    
    @property
    def is_received(self) -> bool:
        """Check if packet was successfully received"""
        return self.arrival_time is not None and not self.is_lost

class UnderwaterCommunicationModel:
    """Realistic underwater acoustic communication model"""
    
    def __init__(self, config: AcousticPhysicsConfig = None):
        self.environment = CommunicationEnvironment()
        
        # Use provided config or default
        self.physics_config = config if config is not None else DEFAULT_CONFIG
        
        # Set communication parameters from config
        self.frequency = self.physics_config.frequency_hz
        self.transmission_power = self.physics_config.transmission_power_db
        self.noise_level = self.physics_config.noise_level_db
        self.packet_counter = 0
        
        # Communication parameters
        self.max_reliable_range = 1000.0  # meters
        self.data_rate = 1200.0  # bits per second
        
        # Physics-based communication parameters from config (CORRECTED)
        # Use the corrected power (intensity) values for SNR calculations
        self.P0 = self.physics_config.transmission_power_linear
        self.noise_psd = self.physics_config.noise_power_linear
        self.gamma_req = self.physics_config.required_snr_linear
        self.spreading_exp = self.physics_config.spreading_exponent
        self.anomaly_db = self.physics_config.site_anomaly_db
        
        # Cache for repeated calculations (optimization)
        self._f_khz = self.physics_config.frequency_khz
        self._alpha_cached = alpha_thorp(self._f_khz)  # Cache absorption coefficient
        self._anomaly_linear_cached = 10.0 ** (self.anomaly_db / 10.0)  # Cache anomaly factor

    def calculate_propagation_loss(self, distance: float, frequency: float, depth: float) -> float:
        """Calculate acoustic propagation loss in underwater environment"""
        if distance <= 0:
            return 0.0
            
        # Thorp's formula for absorption coefficient (dB/km)
        f_khz = frequency / 1000.0
        if f_khz < 0.4:
            alpha = 0.002 + 0.11 * (f_khz**2) / (1 + f_khz**2) + 0.011 * f_khz**2
        else:
            alpha = 0.002 + 0.11 * (f_khz**2) / (1 + f_khz**2) + 0.011 * f_khz**2
        
        # Geometric spreading loss (cylindrical + spherical)
        geometric_loss = 20 * math.log10(distance) if distance > 1 else 0
        
        # Absorption loss
        absorption_loss = alpha * (distance / 1000.0)
        
        # Additional losses due to depth and environment
        depth_factor = 1 + (depth / 1000.0) * 0.1  # Slight increase with depth
        sea_state_factor = 1 + (self.environment.sea_state / 6.0) * 0.2
        
        total_loss = geometric_loss + absorption_loss
        total_loss *= depth_factor * sea_state_factor
        
        return total_loss
    
    def calculate_multipath_effects(self, distance: float, depth_diff: float) -> Tuple[float, float]:
        """Calculate multipath propagation effects"""
        # Surface reflection path
        surface_path = math.sqrt(distance**2 + (2 * depth_diff)**2)
        surface_delay = (surface_path - distance) / self.environment.sound_velocity
        
        # Bottom reflection (assuming 100m bottom depth)
        bottom_depth = 100.0
        bottom_path = math.sqrt(distance**2 + (2 * (bottom_depth - depth_diff))**2)
        bottom_delay = (bottom_path - distance) / self.environment.sound_velocity
        
        # Take the shorter additional delay
        multipath_delay = min(surface_delay, bottom_delay)
        
        # Signal strength reduction due to multipath interference
        interference_factor = 0.8 + 0.2 * random.random()  # 80-100% of original strength
        
        return multipath_delay, interference_factor
    
    def calculate_propagation_delay(self, distance: float, ship_depth: float, sub_depth: float) -> float:
        """Calculate acoustic propagation delay"""
        # Update sound velocity based on average depth and temperature
        avg_depth = (ship_depth + sub_depth) / 2
        temp_at_depth = self.environment.water_temperature - (avg_depth / 100.0) * 2.0  # 2°C per 100m
        sound_velocity = self.environment.calculate_sound_velocity(avg_depth, temp_at_depth)
        
        # Direct path delay
        direct_delay = distance / sound_velocity
        
        return direct_delay
    
    def calculate_packet_loss_probability(self, distance: float, ship_depth: float, 
                                        sub_depth: float, packet_size: int) -> Tuple[float, str]:
        """Calculate physics-based packet loss probability using underwater acoustic propagation model"""
        
        # Use physics-based model with cached parameters for efficiency
        # d: distance in meters
        d = distance
        # f_khz: frequency in kHz (required by alpha_thorp function)
        f_khz = self._f_khz
        # P0: source PSD at 1m in linear scale 
        P0 = self.P0
        # noise_psd: noise power spectral density in linear scale (same units as P0)
        noise_psd = self.noise_psd
        # gamma_req: required SNR threshold in linear scale
        gamma_req = self.gamma_req
        # spreading_exp: geometric spreading exponent
        spreading_exp = self.spreading_exp
        # anomaly_db: site-specific anomaly in dB
        anomaly_db = self.anomaly_db
        
        # Handle edge cases
        if distance <= 0:
            return 0.0, "zero_distance"
        if distance < 1.0:
            # Very close range - assume perfect communication
            return 0.01, "close_range"
        
        # Calculate physics-based packet loss probability
        try:
            # Compute transmission loss
            TL_db = transmission_loss(d, f_khz, spreading_exp, anomaly_db)
            
            # Compute mean SNR (for diagnostic purposes)
            gamma_mean = compute_gamma_mean(d, P0, noise_psd, f_khz, spreading_exp, anomaly_db)
            
            # Compute packet loss probability under Rayleigh fading
            P_loss = physics_packet_loss_probability(d, P0, noise_psd, f_khz, gamma_req, spreading_exp, anomaly_db)
            
            # Determine loss reason based on conditions
            if gamma_mean < 1.0:  # Mean SNR < 0 dB
                reason = "very_low_snr"
            elif gamma_mean < 3.16:  # Mean SNR < 5 dB  
                reason = "low_snr"
            elif gamma_mean < 10.0:  # Mean SNR < 10 dB
                reason = "moderate_snr"
            elif gamma_mean < 31.6:  # Mean SNR < 15 dB
                reason = "acceptable_snr"
            else:
                reason = "good_snr"
            
            # Apply packet size adjustment using config parameters
            size_factor = 1.0 + (packet_size - self.physics_config.baseline_packet_size) / self.physics_config.size_adjustment_factor
            size_factor = max(1.0, min(self.physics_config.max_size_penalty, size_factor))
            
            # Adjust loss probability by size factor
            P_loss_adjusted = min(0.99, P_loss * size_factor)
            
            return P_loss_adjusted, reason
            
        except (ValueError, ZeroDivisionError, OverflowError) as e:
            # Handle numerical errors gracefully
            return 0.95, f"calculation_error_{type(e).__name__}"
    
    def simulate_transmission(self, sender: str, receiver: str, packet_type: str, 
                            data_size: int, ship_pos: Tuple[float, float, float],
                            sub_pos: Tuple[float, float, float]) -> PacketTransmission:
        """Simulate a complete packet transmission"""
        
        self.packet_counter += 1
        packet_id = f"{sender}_{packet_type}_{self.packet_counter}"
        
        # Calculate distance and positions
        distance = math.sqrt((ship_pos[0] - sub_pos[0])**2 + 
                           (ship_pos[1] - sub_pos[1])**2 + 
                           (ship_pos[2] - sub_pos[2])**2)
        
        ship_depth = ship_pos[2]
        sub_depth = sub_pos[2]
        
        # Create transmission record
        transmission = PacketTransmission(
            packet_id=packet_id,
            sender=sender,
            receiver=receiver,
            packet_type=packet_type,
            data_size=data_size,
            transmission_time=time.time()
        )
        
        # Calculate propagation delay
        transmission.propagation_delay = self.calculate_propagation_delay(distance, ship_depth, sub_depth)
        
        # Calculate multipath effects
        multipath_delay, interference_factor = self.calculate_multipath_effects(
            distance, abs(ship_depth - sub_depth))
        transmission.multipath_delay = multipath_delay
        transmission.signal_strength = interference_factor
        
        # Calculate physics-based loss probability
        loss_prob, loss_reason = self.calculate_packet_loss_probability(
            distance, ship_depth, sub_depth, data_size)
        
        # Physics-based packet delivery decision using the same random module for consistent seeding
        # P_loss is probability of loss, so (1 - P_loss) is probability of success
        if random.random() < (1.0 - loss_prob):
            # Packet successfully received
            transmission.arrival_time = transmission.transmission_time + transmission.total_delay
        else:
            # Packet lost
            transmission.is_lost = True
            transmission.loss_reason = loss_reason
        
        return transmission
    
    def update_environment(self, sea_state: int = None, temperature: float = None):
        """Update environmental conditions"""
        if sea_state is not None:
            self.environment.sea_state = max(0, min(6, sea_state))
        if temperature is not None:
            self.environment.water_temperature = temperature
    
    def get_communication_quality(self, distance: float, ship_depth: float, sub_depth: float) -> Dict:
        """Get current communication quality metrics"""
        prop_loss = self.calculate_propagation_loss(distance, self.frequency, sub_depth)
        received_power = self.transmission_power - prop_loss
        snr = received_power - self.noise_level
        
        loss_prob, reason = self.calculate_packet_loss_probability(
            distance, ship_depth, sub_depth, 50)  # Standard packet size
        
        return {
            'distance': distance,
            'propagation_loss_db': prop_loss,
            'snr_db': snr,
            'packet_loss_probability': loss_prob,
            'quality_reason': reason,
            'max_reliable_range': self.max_reliable_range,
            'sound_velocity': self.environment.calculate_sound_velocity(sub_depth, self.environment.water_temperature)
        } 

    def update_physics_config(self, new_config: AcousticPhysicsConfig):
        """Update physics configuration and recalculate cached values"""
        self.physics_config = new_config
        
        # Update main parameters
        self.frequency = self.physics_config.frequency_hz
        self.transmission_power = self.physics_config.transmission_power_db
        self.noise_level = self.physics_config.noise_level_db
        
        # Update physics parameters
        self.P0 = self.physics_config.transmission_power_linear
        self.noise_psd = self.physics_config.noise_power_linear
        self.gamma_req = self.physics_config.required_snr_linear
        self.spreading_exp = self.physics_config.spreading_exponent
        self.anomaly_db = self.physics_config.site_anomaly_db
        
        # Recalculate cached values
        self._f_khz = self.physics_config.frequency_khz
        self._alpha_cached = alpha_thorp(self._f_khz)
        self._anomaly_linear_cached = 10.0 ** (self.anomaly_db / 10.0) 