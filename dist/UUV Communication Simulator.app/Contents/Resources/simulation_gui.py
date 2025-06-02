#!/usr/bin/env python3
"""
🌊 UUV COMMUNICATION SIMULATION GUI 🌊
Beautiful graphical interface for underwater acoustic communication simulation

Features:
- Interactive main menu
- Configuration forms with tooltips
- Real-time simulation monitoring  
- Results visualization
- Export capabilities
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import json
import os
from datetime import datetime
import queue
import gc  # Garbage collection for memory management

from models.acoustic_config import (
    DEFAULT_CONFIG, HARSH_ENVIRONMENT_CONFIG, SHALLOW_WATER_CONFIG,
    DEEP_WATER_CONFIG, HIGH_NOISE_CONFIG, LOW_POWER_CONFIG, AcousticPhysicsConfig,
    REALISTIC_TESTING_CONFIG
)
from complex_simulation import run_complex_simulation, run_configuration_comparison
from models.csv_logger import CSVLogger
from models.ml_csv_logger import MLOptimizedCSVLogger

class ToolTip:
    """Enhanced tooltip class for providing detailed information"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
    
    def on_enter(self, event=None):
        if self.tooltip_window is not None:
            return
        x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(tw, text=self.text, justify='left',
                        background='#1e1e2e', foreground='#cdd6f4',
                        relief='solid', borderwidth=1,
                        font=('Arial', 9), wraplength=300)
        label.pack()
    
    def on_leave(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class UUVSimulationGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🌊 UUV Communication Simulation")
        self.root.geometry("1400x900")
        self.root.configure(bg='#0a0a0a')  # Military black background
        
        # Style configuration
        self.setup_styles()
        
        # Data storage
        self.current_config = DEFAULT_CONFIG
        self.simulation_results = None
        self.simulation_controller = None  # Store controller for CSV export
        self.simulation_thread = None
        self.simulation_queue = queue.Queue()
        self._last_config_name = "default"
        
        # Simulation variables - ADDED MISSING VARIABLES
        self.ticks_var = tk.IntVar(value=5000)
        self.world_size_var = tk.DoubleVar(value=1000.0)
        self.sim_type_var = tk.StringVar(value="single")
        self.progress_var = tk.DoubleVar(value=0.0)
        
        # Initialize experimental params
        self.experimental_params = {}
        
        # Create main interface
        self.create_main_interface()
        
    def setup_styles(self):
        """Setup military-grade tactical interface styles"""
        style = ttk.Style()
        
        # Use a military theme base
        style.theme_use('clam')
        
        # MILITARY COLOR PALETTE - Nuclear submarine vibes
        military_black = '#0a0a0a'      # Deep command center black
        military_dark = '#1a1a1a'       # Dark panel background
        military_gray = '#2d2d2d'       # Medium military gray
        military_light = '#3d3d3d'      # Light panel elements
        
        military_green = '#00ff41'      # Radar/terminal green
        military_amber = '#ffb000'      # Warning amber
        military_red = '#ff0030'        # Alert red
        military_blue = '#0080ff'       # System blue
        military_white = '#e0e0e0'      # Clean white text
        
        # Configure the root window with military styling
        self.root.option_add('*TCombobox*Listbox.selectBackground', military_green)
        
        # TITLE STYLES - Command center headers
        style.configure('Military.Title.TLabel', 
                       font=('Consolas', 18, 'bold'), 
                       foreground=military_green,
                       background=military_black,
                       relief='flat')
        
        style.configure('Military.Header.TLabel',
                       font=('Consolas', 14, 'bold'),
                       foreground=military_white,
                       background=military_dark,
                       relief='flat')
        
        style.configure('Military.Info.TLabel',
                       font=('Consolas', 10),
                       foreground=military_white,
                       background=military_dark,
                       relief='flat')
        
        # BUTTON STYLES - Tactical interface buttons
        style.configure('Military.TButton',
                       font=('Consolas', 10, 'bold'),
                       foreground=military_white,
                       background=military_gray,
                       borderwidth=2,
                       relief='raised',
                       focuscolor='none')
        
        style.map('Military.TButton',
                 background=[('active', military_green),
                           ('pressed', military_blue)])
        
        # CRITICAL ACTION BUTTONS
        style.configure('Critical.TButton',
                       font=('Consolas', 12, 'bold'),
                       foreground=military_black,
                       background=military_red,
                       borderwidth=3,
                       relief='raised')
        
        style.map('Critical.TButton',
                 background=[('active', '#ff3050'),
                           ('pressed', '#cc0020')])
        
        # FRAMES AND PANELS
        style.configure('Military.TFrame',
                       background=military_dark,
                       borderwidth=2,
                       relief='solid')
        
        style.configure('Military.TLabelFrame',
                       background=military_dark,
                       borderwidth=2,
                       relief='solid',
                       labeloutside=False)
        
        style.configure('Military.TLabelFrame.Label',
                       font=('Consolas', 11, 'bold'),
                       foreground=military_green,
                       background=military_dark)
        
        # NOTEBOOK TABS - Command center sections
        style.configure('Military.TNotebook',
                       background=military_black,
                       borderwidth=0)
        
        style.configure('Military.TNotebook.Tab',
                       font=('Consolas', 10, 'bold'),
                       foreground=military_white,
                       background=military_gray,
                       borderwidth=2,
                       padding=[12, 8])
        
        style.map('Military.TNotebook.Tab',
                 background=[('selected', military_green),
                           ('active', military_blue)],
                 foreground=[('selected', military_black),
                           ('active', military_white)])

    def create_main_interface(self):
        """Create the main tactical command interface"""
        # Main container with military styling
        main_frame = tk.Frame(self.root, bg='#0a0a0a', relief='solid', borderwidth=2)
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Command center title bar
        title_frame = tk.Frame(main_frame, bg='#1a1a1a', relief='raised', borderwidth=3)
        title_frame.pack(fill='x', padx=2, pady=2)
        
        title_label = tk.Label(title_frame, 
                              text="⚡ TACTICAL UUV COMMAND & CONTROL SYSTEM ⚡", 
                              font=('Consolas', 16, 'bold'),
                              fg='#00ff41', bg='#1a1a1a')
        title_label.pack(pady=8)
        
        # Classification banner
        classification = tk.Label(title_frame,
                                text="CLASSIFIED - MILITARY SIMULATION SYSTEM",
                                font=('Consolas', 8, 'bold'),
                                fg='#ff0030', bg='#1a1a1a')
        classification.pack()
        
        # Create military-styled notebook
        self.notebook = ttk.Notebook(main_frame, style='Military.TNotebook')
        self.notebook.pack(fill='both', expand=True, padx=2, pady=5)
        
        # Create tabs with military designations
        self.create_home_tab()
        self.create_config_tab()
        self.create_simulation_tab()
        self.create_monitor_tab()
        self.create_results_tab()

    def create_home_tab(self):
        """Create tactical command center home interface"""
        home_frame = tk.Frame(self.notebook, bg='#0a0a0a')
        self.notebook.add(home_frame, text="COMMAND CENTER")
        
        # Welcome panel with military styling
        welcome_frame = tk.Frame(home_frame, bg='#1a1a1a', relief='solid', borderwidth=3)
        welcome_frame.pack(fill='x', padx=5, pady=5)
        
        # Welcome header
        welcome_header = tk.Label(welcome_frame,
                                text="TACTICAL UUV COMMUNICATION SYSTEM",
                                font=('Consolas', 14, 'bold'),
                                fg='#00ff41', bg='#1a1a1a')
        welcome_header.pack(pady=8)
        
        welcome_text = """CLASSIFIED UNDERWATER ACOUSTIC WARFARE SIMULATION
        
MISSION CAPABILITIES:
• Physics-based acoustic propagation modeling
• Real-time tactical communication analysis  
• Advanced sonar detection algorithms
• Comprehensive mission data intelligence
• Strategic deployment parameter optimization

OPERATIONAL PROCEDURES:
1. Configure tactical parameters in MISSION CONFIG
2. Initialize simulation in TACTICAL CONTROL
3. Monitor real-time intelligence in TACTICAL DISPLAY
4. Analyze mission results in INTELLIGENCE REPORT

WARNING: AUTHORIZED PERSONNEL ONLY"""
        
        welcome_text_label = tk.Label(welcome_frame, 
                                    text=welcome_text,
                                    font=('Consolas', 10),
                                    fg='#e0e0e0', bg='#1a1a1a',
                                    justify='left')
        welcome_text_label.pack(padx=20, pady=10)
        
        # Command buttons panel
        command_frame = tk.Frame(home_frame, bg='#1a1a1a', relief='solid', borderwidth=3)
        command_frame.pack(fill='x', padx=5, pady=5)
        
        command_header = tk.Label(command_frame,
                                text="TACTICAL COMMAND OPTIONS",
                                font=('Consolas', 12, 'bold'),
                                fg='#00ff41', bg='#1a1a1a')
        command_header.pack(pady=5)
        
        btn_frame = tk.Frame(command_frame, bg='#1a1a1a')
        btn_frame.pack(pady=10)
        
        # Military-styled buttons - REMOVED ICONS
        quick_demo_btn = tk.Button(btn_frame, 
                                 text="RAPID DEPLOYMENT", 
                                 command=self.quick_demo,
                                 font=('Consolas', 10, 'bold'),
                                 fg='#000000', bg='#00ff41',
                                 relief='raised', borderwidth=3,
                                 padx=15, pady=5)
        quick_demo_btn.pack(side='left', padx=10)
        
        config_btn = tk.Button(btn_frame,
                             text="MISSION CONFIG",
                             command=lambda: self.notebook.select(1),
                             font=('Consolas', 10, 'bold'),
                             fg='#e0e0e0', bg='#2d2d2d',
                             relief='raised', borderwidth=3,
                             padx=15, pady=5)
        config_btn.pack(side='left', padx=10)
        
        sim_btn = tk.Button(btn_frame,
                          text="TACTICAL CONTROL",
                          command=lambda: self.notebook.select(2),
                          font=('Consolas', 10, 'bold'),
                          fg='#e0e0e0', bg='#2d2d2d',
                          relief='raised', borderwidth=3,
                          padx=15, pady=5)
        sim_btn.pack(side='left', padx=10)
        
        # System status panel
        self.status_frame = tk.Frame(home_frame, bg='#2d2d2d', relief='solid', borderwidth=3)
        self.status_frame.pack(fill='x', padx=5, pady=5)
        
        status_header = tk.Label(self.status_frame,
                               text="SYSTEM STATUS",
                               font=('Consolas', 11, 'bold'),
                               fg='#00ff41', bg='#2d2d2d')
        status_header.pack(pady=3)
        
        self.status_label = tk.Label(self.status_frame,
                                   text="ALL SYSTEMS OPERATIONAL - READY FOR DEPLOYMENT",
                                   font=('Consolas', 10, 'bold'),
                                   fg='#00ff41', bg='#2d2d2d')
        self.status_label.pack(pady=5)

    def create_config_tab(self):
        """Create tactical mission configuration interface"""
        config_frame = tk.Frame(self.notebook, bg='#0a0a0a')
        self.notebook.add(config_frame, text="MISSION CONFIG")
        
        # Create scrollable frame with military styling
        canvas = tk.Canvas(config_frame, bg='#0a0a0a', highlightthickness=0)
        scrollbar = tk.Scrollbar(config_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#0a0a0a')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mission preset configurations
        preset_frame = tk.Frame(scrollable_frame, bg='#1a1a1a', relief='solid', borderwidth=3)
        preset_frame.pack(fill='x', padx=5, pady=5)
        
        preset_header = tk.Label(preset_frame,
                               text="TACTICAL PRESET CONFIGURATIONS",
                               font=('Consolas', 12, 'bold'),
                               fg='#00ff41', bg='#1a1a1a')
        preset_header.pack(pady=8)
        
        preset_grid = tk.Frame(preset_frame, bg='#1a1a1a')
        preset_grid.pack(padx=10, pady=10)
        
        self.config_var = tk.StringVar(value="default")
        
        configs = [
            ("default", "DEFAULT TACTICAL", DEFAULT_CONFIG),
            ("shallow", "SHALLOW WATER OPS", SHALLOW_WATER_CONFIG),
            ("deep", "DEEP WATER OPS", DEEP_WATER_CONFIG),
            ("noise", "HIGH NOISE ENV", HIGH_NOISE_CONFIG),
            ("low_power", "LOW POWER MODE", LOW_POWER_CONFIG),
            ("harsh", "HARSH ENVIRONMENT", HARSH_ENVIRONMENT_CONFIG),
            ("realistic_testing", "REALISTIC TESTING", REALISTIC_TESTING_CONFIG)
        ]
        
        for i, (key, name, config) in enumerate(configs):
            row = i // 2
            col = i % 2
            
            # Military-styled radio button
            rb = tk.Radiobutton(preset_grid, text=name,
                               variable=self.config_var, value=key,
                               command=self.update_config_display,
                               font=('Consolas', 10, 'bold'),
                               fg='#e0e0e0', bg='#1a1a1a',
                               selectcolor='#00ff41',
                               activebackground='#2d2d2d',
                               activeforeground='#00ff41',
                               relief='raised', borderwidth=2,
                               padx=20, pady=8)
            rb.grid(row=row, column=col, sticky='ew', padx=5, pady=3)
        
        # Configure grid weights
        preset_grid.columnconfigure(0, weight=1)
        preset_grid.columnconfigure(1, weight=1)
        
        # Custom acoustic configuration
        custom_frame = tk.Frame(scrollable_frame, bg='#1a1a1a', relief='solid', borderwidth=3)
        custom_frame.pack(fill='x', padx=5, pady=5)
        
        custom_header = tk.Label(custom_frame,
                               text="CUSTOM ACOUSTIC PARAMETERS",
                               font=('Consolas', 12, 'bold'),
                               fg='#00ff41', bg='#1a1a1a')
        custom_header.pack(pady=8)
        
        # Configuration parameters
        self.create_config_form(custom_frame)
        
        # Experimental parameters section
        experimental_frame = tk.Frame(scrollable_frame, bg='#1a1a1a', relief='solid', borderwidth=3)
        experimental_frame.pack(fill='x', padx=5, pady=5)
        
        exp_header = tk.Label(experimental_frame,
                            text="EXPERIMENTAL PARAMETERS",
                            font=('Consolas', 12, 'bold'),
                            fg='#ffb000', bg='#1a1a1a')
        exp_header.pack(pady=5)
        
        exp_warning = tk.Label(experimental_frame,
                             text="ADVANCED TACTICAL PARAMETERS - MODIFY WITH CAUTION",
                             font=('Consolas', 9, 'bold'),
                             fg='#ff0030', bg='#1a1a1a')
        exp_warning.pack(pady=3)
        
        self.create_experimental_form(experimental_frame)
        
        # Current configuration display
        display_frame = tk.Frame(scrollable_frame, bg='#1a1a1a', relief='solid', borderwidth=3)
        display_frame.pack(fill='x', padx=5, pady=5)
        
        display_header = tk.Label(display_frame,
                                text="CURRENT MISSION CONFIGURATION",
                                font=('Consolas', 12, 'bold'),
                                fg='#00ff41', bg='#1a1a1a')
        display_header.pack(pady=8)
        
        self.config_display = tk.Text(display_frame,
                                    height=8,
                                    bg='#2d2d2d', fg='#e0e0e0',
                                    font=('Consolas', 9),
                                    relief='sunken', borderwidth=2)
        self.config_display.pack(fill='x', padx=10, pady=10)
        
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        self.update_config_display()

    def create_experimental_form(self, parent):
        """Create experimental parameters form for advanced simulation control"""
        
        # Tooltip texts for experimental parameters
        exp_tooltips = {
            'safe_distance': """Max Safe Distance from Ship (meters)
            
How far the submarine can travel before it starts returning to ship.

• 500-800m: Conservative operation, stays close to ship
• 1000-1500m: Standard operation, good range
• 2000-3000m: Extended range operation
• 5000-10000m: Long range missions, may lose communication
• 15000m+: Extreme range, high packet loss expected

The submarine will automatically return when it reaches 80% of this distance.
Higher values allow more exploration but risk communication loss.""",
            
            'world_size': """World Boundary Size (meters)
            
The size of the simulation world (square area centered on ship).

• 500-1000m: Small world, quick simulations
• 1000-2000m: Standard world size
• 2000-5000m: Large world, extended missions
• 5000-15000m: Massive world, very long simulations
• 20000m+: Extreme world size, use with caution

Objects are scattered within this area. Larger worlds = more exploration time.""",
            
            'detection_range': """Submarine Detection Range (meters)
            
How close the submarine must be to detect objects.

• 20-30m: Short range sensors, must get very close
• 40-60m: Standard sonar range
• 80-100m: Long range sensors, easier detection
• 150-300m: Advanced sensor suite
• 500m+: Experimental long-range detection

Lower values make missions more challenging as submarine must approach objects closely.""",
            
            'sub_speed': """Submarine Movement Speed (meters/tick)
            
How fast the submarine moves per simulation tick.

• 2-3 m/tick: Slow, careful exploration
• 4-6 m/tick: Standard submarine speed
• 8-12 m/tick: Fast exploration
• 15-25 m/tick: High speed operation
• 30+ m/tick: Extreme speed (unrealistic but good for testing)

Higher speeds cover more ground but may miss objects or overshoot targets.""",
            
            'max_range': """Maximum Operational Range (meters)
            
Total distance submarine can travel from start point during entire mission.

• 1000-2000m: Limited range missions
• 3000-5000m: Standard range operations  
• 8000-15000m: Extended range missions
• 20000-50000m: Long range operations
• 100000m+: Extreme range, high packet loss guaranteed

This is the TOTAL distance the submarine can travel, affecting packet loss significantly.""",
            
            'movement_pattern': """Movement Pattern Aggressiveness
            
How aggressively the submarine explores (affects distance from ship).

• 0.1-0.3: Conservative, stays close to ship
• 0.4-0.6: Balanced exploration
• 0.7-0.8: Aggressive exploration
• 0.9-1.0: Maximum aggression, travels to limits

Higher values make submarine venture further from ship, increasing packet loss.""",
            
            'turn_rate': """Submarine Turn Rate (degrees/tick)
            
How quickly the submarine can change direction.

• 5-10°/tick: Slow, realistic submarine turning
• 10-20°/tick: Standard maneuverability  
• 30-45°/tick: High maneuverability
• 60-90°/tick: Very agile maneuvering
• 120°+ /tick: Unrealistically agile

Higher turn rates allow more responsive navigation but may be unrealistic.""",
            
            'depth_rate': """Depth Change Rate (meters/tick)
            
How fast the submarine can ascend or descend.

• 1-2 m/tick: Slow, careful depth changes
• 2-4 m/tick: Standard submarine rates
• 5-8 m/tick: Fast depth changes
• 10-15 m/tick: Very fast depth changes
• 20+ m/tick: Extreme depth change rates

Affects how quickly submarine can change operating depth for better detection."""
        }
        
        # Create three-column layout for experimental parameters
        exp_columns = ttk.Frame(parent)
        exp_columns.pack(fill='x')
        
        left_exp = ttk.Frame(exp_columns)
        left_exp.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        center_exp = ttk.Frame(exp_columns)
        center_exp.pack(side='left', fill='both', expand=True, padx=5)
        
        right_exp = ttk.Frame(exp_columns)
        right_exp.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # Left column - Mission Parameters
        mission_label = ttk.Label(left_exp, text="MISSION PARAMETERS", style='Heading.TLabel', foreground='#89b4fa')
        mission_label.pack(pady=(0, 10))
        
        # Max Safe Distance
        safe_dist_frame = ttk.Frame(left_exp)
        safe_dist_frame.pack(fill='x', pady=5)
        
        safe_dist_label_frame = ttk.Frame(safe_dist_frame)
        safe_dist_label_frame.pack(fill='x')
        
        ttk.Label(safe_dist_label_frame, text="Max Safe Distance (m):", style='Heading.TLabel').pack(side='left')
        safe_dist_info = ttk.Label(safe_dist_label_frame, text=" INFO", style='Info.TLabel', foreground='#89b4fa')
        safe_dist_info.pack(side='left')
        ToolTip(safe_dist_info, exp_tooltips['safe_distance'])
        
        safe_dist_controls = ttk.Frame(safe_dist_frame)
        safe_dist_controls.pack(fill='x')
        
        self.safe_distance_var = tk.DoubleVar(value=5000.0)  # Increased default
        safe_dist_scale = ttk.Scale(safe_dist_controls, from_=500, to=20000, variable=self.safe_distance_var, orient='horizontal')
        safe_dist_scale.pack(side='left', fill='x', expand=True)
        self.safe_distance_label = ttk.Label(safe_dist_controls, text="5000m", style='Info.TLabel', width=10)
        self.safe_distance_label.pack(side='right', padx=(10, 0))
        safe_dist_scale.configure(command=self.update_safe_distance_label)
        
        # World Size
        world_size_frame = ttk.Frame(left_exp)
        world_size_frame.pack(fill='x', pady=5)
        
        world_size_label_frame = ttk.Frame(world_size_frame)
        world_size_label_frame.pack(fill='x')
        
        ttk.Label(world_size_label_frame, text="World Size (m):", style='Heading.TLabel').pack(side='left')
        world_size_info = ttk.Label(world_size_label_frame, text=" INFO", style='Info.TLabel', foreground='#89b4fa')
        world_size_info.pack(side='left')
        ToolTip(world_size_info, exp_tooltips['world_size'])
        
        world_size_controls = ttk.Frame(world_size_frame)
        world_size_controls.pack(fill='x')
        
        self.exp_world_size_var = tk.DoubleVar(value=3000.0)  # Increased default
        world_size_scale = ttk.Scale(world_size_controls, from_=500, to=25000, variable=self.exp_world_size_var, orient='horizontal')
        world_size_scale.pack(side='left', fill='x', expand=True)
        self.exp_world_size_label = ttk.Label(world_size_controls, text="3000m", style='Info.TLabel', width=10)
        self.exp_world_size_label.pack(side='right', padx=(10, 0))
        world_size_scale.configure(command=self.update_exp_world_size_label)
        
        # Detection Range
        detect_range_frame = ttk.Frame(left_exp)
        detect_range_frame.pack(fill='x', pady=5)
        
        detect_range_label_frame = ttk.Frame(detect_range_frame)
        detect_range_label_frame.pack(fill='x')
        
        ttk.Label(detect_range_label_frame, text="Detection Range (m):", style='Heading.TLabel').pack(side='left')
        detect_range_info = ttk.Label(detect_range_label_frame, text=" INFO", style='Info.TLabel', foreground='#89b4fa')
        detect_range_info.pack(side='left')
        ToolTip(detect_range_info, exp_tooltips['detection_range'])
        
        detect_range_controls = ttk.Frame(detect_range_frame)
        detect_range_controls.pack(fill='x')
        
        self.detection_range_var = tk.DoubleVar(value=80.0)  # Increased default
        detect_range_scale = ttk.Scale(detect_range_controls, from_=20, to=500, variable=self.detection_range_var, orient='horizontal')
        detect_range_scale.pack(side='left', fill='x', expand=True)
        self.detection_range_label = ttk.Label(detect_range_controls, text="80m", style='Info.TLabel', width=10)
        self.detection_range_label.pack(side='right', padx=(10, 0))
        detect_range_scale.configure(command=self.update_detection_range_label)
        
        # Center column - Movement Parameters
        movement_label = ttk.Label(center_exp, text="MOVEMENT PARAMETERS", style='Heading.TLabel', foreground='#89b4fa')
        movement_label.pack(pady=(0, 10))
        
        # Maximum Operational Range
        max_range_frame = ttk.Frame(center_exp)
        max_range_frame.pack(fill='x', pady=5)
        
        max_range_label_frame = ttk.Frame(max_range_frame)
        max_range_label_frame.pack(fill='x')
        
        ttk.Label(max_range_label_frame, text="Max Operational Range (m):", style='Heading.TLabel').pack(side='left')
        max_range_info = ttk.Label(max_range_label_frame, text=" INFO", style='Info.TLabel', foreground='#89b4fa')
        max_range_info.pack(side='left')
        ToolTip(max_range_info, exp_tooltips['max_range'])
        
        max_range_controls = ttk.Frame(max_range_frame)
        max_range_controls.pack(fill='x')
        
        self.max_range_var = tk.DoubleVar(value=15000.0)  # New parameter
        max_range_scale = ttk.Scale(max_range_controls, from_=1000, to=100000, variable=self.max_range_var, orient='horizontal')
        max_range_scale.pack(side='left', fill='x', expand=True)
        self.max_range_label = ttk.Label(max_range_controls, text="15000m", style='Info.TLabel', width=12)
        self.max_range_label.pack(side='right', padx=(10, 0))
        max_range_scale.configure(command=self.update_max_range_label)
        
        # Movement Pattern Aggressiveness
        movement_pattern_frame = ttk.Frame(center_exp)
        movement_pattern_frame.pack(fill='x', pady=5)
        
        movement_pattern_label_frame = ttk.Frame(movement_pattern_frame)
        movement_pattern_label_frame.pack(fill='x')
        
        ttk.Label(movement_pattern_label_frame, text="Movement Aggressiveness:", style='Heading.TLabel').pack(side='left')
        movement_pattern_info = ttk.Label(movement_pattern_label_frame, text=" INFO", style='Info.TLabel', foreground='#89b4fa')
        movement_pattern_info.pack(side='left')
        ToolTip(movement_pattern_info, exp_tooltips['movement_pattern'])
        
        movement_pattern_controls = ttk.Frame(movement_pattern_frame)
        movement_pattern_controls.pack(fill='x')
        
        self.movement_pattern_var = tk.DoubleVar(value=0.7)  # New parameter
        movement_pattern_scale = ttk.Scale(movement_pattern_controls, from_=0.1, to=1.0, variable=self.movement_pattern_var, orient='horizontal')
        movement_pattern_scale.pack(side='left', fill='x', expand=True)
        self.movement_pattern_label = ttk.Label(movement_pattern_controls, text="0.7", style='Info.TLabel', width=12)
        self.movement_pattern_label.pack(side='right', padx=(10, 0))
        movement_pattern_scale.configure(command=self.update_movement_pattern_label)
        
        # Submarine Speed
        sub_speed_frame = ttk.Frame(center_exp)
        sub_speed_frame.pack(fill='x', pady=5)
        
        sub_speed_label_frame = ttk.Frame(sub_speed_frame)
        sub_speed_label_frame.pack(fill='x')
        
        ttk.Label(sub_speed_label_frame, text="Submarine Speed (m/tick):", style='Heading.TLabel').pack(side='left')
        sub_speed_info = ttk.Label(sub_speed_label_frame, text=" INFO", style='Info.TLabel', foreground='#89b4fa')
        sub_speed_info.pack(side='left')
        ToolTip(sub_speed_info, exp_tooltips['sub_speed'])
        
        sub_speed_controls = ttk.Frame(sub_speed_frame)
        sub_speed_controls.pack(fill='x')
        
        self.sub_speed_var = tk.DoubleVar(value=12.0)  # Increased default
        sub_speed_scale = ttk.Scale(sub_speed_controls, from_=1, to=50, variable=self.sub_speed_var, orient='horizontal')
        sub_speed_scale.pack(side='left', fill='x', expand=True)
        self.sub_speed_label = ttk.Label(sub_speed_controls, text="12.0 m/tick", style='Info.TLabel', width=12)
        self.sub_speed_label.pack(side='right', padx=(10, 0))
        sub_speed_scale.configure(command=self.update_sub_speed_label)
        
        # Right column - Vehicle Parameters
        vehicle_label = ttk.Label(right_exp, text="VEHICLE PARAMETERS", style='Heading.TLabel', foreground='#89b4fa')
        vehicle_label.pack(pady=(0, 10))
        
        # Turn Rate
        turn_rate_frame = ttk.Frame(right_exp)
        turn_rate_frame.pack(fill='x', pady=5)
        
        turn_rate_label_frame = ttk.Frame(turn_rate_frame)
        turn_rate_label_frame.pack(fill='x')
        
        ttk.Label(turn_rate_label_frame, text="Turn Rate (°/tick):", style='Heading.TLabel').pack(side='left')
        turn_rate_info = ttk.Label(turn_rate_label_frame, text=" INFO", style='Info.TLabel', foreground='#89b4fa')
        turn_rate_info.pack(side='left')
        ToolTip(turn_rate_info, exp_tooltips['turn_rate'])
        
        turn_rate_controls = ttk.Frame(turn_rate_frame)
        turn_rate_controls.pack(fill='x')
        
        self.turn_rate_var = tk.DoubleVar(value=15.0)  # Increased default
        turn_rate_scale = ttk.Scale(turn_rate_controls, from_=5, to=150, variable=self.turn_rate_var, orient='horizontal')
        turn_rate_scale.pack(side='left', fill='x', expand=True)
        self.turn_rate_label = ttk.Label(turn_rate_controls, text="15.0°/tick", style='Info.TLabel', width=12)
        self.turn_rate_label.pack(side='right', padx=(10, 0))
        turn_rate_scale.configure(command=self.update_turn_rate_label)
        
        # Depth Change Rate
        depth_rate_frame = ttk.Frame(right_exp)
        depth_rate_frame.pack(fill='x', pady=5)
        
        depth_rate_label_frame = ttk.Frame(depth_rate_frame)
        depth_rate_label_frame.pack(fill='x')
        
        ttk.Label(depth_rate_label_frame, text="Depth Change Rate (m/tick):", style='Heading.TLabel').pack(side='left')
        depth_rate_info = ttk.Label(depth_rate_label_frame, text=" INFO", style='Info.TLabel', foreground='#89b4fa')
        depth_rate_info.pack(side='left')
        ToolTip(depth_rate_info, exp_tooltips['depth_rate'])
        
        depth_rate_controls = ttk.Frame(depth_rate_frame)
        depth_rate_controls.pack(fill='x')
        
        self.depth_rate_var = tk.DoubleVar(value=5.0)  # Increased default
        depth_rate_scale = ttk.Scale(depth_rate_controls, from_=1, to=30, variable=self.depth_rate_var, orient='horizontal')
        depth_rate_scale.pack(side='left', fill='x', expand=True)
        self.depth_rate_label = ttk.Label(depth_rate_controls, text="5.0 m/tick", style='Info.TLabel', width=12)
        self.depth_rate_label.pack(side='right', padx=(10, 0))
        depth_rate_scale.configure(command=self.update_depth_rate_label)
        
        # High-Performance Mode Warning
        warning_frame = ttk.Frame(parent)
        warning_frame.pack(fill='x', pady=10)
        
        warning_label = ttk.Label(warning_frame,
                                text="⚠️ HIGH-PERFORMANCE MODE SETTINGS",
                                style='Heading.TLabel',
                                foreground='#ff0030')
        warning_label.pack()
        
        warning_text = ttk.Label(warning_frame,
                               text="For 1M+ ticks: Use max range 50000m+, speed 20+ m/tick, aggressiveness 0.8+",
                               style='Info.TLabel',
                               foreground='#ffb000')
        warning_text.pack()
        
        # Apply experimental parameters button
        apply_exp_btn = ttk.Button(parent, text="Apply Experimental Parameters", 
                                  command=self.apply_experimental_params, style='Custom.TButton')
        apply_exp_btn.pack(pady=15)
        
    # Update label methods for experimental parameters
    def update_safe_distance_label(self, value):
        self.safe_distance_label.config(text=f"{float(value):.0f}m")
        
    def update_exp_world_size_label(self, value):
        self.exp_world_size_label.config(text=f"{float(value):.0f}m")
        
    def update_detection_range_label(self, value):
        self.detection_range_label.config(text=f"{float(value):.0f}m")
        
    def update_max_range_label(self, value):
        self.max_range_label.config(text=f"{float(value):.0f}m")
        
    def update_movement_pattern_label(self, value):
        self.movement_pattern_label.config(text=f"{float(value):.2f}")
        
    def update_sub_speed_label(self, value):
        self.sub_speed_label.config(text=f"{float(value):.1f} m/tick")
        
    def update_turn_rate_label(self, value):
        self.turn_rate_label.config(text=f"{float(value):.1f}°/tick")
        
    def update_depth_rate_label(self, value):
        self.depth_rate_label.config(text=f"{float(value):.1f} m/tick")
    
    def apply_experimental_params(self):
        """Apply experimental parameters to the simulation"""
        try:
            # Store experimental parameters for use during simulation creation
            self.experimental_params = {
                'max_safe_distance': self.safe_distance_var.get(),
                'world_size': self.exp_world_size_var.get(),
                'detection_range': self.detection_range_var.get(),
                'submarine_speed': self.sub_speed_var.get(),
                'turn_rate': self.turn_rate_var.get(),
                'depth_rate': self.depth_rate_var.get(),
                'max_range': self.max_range_var.get(),
                'movement_pattern': self.movement_pattern_var.get()
            }
            
            # Update the world size in the simulation tab
            self.world_size_var.set(self.experimental_params['world_size'])
            
            self.log_sci_fi_message("EXPERIMENTAL PARAMETERS APPLIED", "SYSTEM")
            self.log_sci_fi_message(f"   Safe Distance: {self.experimental_params['max_safe_distance']:.0f}m", "INFO")
            self.log_sci_fi_message(f"   World Size: {self.experimental_params['world_size']:.0f}m", "INFO")
            self.log_sci_fi_message(f"   Detection Range: {self.experimental_params['detection_range']:.0f}m", "INFO")
            self.log_sci_fi_message(f"   Sub Speed: {self.experimental_params['submarine_speed']:.1f} m/tick", "INFO")
            self.log_sci_fi_message(f"   Max Range: {self.experimental_params['max_range']:.0f}m", "INFO")
            self.log_sci_fi_message(f"   Movement Pattern: {self.experimental_params['movement_pattern']:.2f}", "INFO")
            
            messagebox.showinfo("Experimental Parameters Applied", 
                              f"Experimental parameters updated!\n\n"
                              f"Max Safe Distance: {self.experimental_params['max_safe_distance']:.0f}m\n"
                              f"World Size: {self.experimental_params['world_size']:.0f}m\n"
                              f"Detection Range: {self.experimental_params['detection_range']:.0f}m\n"
                              f"Submarine Speed: {self.experimental_params['submarine_speed']:.1f} m/tick\n"
                              f"Turn Rate: {self.experimental_params['turn_rate']:.1f}°/tick\n"
                              f"Depth Rate: {self.experimental_params['depth_rate']:.1f} m/tick\n"
                              f"Max Range: {self.experimental_params['max_range']:.0f}m\n"
                              f"Movement Pattern: {self.experimental_params['movement_pattern']:.2f}\n\n"
                              f"These will be applied to the next simulation!")
                              
        except Exception as e:
            messagebox.showerror("Experimental Error", f"Error applying experimental parameters: {str(e)}")

    def update_config_display(self):
        """Update configuration display"""
        config_map = {
            "default": DEFAULT_CONFIG,
            "shallow": SHALLOW_WATER_CONFIG,
            "deep": DEEP_WATER_CONFIG,
            "noise": HIGH_NOISE_CONFIG,
            "low_power": LOW_POWER_CONFIG,
            "harsh": HARSH_ENVIRONMENT_CONFIG,
            "realistic_testing": REALISTIC_TESTING_CONFIG
        }
        
        config = config_map.get(self.config_var.get(), DEFAULT_CONFIG)
        self.current_config = config
        
        # Get experimental params if they exist
        exp_params = getattr(self, 'experimental_params', {})
        
        display_text = f"""🌊 ACOUSTIC CONFIGURATION: {self.config_var.get().upper()}
Transmission Power: {config.transmission_power_db} dB re 1 μPa
Frequency: {config.frequency_hz/1000:.1f} kHz
Noise Level: {config.noise_level_db} dB re 1 μPa
Required SNR: {config.required_snr_db} dB
Spreading Exponent: {config.spreading_exponent}
Site Anomaly: {config.site_anomaly_db:+.1f} dB

🧪 EXPERIMENTAL PARAMETERS:"""
        
        if exp_params:
            display_text += f"""
Max Safe Distance: {exp_params['max_safe_distance']:.0f}m
World Size: {exp_params['world_size']:.0f}m  
Detection Range: {exp_params['detection_range']:.0f}m
Submarine Speed: {exp_params['submarine_speed']:.1f} m/tick
Turn Rate: {exp_params['turn_rate']:.1f}°/tick
Depth Rate: {exp_params['depth_rate']:.1f} m/tick
Max Range: {exp_params['max_range']:.0f}m
Movement Pattern: {exp_params['movement_pattern']:.2f}"""
        else:
            display_text += f"""
Max Safe Distance: 2000m (default)
World Size: 1000m (default)
Detection Range: 50m (default)  
Submarine Speed: 5.0 m/tick (default)
Turn Rate: 10.0°/tick (default)
Depth Rate: 2.0 m/tick (default)
Max Range: 1000m (default)
Movement Pattern: 0.5 (default)"""
        
        self.config_display.delete(1.0, tk.END)
        self.config_display.insert(1.0, display_text)
        
        # Update form values to match current config
        self.power_var.set(config.transmission_power_db)
        self.freq_var.set(config.frequency_hz / 1000)
        self.noise_var.set(config.noise_level_db)
        self.snr_var.set(config.required_snr_db)
        self.spread_var.set(config.spreading_exponent)
        self.anomaly_var.set(config.site_anomaly_db)
    
    def create_config_form(self, parent):
        """Create configuration form with tooltips and improved layout"""
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill='both', expand=True)
        
        # Tooltip texts for detailed explanations
        tooltips = {
            'power': """Transmission Power (dB re 1 μPa)
            
The source level of the acoustic transmitter measured in decibels relative to 1 micropascal at 1 meter.

• 150-170 dB: Low power operation, suitable for short range
• 170-180 dB: Standard operation, good balance of range/power
• 180-190 dB: High power, maximum range but higher energy consumption

Typical Values:
• Small UUVs: 160-170 dB
• Large UUVs: 175-185 dB
• Ship sonar: 220+ dB""",
            
            'frequency': """Frequency (kHz)
            
The carrier frequency for acoustic communication. Lower frequencies travel farther but have lower data rates.

• 5-15 kHz: Long range, high absorption, low data rate
• 15-30 kHz: Medium range, moderate absorption, good data rate
• 30-50 kHz: Short range, low absorption, high data rate

Trade-offs:
• Lower frequency = longer range, more absorption
• Higher frequency = shorter range, less absorption
• Optimal frequency depends on range requirements""",
            
            'noise': """Noise Level (dB re 1 μPa)
            
Ambient underwater noise level that interferes with communication.

Sources of noise:
• 30-40 dB: Very quiet deep water
• 40-50 dB: Typical deep ocean
• 50-60 dB: Moderate shipping traffic
• 60-70 dB: Heavy shipping, coastal areas
• 70+ dB: Very noisy environments, storms

Higher noise requires higher transmission power or better receivers.""",
            
            'snr': """Required SNR (dB)
            
Signal-to-Noise Ratio required for successful packet reception.

• 5-10 dB: Basic communication, some errors expected
• 10-15 dB: Reliable communication, low error rate
• 15-20 dB: Very reliable, error correction possible

Lower SNR requirements allow longer range but with higher error rates.
Higher SNR ensures reliability but limits communication range.""",
            
            'spreading': """Spreading Exponent
            
Describes how acoustic energy spreads in the water column.

• 1.0: Cylindrical spreading (shallow water, waveguide effect)
• 1.5: Mixed spreading (transitional environments)
• 2.0: Spherical spreading (deep water, free field)

Environment effects:
• Shallow water (< 200m): Tends toward cylindrical (1.0-1.5)
• Deep water (> 1000m): Tends toward spherical (1.5-2.0)""",
            
            'anomaly': """Site Anomaly (dB)
            
Environmental propagation effects specific to the operating area.

• Negative values: Better than expected propagation
• Zero: Standard propagation conditions
• Positive values: Worse than expected propagation

Causes:
• Thermoclines, haloclines
• Bottom composition
• Surface conditions
• Geographic features"""
        }
        
        # Left column
        left_frame = ttk.Frame(form_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Power settings with tooltip
        power_frame = ttk.Frame(left_frame)
        power_frame.pack(fill='x', pady=5)
        
        power_label_frame = ttk.Frame(power_frame)
        power_label_frame.pack(fill='x')
        
        ttk.Label(power_label_frame, text="Transmission Power (dB re 1 μPa):", style='Heading.TLabel').pack(side='left')
        power_info = ttk.Label(power_label_frame, text=" ⓘ", style='Info.TLabel', foreground='#89b4fa')
        power_info.pack(side='left')
        ToolTip(power_info, tooltips['power'])
        
        power_controls = ttk.Frame(power_frame)
        power_controls.pack(fill='x')
        
        self.power_var = tk.DoubleVar(value=170.0)
        power_scale = ttk.Scale(power_controls, from_=150, to=190, variable=self.power_var, orient='horizontal')
        power_scale.pack(side='left', fill='x', expand=True)
        self.power_label = ttk.Label(power_controls, text="170.0 dB", style='Info.TLabel', width=10)
        self.power_label.pack(side='right', padx=(10, 0))
        power_scale.configure(command=self.update_power_label)
        
        # Frequency settings with tooltip
        freq_frame = ttk.Frame(left_frame)
        freq_frame.pack(fill='x', pady=5)
        
        freq_label_frame = ttk.Frame(freq_frame)
        freq_label_frame.pack(fill='x')
        
        ttk.Label(freq_label_frame, text="Frequency (kHz):", style='Heading.TLabel').pack(side='left')
        freq_info = ttk.Label(freq_label_frame, text=" ⓘ", style='Info.TLabel', foreground='#89b4fa')
        freq_info.pack(side='left')
        ToolTip(freq_info, tooltips['frequency'])
        
        freq_controls = ttk.Frame(freq_frame)
        freq_controls.pack(fill='x')
        
        self.freq_var = tk.DoubleVar(value=12.0)
        freq_scale = ttk.Scale(freq_controls, from_=5, to=50, variable=self.freq_var, orient='horizontal')
        freq_scale.pack(side='left', fill='x', expand=True)
        self.freq_label = ttk.Label(freq_controls, text="12.0 kHz", style='Info.TLabel', width=10)
        self.freq_label.pack(side='right', padx=(10, 0))
        freq_scale.configure(command=self.update_freq_label)
        
        # Noise settings with tooltip
        noise_frame = ttk.Frame(left_frame)
        noise_frame.pack(fill='x', pady=5)
        
        noise_label_frame = ttk.Frame(noise_frame)
        noise_label_frame.pack(fill='x')
        
        ttk.Label(noise_label_frame, text="Noise Level (dB re 1 μPa):", style='Heading.TLabel').pack(side='left')
        noise_info = ttk.Label(noise_label_frame, text=" ⓘ", style='Info.TLabel', foreground='#89b4fa')
        noise_info.pack(side='left')
        ToolTip(noise_info, tooltips['noise'])
        
        noise_controls = ttk.Frame(noise_frame)
        noise_controls.pack(fill='x')
        
        self.noise_var = tk.DoubleVar(value=50.0)
        noise_scale = ttk.Scale(noise_controls, from_=30, to=80, variable=self.noise_var, orient='horizontal')
        noise_scale.pack(side='left', fill='x', expand=True)
        self.noise_label = ttk.Label(noise_controls, text="50.0 dB", style='Info.TLabel', width=10)
        self.noise_label.pack(side='right', padx=(10, 0))
        noise_scale.configure(command=self.update_noise_label)
        
        # Right column
        right_frame = ttk.Frame(form_frame)
        right_frame.pack(side='right', fill='both', expand=True)
        
        # SNR settings with tooltip
        snr_frame = ttk.Frame(right_frame)
        snr_frame.pack(fill='x', pady=5)
        
        snr_label_frame = ttk.Frame(snr_frame)
        snr_label_frame.pack(fill='x')
        
        ttk.Label(snr_label_frame, text="Required SNR (dB):", style='Heading.TLabel').pack(side='left')
        snr_info = ttk.Label(snr_label_frame, text=" ⓘ", style='Info.TLabel', foreground='#89b4fa')
        snr_info.pack(side='left')
        ToolTip(snr_info, tooltips['snr'])
        
        snr_controls = ttk.Frame(snr_frame)
        snr_controls.pack(fill='x')
        
        self.snr_var = tk.DoubleVar(value=10.0)
        snr_scale = ttk.Scale(snr_controls, from_=5, to=20, variable=self.snr_var, orient='horizontal')
        snr_scale.pack(side='left', fill='x', expand=True)
        self.snr_label = ttk.Label(snr_controls, text="10.0 dB", style='Info.TLabel', width=10)
        self.snr_label.pack(side='right', padx=(10, 0))
        snr_scale.configure(command=self.update_snr_label)
        
        # Spreading settings with tooltip
        spread_frame = ttk.Frame(right_frame)
        spread_frame.pack(fill='x', pady=5)
        
        spread_label_frame = ttk.Frame(spread_frame)
        spread_label_frame.pack(fill='x')
        
        ttk.Label(spread_label_frame, text="Spreading Exponent:", style='Heading.TLabel').pack(side='left')
        spread_info = ttk.Label(spread_label_frame, text=" ⓘ", style='Info.TLabel', foreground='#89b4fa')
        spread_info.pack(side='left')
        ToolTip(spread_info, tooltips['spreading'])
        
        spread_controls = ttk.Frame(spread_frame)
        spread_controls.pack(fill='x')
        
        self.spread_var = tk.DoubleVar(value=1.5)
        spread_scale = ttk.Scale(spread_controls, from_=1.0, to=2.0, variable=self.spread_var, orient='horizontal')
        spread_scale.pack(side='left', fill='x', expand=True)
        self.spread_label = ttk.Label(spread_controls, text="1.5", style='Info.TLabel', width=10)
        self.spread_label.pack(side='right', padx=(10, 0))
        spread_scale.configure(command=self.update_spread_label)
        
        # Anomaly settings with tooltip
        anomaly_frame = ttk.Frame(right_frame)
        anomaly_frame.pack(fill='x', pady=5)
        
        anomaly_label_frame = ttk.Frame(anomaly_frame)
        anomaly_label_frame.pack(fill='x')
        
        ttk.Label(anomaly_label_frame, text="Site Anomaly (dB):", style='Heading.TLabel').pack(side='left')
        anomaly_info = ttk.Label(anomaly_label_frame, text=" ⓘ", style='Info.TLabel', foreground='#89b4fa')
        anomaly_info.pack(side='left')
        ToolTip(anomaly_info, tooltips['anomaly'])
        
        anomaly_controls = ttk.Frame(anomaly_frame)
        anomaly_controls.pack(fill='x')
        
        self.anomaly_var = tk.DoubleVar(value=0.0)
        anomaly_scale = ttk.Scale(anomaly_controls, from_=-10, to=10, variable=self.anomaly_var, orient='horizontal')
        anomaly_scale.pack(side='left', fill='x', expand=True)
        self.anomaly_label = ttk.Label(anomaly_controls, text="0.0 dB", style='Info.TLabel', width=10)
        self.anomaly_label.pack(side='right', padx=(10, 0))
        anomaly_scale.configure(command=self.update_anomaly_label)
        
        # Apply button
        ttk.Button(parent, text="📝 Apply Custom Configuration", 
                  command=self.apply_custom_config, style='Custom.TButton').pack(pady=10)
    
    def apply_custom_config(self):
        """Apply custom configuration"""
        try:
            self.current_config = AcousticPhysicsConfig(
                transmission_power_db=self.power_var.get(),
                frequency_hz=self.freq_var.get() * 1000,
                noise_level_db=self.noise_var.get(),
                required_snr_db=self.snr_var.get(),
                spreading_exponent=self.spread_var.get(),
                site_anomaly_db=self.anomaly_var.get()
            )
            
            display_text = f"""Current Configuration: CUSTOM
Transmission Power: {self.current_config.transmission_power_db} dB re 1 μPa
Frequency: {self.current_config.frequency_hz/1000:.1f} kHz
Noise Level: {self.current_config.noise_level_db} dB re 1 μPa
Required SNR: {self.current_config.required_snr_db} dB
Spreading Exponent: {self.current_config.spreading_exponent}
Site Anomaly: {self.current_config.site_anomaly_db:+.1f} dB"""
            
            self.config_display.delete(1.0, tk.END)
            self.config_display.insert(1.0, display_text)
            
            messagebox.showinfo("Configuration Applied", "Custom configuration has been applied successfully!")
            
        except Exception as e:
            messagebox.showerror("Configuration Error", f"Error applying configuration: {str(e)}")

    def create_simulation_tab(self):
        """Create tactical simulation control interface"""
        sim_frame = tk.Frame(self.notebook, bg='#0a0a0a')
        self.notebook.add(sim_frame, text="TACTICAL CONTROL")
        
        # Mission parameters control panel
        params_control_frame = tk.Frame(sim_frame, bg='#1a1a1a', relief='solid', borderwidth=3)
        params_control_frame.pack(fill='x', padx=5, pady=5)
        
        params_control_header = tk.Label(params_control_frame,
                                       text="SIMULATION PARAMETERS",
                                       font=('Consolas', 12, 'bold'),
                                       fg='#00ff41', bg='#1a1a1a')
        params_control_header.pack(pady=5)
        
        # Parameters control grid
        control_grid = tk.Frame(params_control_frame, bg='#1a1a1a')
        control_grid.pack(padx=10, pady=10)
        
        # Iteration count control
        iter_frame = tk.Frame(control_grid, bg='#1a1a1a')
        iter_frame.pack(fill='x', pady=5)
        
        iter_label = tk.Label(iter_frame,
                            text="Mission Duration (Iterations):",
                            font=('Consolas', 10, 'bold'),
                            fg='#e0e0e0', bg='#1a1a1a')
        iter_label.pack(side='left')
        
        self.ticks_entry = tk.Entry(iter_frame,
                                  textvariable=self.ticks_var,
                                  font=('Consolas', 10),
                                  bg='#2d2d2d', fg='#00ff41',
                                  relief='solid', borderwidth=2,
                                  width=10)
        self.ticks_entry.pack(side='right', padx=(10, 0))
        
        # World size control
        world_frame = tk.Frame(control_grid, bg='#1a1a1a')
        world_frame.pack(fill='x', pady=5)
        
        world_label = tk.Label(world_frame,
                             text="World Size (meters):",
                             font=('Consolas', 10, 'bold'),
                             fg='#e0e0e0', bg='#1a1a1a')
        world_label.pack(side='left')
        
        self.world_entry = tk.Entry(world_frame,
                                  textvariable=self.world_size_var,
                                  font=('Consolas', 10),
                                  bg='#2d2d2d', fg='#00ff41',
                                  relief='solid', borderwidth=2,
                                  width=10)
        self.world_entry.pack(side='right', padx=(10, 0))
        
        # Mission launch panel
        launch_frame = tk.Frame(sim_frame, bg='#1a1a1a', relief='solid', borderwidth=3)
        launch_frame.pack(fill='x', padx=5, pady=5)
        
        launch_header = tk.Label(launch_frame,
                               text="MISSION LAUNCH CONTROL",
                               font=('Consolas', 14, 'bold'),
                               fg='#00ff41', bg='#1a1a1a')
        launch_header.pack(pady=8)
        
        # Control buttons with military styling
        control_frame = tk.Frame(launch_frame, bg='#1a1a1a')
        control_frame.pack(pady=15)
        
        # Launch button - Critical red styling
        self.launch_btn = tk.Button(control_frame,
                                   text="AUTHORIZE MISSION LAUNCH",
                                   command=self.start_simulation,
                                   font=('Consolas', 12, 'bold'),
                                   fg='#000000', bg='#ff0030',
                                   relief='raised', borderwidth=4,
                                   padx=20, pady=8)
        self.launch_btn.pack(side='left', padx=15)
        
        # Make launch_btn also accessible as start_btn for compatibility
        self.start_btn = self.launch_btn
        
        # Stop button - Emergency styling
        self.stop_btn = tk.Button(control_frame,
                                text="EMERGENCY ABORT",
                                command=self.stop_simulation,
                                font=('Consolas', 12, 'bold'),
                                fg='#ffffff', bg='#cc0020',
                                relief='raised', borderwidth=4,
                                padx=20, pady=8,
                                state='disabled')
        self.stop_btn.pack(side='left', padx=15)
        
        # Mission parameters display
        params_frame = tk.Frame(sim_frame, bg='#1a1a1a', relief='solid', borderwidth=3)
        params_frame.pack(fill='x', padx=5, pady=5)
        
        params_header = tk.Label(params_frame,
                               text="CURRENT MISSION PARAMETERS",
                               font=('Consolas', 12, 'bold'),
                               fg='#00ff41', bg='#1a1a1a')
        params_header.pack(pady=5)
        
        self.mission_params_text = tk.Text(params_frame,
                                         height=8,
                                         bg='#2d2d2d', fg='#e0e0e0',
                                         font=('Consolas', 9),
                                         relief='sunken', borderwidth=2)
        self.mission_params_text.pack(fill='x', padx=10, pady=10)
        
        # Progress panel
        progress_frame = tk.Frame(sim_frame, bg='#1a1a1a', relief='solid', borderwidth=3)
        progress_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        progress_header = tk.Label(progress_frame,
                                 text="MISSION PROGRESS MONITOR",
                                 font=('Consolas', 12, 'bold'),
                                 fg='#00ff41', bg='#1a1a1a')
        progress_header.pack(pady=5)
        
        self.progress_text = tk.Text(progress_frame,
                                   bg='#000000', fg='#00ff41',
                                   font=('Consolas', 9),
                                   relief='sunken', borderwidth=2)
        progress_scroll = tk.Scrollbar(progress_frame, orient='vertical', command=self.progress_text.yview)
        self.progress_text.configure(yscrollcommand=progress_scroll.set)
        
        self.progress_text.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        progress_scroll.pack(side='right', fill='y', pady=5)
        
        # Update mission parameters display on tab creation
        self.update_mission_params_display()

    def update_mission_params_display(self):
        """Update the mission parameters display with current configuration"""
        config_name = self.get_current_config_name()
        config = self.current_config
        
        params_text = f"""MISSION CONFIGURATION: {config_name.upper()}
        
ACOUSTIC PARAMETERS:
• Transmission Power: {config.transmission_power_db} dB re 1 μPa
• Operating Frequency: {config.frequency_hz/1000:.1f} kHz  
• Ambient Noise Level: {config.noise_level_db} dB
• Required SNR: {config.required_snr_db} dB
• Propagation Model: {config.spreading_exponent} spreading
• Site Anomaly: {config.site_anomaly_db} dB

EXPERIMENTAL PARAMETERS:
• Max Safe Distance: {getattr(self, 'safe_distance_var', tk.DoubleVar(value=2000)).get():.0f} meters
• World Dimensions: {getattr(self, 'exp_world_size_var', tk.DoubleVar(value=1000)).get():.0f} meters
• Detection Range: {getattr(self, 'detection_range_var', tk.DoubleVar(value=50)).get():.0f} meters
• Vehicle Speed: {getattr(self, 'sub_speed_var', tk.DoubleVar(value=5)).get():.1f} m/tick
• Turn Rate: {getattr(self, 'turn_rate_var', tk.DoubleVar(value=10)).get():.1f}°/tick
• Depth Rate: {getattr(self, 'depth_rate_var', tk.DoubleVar(value=2)).get():.1f} m/tick

MISSION READY FOR AUTHORIZATION"""
        
        self.mission_params_text.delete(1.0, tk.END)
        self.mission_params_text.insert(1.0, params_text)

    def create_monitor_tab(self):
        """Create military-grade mission control dashboard"""
        monitor_frame = tk.Frame(self.notebook, bg='#0a0a0a')
        self.notebook.add(monitor_frame, text="TACTICAL DISPLAY")
        
        # Mission Control Header
        header_frame = tk.Frame(monitor_frame, bg='#1a1a1a', relief='solid', borderwidth=3)
        header_frame.pack(fill='x', padx=5, pady=5)
        
        mission_header = tk.Label(header_frame,
                                text="MISSION CONTROL DASHBOARD",
                                font=('Consolas', 16, 'bold'),
                                fg='#00ff41', bg='#1a1a1a')
        mission_header.pack(pady=8)
        
        # Classification banner
        classification = tk.Label(header_frame,
                                text="REAL-TIME TACTICAL INTELLIGENCE FEED",
                                font=('Consolas', 10, 'bold'),
                                fg='#ffb000', bg='#1a1a1a')
        classification.pack()
        
        # Main dashboard layout
        dashboard_frame = tk.Frame(monitor_frame, bg='#0a0a0a')
        dashboard_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left panel - Live Statistics
        left_panel = tk.Frame(dashboard_frame, bg='#1a1a1a', relief='solid', borderwidth=3)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 3))
        
        stats_header = tk.Label(left_panel,
                              text="LIVE TELEMETRY DATA",
                              font=('Consolas', 12, 'bold'),
                              fg='#00ff41', bg='#1a1a1a')
        stats_header.pack(pady=5)
        
        # Statistics grid
        stats_grid = tk.Frame(left_panel, bg='#1a1a1a')
        stats_grid.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Initialize stats labels dictionary
        self.stats_labels = {}
        
        # Create stats display
        stats_data = [
            ("Mission Tick:", "mission_tick", "0"),
            ("Success Rate:", "success_rate", "0.0%"),
            ("Distance:", "distance", "0.0m"),
            ("Objects Detected:", "objects_detected", "0"),
            ("Commands Sent:", "commands_sent", "0"),
            ("Status Received:", "status_received", "0"),
            ("Comm Range:", "comm_range", "0.0m"),
            ("Current Depth:", "current_depth", "0.0m"),
            ("Heading:", "heading", "0.0°"),
            ("Lost Packets:", "lost_packets", "0"),
            ("Signal Strength:", "signal_strength", "0%"),
            ("Mission Progress:", "mission_progress", "0.0%")
        ]
        
        for i, (label_text, key, default_value) in enumerate(stats_data):
            row = i // 2
            col = i % 2
            
            # Create stat frame
            stat_frame = tk.Frame(stats_grid, bg='#2d2d2d', relief='raised', borderwidth=2)
            stat_frame.grid(row=row, column=col, sticky='ew', padx=3, pady=3)
            
            # Label
            label = tk.Label(stat_frame,
                           text=label_text,
                           font=('Consolas', 9, 'bold'),
                           fg='#e0e0e0', bg='#2d2d2d')
            label.pack(anchor='w', padx=5, pady=2)
            
            # Value
            value_label = tk.Label(stat_frame,
                                 text=default_value,
                                 font=('Consolas', 11, 'bold'),
                                 fg='#00ff41', bg='#2d2d2d')
            value_label.pack(anchor='w', padx=5, pady=2)
            
            self.stats_labels[key] = value_label
        
        # Configure grid weights
        for i in range(6):  # 6 rows
            stats_grid.grid_rowconfigure(i, weight=1)
        stats_grid.grid_columnconfigure(0, weight=1)
        stats_grid.grid_columnconfigure(1, weight=1)
        
        # Right panel - Mission Console
        right_panel = tk.Frame(dashboard_frame, bg='#1a1a1a', relief='solid', borderwidth=3)
        right_panel.pack(side='right', fill='both', expand=True, padx=(3, 0))
        
        console_header = tk.Label(right_panel,
                                text="MISSION CONSOLE LOG",
                                font=('Consolas', 12, 'bold'),
                                fg='#00ff41', bg='#1a1a1a')
        console_header.pack(pady=5)
        
        # Mission status indicator
        status_frame = tk.Frame(right_panel, bg='#1a1a1a')
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.mission_status_label = tk.Label(status_frame,
                                           text="MISSION STANDBY",
                                           font=('Consolas', 11, 'bold'),
                                           fg='#ff0030', bg='#1a1a1a')
        self.mission_status_label.pack()
        
        # Console text area
        console_container = tk.Frame(right_panel, bg='#1a1a1a')
        console_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.console_text = tk.Text(console_container,
                                   bg='#000000', fg='#00ff41',
                                   font=('Consolas', 9),
                                   wrap='word',
                                   relief='sunken', borderwidth=2)
        console_scroll = tk.Scrollbar(console_container, orient='vertical', command=self.console_text.yview)
        self.console_text.configure(yscrollcommand=console_scroll.set)
        
        self.console_text.pack(side='left', fill='both', expand=True)
        console_scroll.pack(side='right', fill='y')
        
        # Initial console message
        self.log_sci_fi_message("TACTICAL DISPLAY SYSTEM ONLINE", "SYSTEM")
        self.log_sci_fi_message("AWAITING MISSION AUTHORIZATION", "INFO")

    def create_results_tab(self):
        """Create military intelligence report interface"""
        results_frame = tk.Frame(self.notebook, bg='#0a0a0a')
        self.notebook.add(results_frame, text="INTELLIGENCE")
        
        # Intelligence report panel
        intel_frame = tk.Frame(results_frame, bg='#1a1a1a', relief='solid', borderwidth=3)
        intel_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Intelligence header
        intel_header = tk.Label(intel_frame,
                              text="MISSION INTELLIGENCE REPORT",
                              font=('Consolas', 14, 'bold'),
                              fg='#00ff41', bg='#1a1a1a')
        intel_header.pack(pady=8)
        
        # Report text area
        report_container = tk.Frame(intel_frame, bg='#1a1a1a')
        report_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.results_text = tk.Text(report_container,
                                   bg='#2d2d2d', fg='#e0e0e0',
                                   font=('Consolas', 9),
                                   wrap='word',
                                   relief='sunken', borderwidth=2)
        results_scroll = tk.Scrollbar(report_container, orient='vertical', command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=results_scroll.set)
        
        self.results_text.pack(side='left', fill='both', expand=True)
        results_scroll.pack(side='right', fill='y')
        
        # Data export operations
        export_frame = tk.Frame(results_frame, bg='#1a1a1a', relief='solid', borderwidth=3)
        export_frame.pack(fill='x', padx=5, pady=5)
        
        export_header = tk.Label(export_frame,
                               text="DATA EXPORT OPERATIONS",
                               font=('Consolas', 11, 'bold'),
                               fg='#00ff41', bg='#1a1a1a')
        export_header.pack(pady=3)
        
        export_buttons = tk.Frame(export_frame, bg='#1a1a1a')
        export_buttons.pack(pady=8)
        
        # Export buttons with military styling
        csv_btn = tk.Button(export_buttons,
                          text="EXPORT MISSION DATA",
                          command=self.export_csv,
                          font=('Consolas', 10, 'bold'),
                          fg='#e0e0e0', bg='#2d2d2d',
                          relief='raised', borderwidth=3,
                          padx=12, pady=5)
        csv_btn.pack(side='left', padx=8)
        
        report_btn = tk.Button(export_buttons,
                             text="EXPORT INTEL REPORT",
                             command=self.export_report,
                             font=('Consolas', 10, 'bold'),
                             fg='#e0e0e0', bg='#2d2d2d',
                             relief='raised', borderwidth=3,
                             padx=12, pady=5)
        report_btn.pack(side='left', padx=8)
        
        charts_btn = tk.Button(export_buttons,
                             text="TACTICAL ANALYSIS",
                             command=self.show_charts,
                             font=('Consolas', 10, 'bold'),
                             fg='#e0e0e0', bg='#2d2d2d',
                             relief='raised', borderwidth=3,
                             padx=12, pady=5)
        charts_btn.pack(side='left', padx=8)

    def log_sci_fi_message(self, message, level="INFO"):
        """Add sci-fi styled message to console"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # Include milliseconds
        
        # Color coding for different levels - REMOVED ICONS
        if level == "ERROR":
            prefix = "[ERROR]"
            color_tag = "error"
        elif level == "WARNING":
            prefix = "[WARN] "
            color_tag = "warning"
        elif level == "SUCCESS":
            prefix = "[SUCC] "
            color_tag = "success"
        elif level == "SYSTEM":
            prefix = "[SYS]  "
            color_tag = "system"
        elif level == "COMM":
            prefix = "[COMM] "
            color_tag = "comm"
        elif level == "DETECT":
            prefix = "[DETECT]"
            color_tag = "detect"
        else:
            prefix = "[INFO] "
            color_tag = "info"
        
        full_message = f"[T+{timestamp}] {prefix} {message}\n"
        
        # Configure color tags if not already done
        self.console_text.tag_configure("error", foreground="#ff6b6b")
        self.console_text.tag_configure("warning", foreground="#ffd93d")
        self.console_text.tag_configure("success", foreground="#6bcf7f")
        self.console_text.tag_configure("system", foreground="#74c0fc")
        self.console_text.tag_configure("comm", foreground="#da77f2")
        self.console_text.tag_configure("detect", foreground="#ff922b")
        self.console_text.tag_configure("info", foreground="#00ff00")
        
        self.console_text.insert(tk.END, full_message, color_tag)
        self.console_text.see(tk.END)
        self.root.update_idletasks()

    def update_mission_stats(self, stats_update):
        """Update real-time mission statistics"""
        try:
            if "tick" in stats_update:
                self.stats_labels["mission_tick"].config(text=f"{stats_update['tick']:,}")
            
            if "success_rate" in stats_update:
                rate = stats_update['success_rate']
                color = '#a6e3a1' if rate > 0.8 else '#ffd93d' if rate > 0.5 else '#f38ba8'
                self.stats_labels["success_rate"].config(text=f"{rate:.2%}", foreground=color)
            
            if "distance" in stats_update:
                self.stats_labels["distance"].config(text=f"{stats_update['distance']:.1f}m")
            
            if "objects_detected" in stats_update:
                self.stats_labels["objects_detected"].config(text=str(stats_update['objects_detected']))
            
            if "commands_sent" in stats_update:
                self.stats_labels["commands_sent"].config(text=str(stats_update['commands_sent']))
            
            if "status_received" in stats_update:
                self.stats_labels["status_received"].config(text=str(stats_update['status_received']))
            
            if "comm_range" in stats_update:
                self.stats_labels["comm_range"].config(text=f"{stats_update['comm_range']:.1f}m")
            
            if "depth" in stats_update:
                self.stats_labels["current_depth"].config(text=f"{stats_update['depth']:.1f}m")
            
            if "heading" in stats_update:
                self.stats_labels["heading"].config(text=f"{stats_update['heading']:.1f}°")
            
            if "lost_packets" in stats_update:
                lost = stats_update['lost_packets']
                color = '#a6e3a1' if lost == 0 else '#ffd93d' if lost < 10 else '#f38ba8'
                self.stats_labels["lost_packets"].config(text=str(lost), foreground=color)
            
            if "signal_strength" in stats_update:
                strength = stats_update['signal_strength']
                color = '#a6e3a1' if strength > 0.8 else '#ffd93d' if strength > 0.5 else '#f38ba8'
                self.stats_labels["signal_strength"].config(text=f"{strength:.0%}", foreground=color)
            
            if "progress" in stats_update:
                progress = stats_update['progress']
                self.stats_labels["mission_progress"].config(text=f"{progress:.2%}")
                
                # Update mission status
                if progress < 0.1:
                    status = "🟡 MISSION INITIALIZING"
                    color = '#ffd93d'
                elif progress < 0.9:
                    status = "🟢 MISSION ACTIVE"
                    color = '#a6e3a1'
                else:
                    status = "🔵 MISSION COMPLETING"
                    color = '#89b4fa'
                
                self.mission_status_label.config(text=status, foreground=color)
                
        except Exception as e:
            pass  # Silently handle missing labels

    def run_simulation_thread(self):
        """Run simulation in background thread with live updates"""
        try:
            if self.sim_type_var.get() == "comparison":
                self.log_sci_fi_message("INITIATING MULTI-CONFIGURATION ANALYSIS PROTOCOL", "SYSTEM")
                results = run_configuration_comparison()
                self.simulation_queue.put(("comparison_complete", results))
            else:
                self.log_sci_fi_message("DEPLOYING UUV TO MISSION AREA", "SYSTEM")
                self.log_sci_fi_message(f"MISSION PARAMETERS: {self.ticks_var.get():,} TICKS, {self.world_size_var.get():.0f}M WORLD", "INFO")
                
                # Create a custom simulation function with progress updates
                controller, report = self.run_simulation_with_updates()
                self.simulation_queue.put(("simulation_complete", (controller, report)))
                
        except Exception as e:
            self.log_sci_fi_message(f"CRITICAL SYSTEM ERROR: {str(e)}", "ERROR")
            self.simulation_queue.put(("error", str(e)))

    def run_simulation_with_updates(self):
        """Run simulation with real-time progress updates - OPTIMIZED FOR HIGH TICK COUNTS"""
        from models.simulation_controller import SimulationController
        import gc  # Garbage collection for memory management
        
        # Get experimental parameters if they exist
        exp_params = getattr(self, 'experimental_params', {})
        
        # Initialize simulation with experimental world size if available
        world_size = exp_params.get('world_size', self.world_size_var.get())
        controller = SimulationController(world_size=world_size)
        
        # Apply experimental parameters to the submarine and game state
        if exp_params:
            self.log_sci_fi_message("APPLYING EXPERIMENTAL PARAMETERS", "SYSTEM")
            
            # Update submarine parameters
            submarine = controller.game_state.submarine
            submarine.max_safe_distance_from_ship = exp_params.get('max_safe_distance', 2000.0)
            submarine.detection_range = exp_params.get('detection_range', 50.0)
            submarine.speed = exp_params.get('submarine_speed', 5.0)
            submarine.turn_rate = exp_params.get('turn_rate', 10.0)
            submarine.ascent_descent_rate = exp_params.get('depth_rate', 2.0)
            
            # APPLY NEW MOVEMENT PARAMETERS
            max_range = exp_params.get('max_range', 15000.0)
            movement_pattern = exp_params.get('movement_pattern', 0.7)
            
            # Set submarine's maximum operational range
            submarine.max_operational_range = max_range
            submarine.movement_aggressiveness = movement_pattern
            
            self.log_sci_fi_message(f"   Max Safe Distance: {submarine.max_safe_distance_from_ship:.0f}m", "ⓘ")
            self.log_sci_fi_message(f"   Detection Range: {submarine.detection_range:.0f}m", "ⓘ")
            self.log_sci_fi_message(f"   Submarine Speed: {submarine.speed:.1f} m/tick", "ⓘ")
            self.log_sci_fi_message(f"   Turn Rate: {submarine.turn_rate:.1f}°/tick", "ⓘ")
            self.log_sci_fi_message(f"   Depth Rate: {submarine.ascent_descent_rate:.1f} m/tick", "ⓘ")
            self.log_sci_fi_message(f"   Max Operational Range: {max_range:.0f}m", "ⓘ")
            self.log_sci_fi_message(f"   Movement Aggressiveness: {movement_pattern:.2f}", "ⓘ")
        
        if self.current_config is not None:
            controller.communication_model.update_physics_config(self.current_config)
            self.log_sci_fi_message("ACOUSTIC PHYSICS CONFIGURATION APPLIED", "SYSTEM")
        
        total_ticks = self.ticks_var.get()
        
        # OPTIMIZATION: Dynamic update interval based on tick count
        if total_ticks > 100000:  # High performance mode for 100k+ ticks
            update_interval = max(100, total_ticks // 500)  # Update every 0.2% for high tick counts
            log_interval = max(1000, total_ticks // 100)    # Less frequent logging
            gc_interval = 10000  # Garbage collection every 10k ticks
            self.log_sci_fi_message("HIGH-PERFORMANCE MODE ACTIVATED FOR LARGE SIMULATION", "SYSTEM")
        else:
            update_interval = max(1, total_ticks // 100)     # Update every 1% for normal simulations  
            log_interval = max(10, total_ticks // 50)        # Standard logging
            gc_interval = 5000   # GC every 5k ticks
        
        # Log initial state
        sub_pos = controller.game_state.submarine.position
        self.log_sci_fi_message(f"UUV DEPLOYED AT COORDINATES ({sub_pos.x:.1f}, {sub_pos.y:.1f}, {sub_pos.z:.1f})", "ⓘ")
        self.log_sci_fi_message(f"TARGET: {len(controller.game_state.objects)} OBJECTS FOR DETECTION", "ⓘ")
        self.log_sci_fi_message("COMMUNICATION LINK ESTABLISHED", "COMM")
        
        # Performance tracking
        commands_sent = 0
        status_received = 0
        lost_packets = 0
        last_gc_tick = 0
        
        # OPTIMIZATION: Batch event processing for large simulations
        event_batch = []
        batch_size = 1000 if total_ticks > 100000 else 100
        
        for tick in range(total_ticks):
            try:
                # Run one simulation tick (this handles commands, communication, movement, detection)
                tick_events = controller.simulate_tick()
                
                # OPTIMIZATION: Batch process events instead of processing individually
                event_batch.extend(tick_events)
                
                # Process batch when full or at update intervals
                if len(event_batch) >= batch_size or tick % update_interval == 0:
                    # Count communication events in batch
                    for event in event_batch:
                        if event.event_type == "command":
                            commands_sent += 1
                            if not event.success:
                                lost_packets += 1
                        elif event.event_type == "status" and event.success:
                            status_received += 1
                    
                    # Clear batch after processing
                    event_batch = []
                
                # OPTIMIZATION: Memory management for high tick counts
                if tick - last_gc_tick >= gc_interval:
                    gc.collect()  # Force garbage collection
                    last_gc_tick = tick
                
                # Send progress updates at optimized intervals
                if tick % update_interval == 0 or tick == total_ticks - 1:
                    progress = tick / total_ticks
                    
                    # OPTIMIZATION: Efficient statistics calculation
                    try:
                        success_events = len([e for e in controller.events[-1000:] if e.success])  # Only check last 1000 events
                        total_events = min(len(controller.events), 1000) or 1
                        success_rate = success_events / total_events
                    except:
                        success_rate = 0.5  # Fallback
                    
                    objects_detected = len([obj for obj in controller.game_state.objects if obj.detected])
                    
                    current_pos = controller.game_state.submarine.position
                    distance_from_start = ((current_pos.x**2 + current_pos.y**2 + current_pos.z**2)**0.5)
                    
                    # Communication range estimation
                    comm_range = getattr(controller.communication_model, 'max_reliable_range', 1000)
                    
                    # Signal strength based on distance and success rate
                    signal_strength = min(1.0, success_rate * (1 - distance_from_start / comm_range) if comm_range > 0 else success_rate)
                    
                    stats_update = {
                        'tick': tick,
                        'progress': progress,
                        'success_rate': success_rate,
                        'distance': distance_from_start,
                        'objects_detected': objects_detected,
                        'commands_sent': commands_sent,
                        'status_received': status_received,
                        'comm_range': comm_range,
                        'depth': current_pos.z,
                        'heading': controller.game_state.submarine.heading,
                        'lost_packets': lost_packets,
                        'signal_strength': signal_strength
                    }
                    
                    self.simulation_queue.put(("stats_update", stats_update))
                    
                    # OPTIMIZATION: Less frequent logging for high tick counts
                    if tick % log_interval == 0:
                        self.simulation_queue.put(("log_message", f"MISSION PROGRESS: {progress:.1%} - DEPTH: {current_pos.z:.1f}M", "INFO"))
                        
                    # OPTIMIZATION: Only log significant detections for high tick counts
                    if total_ticks <= 100000:  # Normal logging for smaller simulations
                        detection_events = [e for e in tick_events if e.event_type == "detection"]
                        for det_event in detection_events:
                            obj_type = det_event.data.get('object_type', 'UNKNOWN')
                            obj_id = det_event.data.get('object_id', 'XX')
                            distance = det_event.data.get('distance', 0)
                            self.simulation_queue.put(("log_message", f"OBJECT DETECTED: {obj_type.upper()} #{obj_id} AT {distance:.1f}M", "DETECT"))
                    
                    # Log communication issues less frequently for high tick counts
                    comm_failures = [e for e in tick_events if not e.success and e.event_type in ["command", "status"]]
                    if comm_failures and tick % (log_interval * 2) == 0:
                        self.simulation_queue.put(("log_message", f"COMMUNICATION DEGRADED: {len(comm_failures)} LOST PACKETS", "WARNING"))
                
            except Exception as e:
                self.simulation_queue.put(("log_message", f"SIMULATION ERROR AT TICK {tick}: {str(e)}", "ERROR"))
                break
        
        # Final cleanup
        gc.collect()
        
        # Generate final report
        self.log_sci_fi_message("GENERATING MISSION ANALYSIS REPORT", "SYSTEM")
        final_report = controller._generate_final_report()
        
        return controller, final_report

    def monitor_simulation(self):
        """Monitor simulation progress with live updates"""
        try:
            message_count = 0
            while message_count < 50:  # Process up to 50 messages per update
                try:
                    message_data = self.simulation_queue.get_nowait()
                    message_count += 1
                    
                    # Handle different message formats
                    if len(message_data) == 2:
                        message_type, data = message_data
                    elif len(message_data) == 3:
                        message_type, data1, data2 = message_data
                        if message_type == "log_message":
                            # For log messages: (type, message, level)
                            data = (data1, data2)
                        else:
                            data = data1
                    else:
                        continue  # Skip malformed messages
                    
                    if message_type == "simulation_complete":
                        controller, report = data
                        self.simulation_controller = controller
                        self.simulation_results = report
                        self.simulation_complete((controller, report))
                        return
                    elif message_type == "comparison_complete":
                        self.comparison_complete(data)
                        return
                    elif message_type == "error":
                        self.simulation_error(data)
                        return
                    elif message_type == "stats_update":
                        self.update_mission_stats(data)
                    elif message_type == "log_message":
                        if isinstance(data, tuple) and len(data) == 2:
                            message, level = data
                        else:
                            message, level = str(data), "INFO"
                        self.log_sci_fi_message(message, level)
                        
                except queue.Empty:
                    break
                    
        except queue.Empty:
            pass
            
        # Continue monitoring
        self.root.after(50, self.monitor_simulation)  # Faster updates for better responsiveness

    def export_csv(self):
        """Export all CSV files to a selected folder - OPTIMIZED VERSION WITH CRASH PROTECTION"""
        if not self.simulation_results:
            messagebox.showwarning("No Results", "No simulation results to export!")
            return
            
        # Ask user to select a directory
        export_dir = filedialog.askdirectory(title="Select folder to export simulation data")
        
        if not export_dir:
            return
            
        try:
            # Create a timestamped subfolder
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            config_name = self._last_config_name
            folder_name = f"uuv_simulation_{config_name}_{timestamp}"
            full_export_path = os.path.join(export_dir, folder_name)
            
            # Create the folder
            os.makedirs(full_export_path, exist_ok=True)
            
            self.log_sci_fi_message(f"CREATING EXPORT DIRECTORY: {folder_name}", "SYSTEM")
            
            # OPTIMIZATION: Check simulation size and warn for large exports
            if self.simulation_controller:
                event_count = len(getattr(self.simulation_controller, 'events', []))
                if event_count > 100000:
                    self.log_sci_fi_message(f"WARNING: LARGE DATASET ({event_count:,} EVENTS) - EXPORT MAY TAKE TIME", "WARNING")
                    
                    # Ask user if they want to continue with large export
                    result = messagebox.askyesno("Large Dataset Warning", 
                                               f"This simulation has {event_count:,} events.\n\n"
                                               f"Export may take several minutes and use significant disk space.\n\n"
                                               f"Continue with export?")
                    if not result:
                        return
                
                self.log_sci_fi_message("EXPORTING COMPLETE DATASET ARCHIVES", "SYSTEM")
                
                # Use the controller's export methods directly with error handling
                base_name = f"uuv_simulation_{config_name}"
                
                try:
                    # Export standard simulation files with progress updates
                    standard_folder = os.path.join(full_export_path, "standard_simulation")
                    os.makedirs(standard_folder, exist_ok=True)
                    
                    self.log_sci_fi_message("EXPORTING STANDARD SIMULATION DATA", "INFO")
                    
                    from models.csv_logger import CSVLogger
                    logger = CSVLogger(base_name)
                    
                    # Export with individual error handling
                    try:
                        logger.export_simulation_log(self.simulation_controller, 
                                                   os.path.join(standard_folder, f"{base_name}_log.csv"))
                        self.log_sci_fi_message("✓ SIMULATION LOG EXPORTED", "SUCCESS")
                    except Exception as e:
                        self.log_sci_fi_message(f"⚠ LOG EXPORT FAILED: {str(e)}", "WARNING")
                    
                    try:
                        logger.export_objects_summary(self.simulation_controller, 
                                                     os.path.join(standard_folder, f"{base_name}_objects.csv"))
                        self.log_sci_fi_message("✓ OBJECTS SUMMARY EXPORTED", "SUCCESS")
                    except Exception as e:
                        self.log_sci_fi_message(f"⚠ OBJECTS EXPORT FAILED: {str(e)}", "WARNING")
                    
                    try:
                        logger.export_detection_timeline(self.simulation_controller, 
                                                       os.path.join(standard_folder, f"{base_name}_detections.csv"))
                        self.log_sci_fi_message("✓ DETECTION TIMELINE EXPORTED", "SUCCESS")
                    except Exception as e:
                        self.log_sci_fi_message(f"⚠ DETECTIONS EXPORT FAILED: {str(e)}", "WARNING")
                    
                    try:
                        logger.export_communication_stats(self.simulation_controller, 
                                                         os.path.join(standard_folder, f"{base_name}_communication.csv"))
                        self.log_sci_fi_message("✓ COMMUNICATION STATS EXPORTED", "SUCCESS")
                    except Exception as e:
                        self.log_sci_fi_message(f"⚠ COMMUNICATION EXPORT FAILED: {str(e)}", "WARNING")
                    
                except Exception as e:
                    self.log_sci_fi_message(f"STANDARD EXPORT ERROR: {str(e)}", "ERROR")
                
                try:
                    # Export ML training data with error handling
                    ml_folder = os.path.join(full_export_path, "ml_training_data")
                    os.makedirs(ml_folder, exist_ok=True)
                    
                    self.log_sci_fi_message("EXPORTING ML TRAINING DATASETS", "INFO")
                    
                    from models.ml_csv_logger import MLOptimizedCSVLogger
                    ml_logger = MLOptimizedCSVLogger(f"packet_prediction_{config_name}")
                    
                    try:
                        ml_logger.export_packet_prediction_data(self.simulation_controller,
                                                              os.path.join(ml_folder, f"packet_prediction_{config_name}.csv"))
                        self.log_sci_fi_message("✓ PACKET PREDICTION DATA EXPORTED", "SUCCESS")
                    except Exception as e:
                        self.log_sci_fi_message(f"⚠ PACKET PREDICTION EXPORT FAILED: {str(e)}", "WARNING")
                    
                    try:
                        ml_logger.export_sequence_data(self.simulation_controller,
                                                     os.path.join(ml_folder, f"packet_prediction_{config_name}_sequences.csv"))
                        self.log_sci_fi_message("✓ SEQUENCE DATA EXPORTED", "SUCCESS")
                    except Exception as e:
                        self.log_sci_fi_message(f"⚠ SEQUENCE EXPORT FAILED: {str(e)}", "WARNING")
                    
                    try:
                        ml_logger.export_quality_timeline(self.simulation_controller,
                                                         os.path.join(ml_folder, f"packet_prediction_{config_name}_quality_timeline.csv"))
                        self.log_sci_fi_message("✓ QUALITY TIMELINE EXPORTED", "SUCCESS")
                    except Exception as e:
                        self.log_sci_fi_message(f"⚠ QUALITY TIMELINE EXPORT FAILED: {str(e)}", "WARNING")
                    
                except Exception as e:
                    self.log_sci_fi_message(f"ML EXPORT ERROR: {str(e)}", "ERROR")
                
                self.log_sci_fi_message("CSV DATASETS EXPORT COMPLETED", "SUCCESS")
            
            # Export results summary as text (with error handling)
            try:
                report_file = os.path.join(full_export_path, "mission_report.txt")
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(self.results_text.get(1.0, tk.END))
                self.log_sci_fi_message("✓ MISSION REPORT EXPORTED", "SUCCESS")
            except Exception as e:
                self.log_sci_fi_message(f"⚠ REPORT EXPORT FAILED: {str(e)}", "WARNING")
            
            # Export results as JSON (with error handling)
            try:
                json_file = os.path.join(full_export_path, "simulation_results.json")
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(self.simulation_results, f, indent=2, default=str)
                self.log_sci_fi_message("✓ SIMULATION METADATA EXPORTED", "SUCCESS")
            except Exception as e:
                self.log_sci_fi_message(f"⚠ JSON EXPORT FAILED: {str(e)}", "WARNING")
            
            # Create a summary info file
            try:
                info_file = os.path.join(full_export_path, "export_info.txt")
                with open(info_file, 'w', encoding='utf-8') as f:
                    f.write(f"🌊 UUV Communication Simulation Export\n")
                    f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Configuration: {config_name}\n")
                    f.write(f"Ticks Simulated: {self.ticks_var.get():,}\n")
                    if hasattr(self, 'experimental_params'):
                        f.write(f"Max Range: {self.experimental_params.get('max_range', 'N/A')}\n")
                        f.write(f"Movement Pattern: {self.experimental_params.get('movement_pattern', 'N/A')}\n")
                    f.write(f"\n📁 Folder Contents:\n")
                    f.write(f"- mission_report.txt: Detailed mission report\n")
                    f.write(f"- simulation_results.json: Complete results data\n")
                    f.write(f"- standard_simulation/: Standard CSV exports\n")
                    f.write(f"- ml_training_data/: ML-optimized datasets\n")
                self.log_sci_fi_message("✓ EXPORT INFO CREATED", "SUCCESS")
            except Exception as e:
                self.log_sci_fi_message(f"⚠ INFO FILE FAILED: {str(e)}", "WARNING")
            
            self.log_sci_fi_message("EXPORT OPERATION COMPLETED", "SUCCESS")
            messagebox.showinfo("Export Complete", 
                              f"🎊 Mission data exported successfully!\n\n"
                              f"📁 Location: {full_export_path}\n\n"
                              f"📊 Export includes all available data with error recovery.")
            
            # Open the folder in file explorer (with error handling)
            try:
                import subprocess
                import platform
                if platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", full_export_path])
                elif platform.system() == "Windows":
                    subprocess.run(["explorer", full_export_path])
                elif platform.system() == "Linux":
                    subprocess.run(["xdg-open", full_export_path])
            except:
                pass  # Silently fail if can't open folder
            
        except Exception as e:
            error_msg = f"EXPORT SYSTEM FAILURE: {str(e)}"
            self.log_sci_fi_message(error_msg, "ERROR")
            messagebox.showerror("Export Error", f"Export failed:\n{error_msg}")
            
            # Try to create an error log
            try:
                if 'full_export_path' in locals():
                    error_file = os.path.join(full_export_path, "export_error.log")
                    with open(error_file, 'w') as f:
                        f.write(f"Export Error: {error_msg}\n")
                        f.write(f"Timestamp: {datetime.now()}\n")
            except:
                pass
    
    def export_report(self):
        """Export detailed report"""
        if not self.simulation_results:
            messagebox.showwarning("No Results", "No simulation results to export!")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            with open(filename, 'w') as f:
                f.write(self.results_text.get(1.0, tk.END))
            messagebox.showinfo("Export Complete", f"Report exported to {filename}")
    
    def show_charts(self):
        """Show visualization charts"""
        if not self.simulation_results:
            messagebox.showwarning("No Results", "No simulation results to visualize!")
            return
            
        # Create a new window for charts
        chart_window = tk.Toplevel(self.root)
        chart_window.title("📊 Simulation Charts")
        chart_window.geometry("800x600")
        
        # Here you would create matplotlib charts
        # For now, just show a placeholder
        ttk.Label(chart_window, text="📊 Charts coming soon!", 
                 style='Title.TLabel').pack(expand=True)
    
    def get_current_config_name(self):
        """Get name of current configuration"""
        if hasattr(self, 'config_var'):
            return self.config_var.get()
        return "custom"
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

    # Event handlers and utility methods
    
    def update_power_label(self, value):
        self.power_label.config(text=f"{float(value):.1f} dB")
        
    def update_freq_label(self, value):
        self.freq_label.config(text=f"{float(value):.1f} kHz")
        
    def update_noise_label(self, value):
        self.noise_label.config(text=f"{float(value):.1f} dB")
        
    def update_snr_label(self, value):
        self.snr_label.config(text=f"{float(value):.1f} dB")
        
    def update_spread_label(self, value):
        self.spread_label.config(text=f"{float(value):.2f}")
        
    def update_anomaly_label(self, value):
        self.anomaly_label.config(text=f"{float(value):.1f} dB")
    
    def quick_demo(self):
        """Run a quick demo"""
        self.ticks_var.set(1000)
        self.world_size_var.set(800)
        self.sim_type_var.set("single")
        self.notebook.select(2)  # Switch to simulation tab
        messagebox.showinfo("Quick Demo", "Demo parameters set! Click 'Start Simulation' to begin.")
    
    def log_message(self, message):
        """Add message to console - now uses sci-fi logging"""
        self.log_sci_fi_message(message, "INFO")
    
    def start_simulation(self):
        """Start simulation in a separate thread"""
        if self.simulation_thread and self.simulation_thread.is_alive():
            messagebox.showwarning("Simulation Running", "A simulation is already running!")
            return
            
        # Prepare simulation
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.progress_var.set(0)
        
        # Clear console and add startup messages
        self.console_text.delete(1.0, tk.END)
        self.log_sci_fi_message("🚀 MISSION INITIALIZATION SEQUENCE STARTED", "SYSTEM")
        self.log_sci_fi_message("📊 PREPARING SIMULATION ENVIRONMENT", "INFO")
        
        # Switch to monitor tab
        self.notebook.select(3)
        
        # Start simulation thread
        self.simulation_thread = threading.Thread(target=self.run_simulation_thread)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()
        
        # Start progress monitor
        self.monitor_simulation()
    
    def stop_simulation(self):
        """Stop running simulation"""
        self.log_sci_fi_message("🛑 MISSION ABORT SEQUENCE INITIATED", "WARNING")
        # Note: This is a basic implementation. For proper cancellation,
        # you'd need to modify the simulation code to check for stop signals
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
    
    def simulation_complete(self, report):
        """Handle simulation completion"""
        # report is now a tuple of (controller, actual_report)
        if isinstance(report, tuple):
            controller, actual_report = report
            self.simulation_controller = controller  # Store controller
            self.simulation_results = actual_report
            report_to_display = actual_report
        else:
            self.simulation_results = report
            report_to_display = report
            
        self.log_sci_fi_message("🎊 MISSION COMPLETED SUCCESSFULLY", "SUCCESS")
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.progress_var.set(100)
        
        # Store config name for export
        self._last_config_name = self.get_current_config_name()
        
        # Update results tab
        self.display_results(report_to_display)
        
        # Switch to results tab
        self.notebook.select(4)
        
        messagebox.showinfo("Mission Complete", "🎊 Mission completed successfully! Check the Results tab for detailed analysis.")
    
    def comparison_complete(self, results):
        """Handle comparison completion"""
        self.log_sci_fi_message("📊 CONFIGURATION COMPARISON ANALYSIS COMPLETED", "SUCCESS")
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.progress_var.set(100)
        
        # Display comparison results
        self.display_comparison_results(results)
        
        messagebox.showinfo("Comparison Complete", "Configuration comparison completed!")
    
    def simulation_error(self, error):
        """Handle simulation error"""
        self.log_sci_fi_message(f"CRITICAL MISSION FAILURE: {error}", "ERROR")
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.progress_var.set(0)
        
        messagebox.showerror("Mission Failed", f"Simulation failed: {error}")
    
    def display_results(self, report):
        """Display ultra-detailed simulation results like complex_simulation.py"""
        if not report:
            return
            
        sim_summary = report["simulation_summary"]
        comm_stats = report["communication_stats"]
        
        # Create comprehensive results text
        results_text = f"""🎯 MISSION REPORT - DETAILED ANALYSIS
