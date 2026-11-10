"""
REMI Orbital Gateway - ABAE Sovereign Satellite Tracking Engine
Author: jramonrivasg (Sovereign Node: ramon-desktop)
Description: Tracks operational Venezuelan remote-sensing satellites (VRSS-1 Miranda, VRSS-2 Sucre)
             via open ephemeris public registries.
"""

import requests
from datetime import datetime, timezone

def fetch_abae_telemetry():
    """
    Queries public orbital databases for ABAE sovereign constellation nodes 
    (VRSS-1 NORAD: 38748, VRSS-2 NORAD: 42967).
    """
    try:
        url = "https://celestrak.org/NORAD/elements/gp.php?CATNR=38748&FORMAT=json"
        headers = {"User-Agent": "REMI-Sovereign-Gateway/1.0"}
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                sat = data[0]
                return {
                    "status": "ONLINE",
                    "agency": "ABAE Venezuela",
                    "satellite": sat.get("OBJECT_NAME", "VRSS-1 (MIRANDA)"),
                    "norad_id": sat.get("NORAD_CAT_ID", "38748"),
                    "epoch": sat.get("EPOCH", "N/A"),
                    "mean_motion": f"{sat.get('MEAN_MOTION', 'N/A')} revs/day",
                    "eccentricity": sat.get("ECCENTRICITY", "N/A")
                }
        return {"status": "DEGRADED", "error": f"HTTP Status {response.status_code}"}
    except Exception as e:
        return {"status": "OFFLINE", "error": str(e)}

def compile_abae_matrix():
    """
    Compiles ABAE sovereign satellite metrics into a structured intelligence block 
    for REMI's national orbital observation layer.
    """
    data = fetch_abae_telemetry()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    report = (
        f"=== ABAE SOVEREIGN ORBITAL TELEMETRY ===\n"
        f"- Query Epoch: {timestamp}\n"
        f"--- NATIONAL ASSET TRACKING (VENEZUELA) ---\n"
        f"  * Status: {data.get('status')}\n"
        f"  * Space Agency: {data.get('agency', 'ABAE')}\n"
        f"  * Target Asset: {data.get('satellite', 'N/A')} (NORAD: {data.get('norad_id', 'N/A')})\n"
        f"  * Orbital Epoch: {data.get('epoch', 'N/A')}\n"
        f"  * Mean Motion: {data.get('mean_motion', 'N/A')}\n"
        f"=========================================="
    )
    return report
