"""
Setup script for creating UUV Communication Simulation .app bundle
Enhanced for macOS compatibility with crash prevention
"""

from setuptools import setup

APP = ['macos_launcher.py']
DATA_FILES = [
    ('models', [
        'models/acoustic_config.py', 
        'models/csv_logger.py',
        'models/ml_csv_logger.py',
        'models/simulation_controller.py',
        'models/game_state.py',
        'models/communication_model.py',
        'models/acoustic_physics.py',
        'models/packet.py'
    ]),
    ('.', [
        'simulation_gui.py',
        'complex_simulation.py'
    ])
]

OPTIONS = {
    'argv_emulation': False,  # Disable to prevent tkinter menu bar conflicts
    'strip': True,
    'optimize': 1,
    'iconfile': None,  # You can add an .icns file here if you have one
    'plist': {
        'CFBundleName': 'UUV Communication Simulator',
        'CFBundleDisplayName': 'UUV Communication Simulator',
        'CFBundleGetInfoString': 'Military-grade underwater acoustic communication simulation',
        'CFBundleIdentifier': 'com.thesis.uuv-simulator',
        'CFBundleVersion': '1.0.2',
        'CFBundleShortVersionString': '1.0.2',
        'CFBundleExecutable': 'UUV Communication Simulator',
        'NSRequiresAquaSystemAppearance': False,
        'LSMinimumSystemVersion': '10.14',
        'NSHighResolutionCapable': True,
        'NSSupportsAutomaticGraphicsSwitching': True,
        # Prevent automatic menu bar creation
        'LSUIElement': False,
        'NSAppleScriptEnabled': False,
        # macOS app transport security
        'NSAppTransportSecurity': {
            'NSAllowsArbitraryLoads': True
        },
        # Accessibility and display settings
        'NSSupportsAutomaticTermination': True,
        'NSSupportsSuddenTermination': True,
    },
    'excludes': ['PyQt4', 'PyQt5', 'PySide', 'PySide2'],
    'includes': ['tkinter', 'tkinter.ttk', 'tkinter.messagebox', 'tkinter.filedialog', 'queue', 'threading', 'datetime', 'json', 'os', 'time', 'platform'],
    'frameworks': [],
    'resources': [],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    name='UUV Communication Simulator',
    version='1.0.2',
    description='Military-grade underwater acoustic communication simulation',
    author='UUV Research Team',
    python_requires='>=3.8',
) 