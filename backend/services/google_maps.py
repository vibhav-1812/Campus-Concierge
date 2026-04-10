import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import googlemaps
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

_GOOGLE_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
_client: Optional[googlemaps.Client] = googlemaps.Client(key=_GOOGLE_KEY) if _GOOGLE_KEY else None

def ensure_client() -> googlemaps.Client:
    if not _client:
        raise RuntimeError("GOOGLE_MAPS_API_KEY not set")
    return _client

def geocode_place(name: str) -> Optional[Dict[str, Any]]:
    """
    Resolve a place name to lat/lng using Google Geocoding.
    """
    client = ensure_client()
    results = client.geocode(name, region="us")
    if not results:
        return None
    r = results[0]
    loc = r["geometry"]["location"]
    return {
        "name": r.get("formatted_address", name),
        "lat": loc["lat"],
        "lng": loc["lng"],
        "place_id": r.get("place_id"),
    }

def directions_transit(origin: str | Tuple[float, float], destination: str | Tuple[float, float],
                       departure_time: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Get multimodal (transit + walk) directions. Returns a structured plan.
    """
    client = ensure_client()
    if departure_time is None:
        departure_time = datetime.now()

    dirs = client.directions(
        origin=origin,
        destination=destination,
        mode="transit",
        alternatives=False,
        departure_time=departure_time
    )
    if not dirs:
        return {"routes": []}

    route = dirs[0]
    leg = route["legs"][0]
    steps_out: List[Dict[str, Any]] = []

    for s in leg["steps"]:
        step = {"mode": s["travel_mode"], "duration_text": s["duration"]["text"]}
        if s["travel_mode"] == "WALKING":
            step["instruction"] = s.get("html_instructions", "Walk")
            step["distance_text"] = s["distance"]["text"]
        if s["travel_mode"] == "TRANSIT":
            td = s["transit_details"]
            line = td["line"]
            step.update({
                "instruction": f"Take {line.get('short_name') or line.get('name')} toward {td['headsign']}",
                "departure_stop": td["departure_stop"]["name"],
                "arrival_stop": td["arrival_stop"]["name"],
                "departure_time": td["departure_time"]["text"],
                "arrival_time": td["arrival_time"]["text"],
                "num_stops": td.get("num_stops"),
                "line_short_name": line.get("short_name"),
                "agency": (line.get("agencies") or [{}])[0].get("name", "")
            })
        steps_out.append(step)

    return {
        "summary": route.get("summary", ""),
        "duration_text": leg["duration"]["text"],
        "arrival_time": leg.get("arrival_time", {}).get("text"),
        "departure_time": leg.get("departure_time", {}).get("text"),
        "steps": steps_out
    }
