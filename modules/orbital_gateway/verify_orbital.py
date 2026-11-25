"""
REMI Orbital Gateway - Complete 5-Pillar Subsystem Verification Script
Author: jramonrivasg
Description: Validates ISS, Earth atmosphere, Webcams, Starlink, and ABAE sovereign satellite feeds.
"""

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '../..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from modules.orbital_gateway.telemetry_engine import compile_orbital_matrix
from modules.orbital_gateway.earth_observer import compile_earth_observation_matrix
from modules.orbital_gateway.webcam_observer import compile_visual_surveillance_matrix
from modules.orbital_gateway.starlink_engine import compile_starlink_matrix
from modules.orbital_gateway.abae_engine import compile_abae_matrix

if __name__ == "__main__":
    print("[INIT] Executing 5-Pillar REMI Orbital Gateway diagnostic...\n")
    try:
        print("[1/5] Compiling Orbital Telemetry (ISS)...")
        print(compile_orbital_matrix())
        
        print("\n[2/5] Compiling Earth Observation & Atmospheric Metadata...")
        print(compile_earth_observation_matrix())
        
        print("\n[3/5] Compiling Global Webcam & Authorized Surveillance Matrix...")
        print(compile_visual_surveillance_matrix())
        
        print("\n[4/5] Compiling Starlink LEO Constellation Telemetry...")
        print(compile_starlink_matrix())

        print("\n[5/5] Compiling ABAE Sovereign Satellite Telemetry (Venezuela)...")
        print(compile_abae_matrix())
        
        print("\n[SUCCESS] All five pillars of the Orbital Gateway verified successfully.")
    except Exception as e:
        print(f"\n[ERROR] Diagnostic failure: {e}")