════════════════════════════════════════════════════════════════

📊 MISSION RESULTS:
   Total Ticks: {sim_summary['total_ticks']:,}
   Distance Traveled: {sim_summary['total_distance_traveled']:.1f}m
   Objects Detected: {sim_summary['objects_detected']}/{sim_summary['total_objects']}
   Detection Rate: {sim_summary['detection_rate']:.1%}
   Max Distance from Ship: {sim_summary['max_distance_from_ship']:.1f}m

📍 FINAL POSITION:
   Position: ({sim_summary['final_position'][0]:.1f}, {sim_summary['final_position'][1]:.1f}, {sim_summary['final_position'][2]:.1f})
   Depth: {sim_summary['final_depth']:.1f}m
   Heading: {sim_summary['final_heading']:.1f}°

📡 COMMUNICATION PERFORMANCE DETAILED:
   Overall Success Rate: {comm_stats['overall_communication_success']:.1%}
   Command Success Rate: {comm_stats['command_success_rate']:.1%}
   Status Success Rate: {comm_stats['status_success_rate']:.1%}
   
   PACKET STATISTICS:
   Commands Sent/Received: {comm_stats['commands_sent']}/{comm_stats['commands_received']}
   Status Sent/Received: {comm_stats['status_sent']}/{comm_stats['status_received']}
   Total Communication Events: {comm_stats['total_communication_events']:,}
   
   TIMING ANALYSIS:
   Average Propagation Delay: {comm_stats['average_propagation_delay_ms']:.1f}ms
   Average Total Delay: {comm_stats['average_total_delay_ms']:.1f}ms
   Min Delay: {comm_stats.get('min_delay_ms', 0):.1f}ms
   Max Delay: {comm_stats.get('max_delay_ms', 0):.1f}ms

