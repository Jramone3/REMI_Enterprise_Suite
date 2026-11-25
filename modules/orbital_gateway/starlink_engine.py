"""
REMI Orbital Gateway - Starlink LEO Constellation Tracking Engine
Author: jramonrivasg (Sovereign Node: ramon-desktop)
Description: Queries open public CelesTrak GP catalogs for live 
             Starlink Low Earth Orbit (LEO) constellation telemetry and node counts.
"""

import requests
from datetime import datetime, timezone

def fetch_starlink_constellation_telemetry():
    """
    Queries CelesTrak open public General Perturbations (GP) API 
    for live Starlink constellation tracking metadata.
    """
    try:
        url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=json"
        headers = {"User-Agent": "REMI-Sovereign-Gateway/1.0"}
        response = requests.get(url, headers=headers, timeout=8)
        
        if response.status_code == 200:
            satellites = response.json()
            total_nodes = len(satellites)
            
            sample_nodes = []
            for sat in satellites[:3]:
                sample_nodes.append({
                    "name": sat.get("OBJECT_NAME", "N/A"),
                    "norad_id": sat.get("NORAD_CAT_ID", "N/A"),
                    "epoch": sat.get("EPOCH", "N/A")
                })
            
            return {
                "status": "ONLINE",
                "constellation": "SpaceX Starlink LEO",
                "active_tracked_nodes": total_nodes,
                "catalog_source": "CelesTrak Open GP Registry",
                "sample_nodes": sample_nodes
            }
        return {"status": "DEGRADED", "error": f"HTTP Status {response.status_code}"}
    except Exception as e:
        return {"status": "OFFLINE", "error": str(e)}

def compile_starlink_matrix():
    """
    Compiles Starlink constellation metrics into a structured intelligence block 
    for REMI's orbital observation layer.
    """
    data = fetch_starlink_constellation_telemetry()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    report_lines = [
        f"=== STARLINK LEO CONSTELLATION TELEMETRY ===",
        f"- Query Epoch: {timestamp}",
        f"--- CONSTELLATION STATUS ---",
        f"  * Status: {data.get('status')}",
        f"  * Target Network: {data.get('constellation', 'N/A')}",
        f"  * Total Tracked Active Nodes: {data.get('active_tracked_nodes', 'N/A')}",
        f"  * Data Source: {data.get('catalog_source', 'N/A')}"
    ]

    if data.get("status") == "ONLINE" and "sample_nodes" in data:
        report_lines.append(f"--- SAMPLE ACTIVE NODES OVERHEAD ---")
        for node in data["sample_nodes"]:
            report_lines.append(f"  * [{node['norad_id']}] {node['name']} (Epoch: {node['epoch']})")

    report_lines.append(f"============================================")
    return "\n".join(report_lines)
