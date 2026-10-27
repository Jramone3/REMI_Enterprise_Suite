"""
REMI Orbital Gateway - Earth Observation & Atmospheric Engine
Author: jramonrivasg (Sovereign Node: ramon-desktop)
Description: Manages open-source meteorological telemetry, atmospheric indices, 
             and global earth observation metadata feeds.
"""

import requests
from datetime import datetime, timezone

def fetch_global_atmospheric_indices():
    """
    Queries open meteorological and atmospheric telemetry endpoints 
    for global environmental baseline tracking.
    """
    try:
        # Using Open-Meteo public free open API for global coordinates baseline (e.g., Equator / Prime Meridian)
        url = "https://api.open-meteo.com/v1/forecast?latitude=0.0&longitude=0.0&current=temperature_2m,relative_humidity_2m,surface_pressure"
        response = requests.get(url, timeout=4)
        
        if response.status_code == 200:
            data = response.json()
            current = data.get("current", {})
            return {
                "status": "ONLINE",
                "reference_point": "Global Baseline (Lat 0.0°, Lon 0.0°)",
                "surface_temperature": f"{current.get('temperature_2m', 'N/A')} °C",
                "relative_humidity": f"{current.get('relative_humidity_2m', 'N/A')}%",
                "surface_pressure": f"{current.get('surface_pressure', 'N/A')} hPa"
            }
        return {"status": "DEGRADED", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "OFFLINE", "error": str(e)}

def compile_earth_observation_matrix():
    """
    Aggregates earth observation metadata and atmospheric telemetry 
    into a structured intelligence block for REMI's global perspective.
    """
    atmos = fetch_global_atmospheric_indices()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    report = (
        f"=== EARTH OBSERVATION & ATMOSPHERIC METADATA ===\n"
        f"- Evaluation Timestamp: {timestamp}\n"
        f"--- ATMOSPHERIC BASELINE TELEMETRY ---\n"
        f"  * Status: {atmos.get('status')}\n"
        f"  * Reference Scope: {atmos.get('reference_point')}\n"
        f"  * Ambient Temperature: {atmos.get('surface_temperature')}\n"
        f"  * Humidity Index: {atmos.get('relative_humidity')}\n"
        f"  * Atmospheric Pressure: {atmos.get('surface_pressure')}\n"
        f"--- GLOBAL WEBCAM / VISUAL FEEDS METADATA ---\n"
        f"  * Active Feeds Register: Open-Source Public Nodes (Windy/NOAA imagery proxies)\n"
        f"  * Visual Surveillance State: Standby (On-demand query mode)\n"
        f"================================================="
    )
    return report