🔍 OBJECT DETECTION DETAILED:"""

        # Add detected objects details
        detected_objects = [obj for obj in report["objects"] if obj["detected"]]
        undetected_objects = [obj for obj in report["objects"] if not obj["detected"]]
        
        if detected_objects:
            results_text += f"\n   DETECTED OBJECTS ({len(detected_objects)}):"
            for obj in detected_objects:
                pos = obj["position"]
                distance = ((pos[0]**2 + pos[1]**2 + pos[2]**2)**0.5)
                results_text += f"\n     • {obj['type'].upper()} #{obj['id']} at ({pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f}) - Distance: {distance:.1f}m"
        
        if undetected_objects:
            results_text += f"\n\n   MISSED OBJECTS ({len(undetected_objects)}):"
            for i, obj in enumerate(undetected_objects):
                if i < 10:  # Show first 10
                    pos = obj["position"]
                    distance = ((pos[0]**2 + pos[1]**2 + pos[2]**2)**0.5)
                    results_text += f"\n     • {obj['type'].upper()} #{obj['id']} at ({pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f}) - Distance: {distance:.1f}m"
            if len(undetected_objects) > 10:
                results_text += f"\n     ... and {len(undetected_objects) - 10} more missed objects"

        # Add object type breakdown
        object_types = {}
        for obj in report["objects"]:
            obj_type = obj["type"]
            if obj_type not in object_types:
                object_types[obj_type] = {'total': 0, 'detected': 0}
            object_types[obj_type]['total'] += 1
            if obj["detected"]:
                object_types[obj_type]['detected'] += 1

        results_text += f"\n\n📈 OBJECT TYPE BREAKDOWN:"
        for obj_type, stats in object_types.items():
            detection_rate = (stats['detected'] / stats['total']) * 100 if stats['total'] > 0 else 0
            results_text += f"\n   {obj_type.upper()}: {stats['detected']}/{stats['total']} ({detection_rate:.1f}%)"

        # Add environmental and configuration info
        results_text += f"\n\n🌊 ENVIRONMENTAL CONDITIONS:"
        results_text += f"\n   Sea State: {report.get('sea_state', 'Unknown')}"
        results_text += f"\n   Communication Range: {report.get('communication_range', 'Unknown')}m"
        
        # Add mission performance metrics
        results_text += f"\n\n📈 MISSION PERFORMANCE METRICS:"
        results_text += f"\n   Total Events Logged: {report.get('total_events', 0):,}"
        results_text += f"\n   Detection Events: {report.get('detection_events', 0):,}"
        results_text += f"\n   Mission Efficiency: {(sim_summary['objects_detected']/max(sim_summary['total_objects'], 1)) * 100:.1f}%"
        results_text += f"\n   Distance per Object: {sim_summary['total_distance_traveled']/max(sim_summary['objects_detected'], 1):.1f}m/object"
        
        # Add simulation statistics
        if 'simulation_time' in report:
            results_text += f"\n   Simulation Time: {report['simulation_time']:.2f} seconds"
            results_text += f"\n   Ticks per Second: {sim_summary['total_ticks']/report['simulation_time']:.0f}"

        results_text += f"\n\n════════════════════════════════════════════════════════════════"
        results_text += f"\n🎊 Mission completed successfully! Review details above."
        results_text += f"\n💾 Data exported to outputs/ folder for further analysis."
        results_text += f"\n📊 Use Export buttons to save this report or CSV data."
        results_text += f"\n════════════════════════════════════════════════════════════════"
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, results_text)
    
    def display_comparison_results(self, results):
        """Display configuration comparison results"""
        if not results:
            return
            
        comparison_text = "🔬 CONFIGURATION COMPARISON RESULTS\n"
        comparison_text += "=" * 60 + "\n\n"
        
        for config_name, result in results.items():
            comm_stats = result['report']['communication_stats']
            sim_summary = result['report']['simulation_summary']
            
            comparison_text += f"📡 {config_name.upper()} Configuration:\n"
            comparison_text += f"   Success Rate: {comm_stats['overall_communication_success']:.1%}\n"
            comparison_text += f"   Objects Detected: {sim_summary['objects_detected']}/{sim_summary['total_objects']}\n"
            comparison_text += f"   Average Delay: {comm_stats['average_total_delay_ms']:.1f}ms\n"
            comparison_text += f"   Max Distance: {sim_summary['max_distance_from_ship']:.1f}m\n\n"
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, comparison_text)

if __name__ == "__main__":
    app = UUVSimulationGUI()
    app.run() 