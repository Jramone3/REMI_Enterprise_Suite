"""
REMI Orbital Gateway - Advanced Telemetry & Space Observation Engine
Author: jramonrivasg (Sovereign Node: ramon-desktop)
Description: Comprehensive collector for open orbital telemetry, satellite positioning, 
             and atmospheric/space weather metadata.
"""

import requests
from datetime import datetime, timezone

def fetch_iss_telemetry():
    """
    Queries open public telemetry for the International Space Station (NORAD ID: 25544).
    """
    try:
        url = "https://api.wheretheiss.at/v1/satellites/25544"
        response = requests.get(url, timeout=4)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "ONLINE",
                "target": "ISS (NORAD 25544)",
                "latitude": round(data.get("latitude", 0.0), 4),
                "longitude": round(data.get("longitude", 0.0), 4),
                "altitude_km": round(data.get("altitude", 0.0), 2),
                "velocity_kmh": round(data.get("velocity", 0.0), 2),
                "visibility": data.get("visibility", "unknown"),
                "footprint": round(data.get("footprint", 0.0), 2)
            }
        return {"status": "DEGRADED", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "OFFLINE", "error": str(e)}

def fetch_space_weather_telemetry():
    """
    Queries public NOAA space weather / solar activity indicators.
    """
    try:
        url = "https://services.swpc.noaa.gov/json/solar-cycle/solar-cycle-indices.json"
        response = requests.get(url, timeout=4)
        if response.status_code == 200:
            data = response.json()
            latest = data[-1] if data else {}
            return {
                "status": "ONLINE",
                "solar_cycle": latest.get("icyclo", "N/A"),
                "smoothed_sunspot_number": latest.get("ssn", "N/A"),
                "observed_flux": latest.get("flux", "N/A")
            }
        return {"status": "DEGRADED", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "OFFLINE", "error": str(e)}

def compile_orbital_matrix():
    """
    Aggregates all telemetry feeds into a structured, LLM-ready context block.
    """
    iss = fetch_iss_telemetry()
    weather = fetch_space_weather_telemetry()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    report = (
        f"=== ORBITAL & SPACE TELEMETRY REPORT ===\n"
        f"- Epoch Timestamp: {timestamp}\n"
        f"--- PRIMARY TARGET (ISS) ---\n"
        f"  * Status: {iss.get('status')}\n"
        f"  * Coordinates: Lat {iss.get('latitude')}°, Lon {iss.get('longitude')}°\n"
        f"  * Altitude: {iss.get('altitude_km')} km | Velocity: {iss.get('velocity_kmh')} km/h\n"
        f"  * Solar Illumination: {iss.get('visibility')}\n"
        f"--- SPACE WEATHER / SOLAR METRICS ---\n"
        f"  * Status: {weather.get('status')}\n"
        f"  * Sunspot Index: {weather.get('smoothed_sunspot_number')}\n"
        f"  * Radio Flux: {weather.get('observed_flux')}\n"
        f"========================================"
    )
    return report
