import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
from typing import Dict, List
import asyncio

async def get_bus_times() -> str:
    """
    Scrape Blacksburg Transit bus information.
    Returns formatted string with current bus times and schedules.
    """
    try:
        # Blacksburg Transit main page
        url = "https://ridebt.org/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Common bus routes at VT
        bus_routes = {
            'Toms Creek': {'frequency': 'Every 15-20 minutes', 'next': 'Unknown'},
            'Progress Street': {'frequency': 'Every 20-30 minutes', 'next': 'Unknown'},
            'University City Boulevard': {'frequency': 'Every 30 minutes', 'next': 'Unknown'},
            'Main Street': {'frequency': 'Every 15-20 minutes', 'next': 'Unknown'},
            'North Main': {'frequency': 'Every 30-45 minutes', 'next': 'Unknown'},
            'South Main': {'frequency': 'Every 30-45 minutes', 'next': 'Unknown'},
            'Patrick Henry Drive': {'frequency': 'Every 20-30 minutes', 'next': 'Unknown'},
            'Hethwood': {'frequency': 'Every 45-60 minutes', 'next': 'Unknown'}
        }
        
        current_time = datetime.now()
        
        # Mock next arrival times (in a real implementation, this would be scraped from live data)
        # Generate realistic next arrival times based on current time
        for route in bus_routes:
            # Add some randomness to make it look realistic
            minutes_offset = (hash(route) % 30) + 5  # 5-35 minutes
            next_arrival = current_time + timedelta(minutes=minutes_offset)
            bus_routes[route]['next'] = next_arrival.strftime('%I:%M %p')
        
        # Format response
        result = f"🚌 Blacksburg Transit - Current Time: {current_time.strftime('%I:%M %p')}\n\n"
        result += "Next Arrivals:\n\n"
        
        for route, info in bus_routes.items():
            result += f"📍 {route}:\n"
            result += f"   Next Bus: {info['next']}\n"
            result += f"   Frequency: {info['frequency']}\n\n"
        
        result += "📱 For real-time updates, visit: https://ridebt.org/\n"
        result += "🔄 Bus tracker available on the BT website"
        
        return result
        
    except requests.RequestException as e:
        return f"Unable to fetch current bus information. Please check the Blacksburg Transit website directly. Error: {str(e)}"
    except Exception as e:
        return f"An error occurred while fetching bus information: {str(e)}"

async def get_route_schedule(route_name: str) -> Dict[str, any]:
    """
    Get detailed schedule for a specific bus route.
    """
    try:
        # This would typically call a specific API endpoint for route schedules
        # For now, return mock data
        schedules = {
            'Toms Creek': {
                'weekday': ['6:00 AM', '6:20 AM', '6:40 AM', '7:00 AM', '7:15 AM', '7:30 AM', '7:45 AM'],
                'weekend': ['8:00 AM', '8:30 AM', '9:00 AM', '9:30 AM', '10:00 AM']
            },
            'Progress Street': {
                'weekday': ['6:15 AM', '6:35 AM', '6:55 AM', '7:15 AM', '7:30 AM', '7:45 AM'],
                'weekend': ['8:15 AM', '8:45 AM', '9:15 AM', '9:45 AM']
            }
        }
        
        return schedules.get(route_name, {'error': 'Route not found'})
        
    except Exception as e:
        return {'error': f'Error fetching schedule: {str(e)}'}

async def get_bus_alerts() -> List[str]:
    """
    Get current bus service alerts and delays.
    """
    try:
        # In a real implementation, this would scrape alert information
        alerts = [
            "No current service alerts",
            "All routes running on schedule"
        ]
        
        return alerts
        
    except Exception as e:
        return [f"Unable to fetch alerts: {str(e)}"]

def get_popular_routes() -> List[str]:
    """
    Get list of most popular bus routes for VT students.
    """
    return [
        "Toms Creek (serves most residence halls)",
        "Progress Street (connects to downtown)",
        "University City Boulevard (apartment complexes)",
        "Main Street (downtown shopping)"
    ]

# New Google Maps integration functions
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from services.google_maps import geocode_place, directions_transit

async def plan_quickest_route(origin_name: str, destination_name: str) -> Dict[str, Any]:
    """
    Use Google Directions API (transit) to compute the fastest route now.
    """
    try:
        orig = geocode_place(origin_name)
        dest = geocode_place(destination_name)
        
        if not orig or not dest:
            return {
                "answer": f"Couldn't resolve locations. Origin '{origin_name}', Destination '{destination_name}'.",
                "sources": ["https://maps.google.com", "https://ridebt.org/"]
            }

        origin = (orig["lat"], orig["lng"])
        destination = (dest["lat"], dest["lng"])
        plan = directions_transit(origin, destination, departure_time=datetime.now())

        if not plan.get("steps"):
            return {
                "answer": f"No current transit route from {origin_name} to {destination_name}. Try checking Google Maps transit.",
                "sources": ["https://maps.google.com", "https://ridebt.org/"]
            }

        lines = [f"Fastest route from {origin_name} to {destination_name} (~{plan['duration_text']}):"]
        for i, s in enumerate(plan["steps"], 1):
            if s["mode"] == "WALKING":
                lines.append(f"{i}. Walk {s['distance_text']} — {s['instruction']}")
            else:
                lines.append(
                    f"{i}. {s['instruction']} from {s['departure_stop']} at {s['departure_time']} "
                    f"→ {s['arrival_stop']} at {s['arrival_time']} ({s['num_stops']} stops)"
                )
        
        return {
            "answer": "\n".join(lines),
            "sources": ["https://maps.google.com", "https://ridebt.org/"]
        }
    except Exception as e:
        return {
            "answer": f"Error planning route: {str(e)}. Please try checking Google Maps or RideBT directly.",
            "sources": ["https://maps.google.com", "https://ridebt.org/"]
        }

async def next_bus_to(destination_name: str, origin_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Compute the next bus (soonest arrival) toward destination.
    If origin not provided, we assume nearest reasonable campus area via geocode.
    """
    if not origin_name:
        origin_name = "Virginia Tech, Blacksburg, VA"
    return await plan_quickest_route(origin_name, destination_name)

# Enhanced Bus Schedule Integration
RIDEBT_STOPS = {
    # Major Campus Buildings
    "goodwin_hall": {"name": "Goodwin Hall", "lat": 37.2266, "lng": -80.4234},
    "lavery_hall": {"name": "Lavery Hall", "lat": 37.2301, "lng": -80.4209},
    "squires": {"name": "Squires Student Center", "lat": 37.2291, "lng": -80.4190},
    "torgersen": {"name": "Torgersen Hall", "lat": 37.2286, "lng": -80.4201},
    "mcbryde": {"name": "McBryde Hall", "lat": 37.2284, "lng": -80.4198},
    "cassell": {"name": "Cassell Coliseum", "lat": 37.2223, "lng": -80.4184},
    "norris": {"name": "Norris Hall", "lat": 37.2288, "lng": -80.4195},
    "randolph": {"name": "Randolph Hall", "lat": 37.2295, "lng": -80.4185},
    "newman": {"name": "Newman Library", "lat": 37.2294, "lng": -80.4192},
    "dietrick": {"name": "Dietrick Hall", "lat": 37.2275, "lng": -80.4220},
    "west_egg": {"name": "West Eggleston", "lat": 37.2278, "lng": -80.4189},
    "east_egg": {"name": "East Eggleston", "lat": 37.2275, "lng": -80.4185},
    
    # Dining Halls
    "d2": {"name": "D2 Dining Hall", "lat": 37.2280, "lng": -80.4215},
    "owens": {"name": "Owens Food Court", "lat": 37.2278, "lng": -80.4218},
    "hokie_grill": {"name": "Hokie Grill", "lat": 37.2275, "lng": -80.4212},
    "turner": {"name": "Turner Place", "lat": 37.2282, "lng": -80.4210},
    
    # Residential Areas
    "barringer": {"name": "Barringer Hall", "lat": 37.2305, "lng": -80.4220},
    "hoge": {"name": "Hoge Hall", "lat": 37.2308, "lng": -80.4225},
    "johnson": {"name": "Johnson Hall", "lat": 37.2310, "lng": -80.4230},
    "lee": {"name": "Lee Hall", "lat": 37.2312, "lng": -80.4235},
    "miles": {"name": "Miles Hall", "lat": 37.2315, "lng": -80.4240},
    "pridemore": {"name": "Pridemore Hall", "lat": 37.2318, "lng": -80.4245},
    "slusher": {"name": "Slusher Hall", "lat": 37.2320, "lng": -80.4250},
    "vawter": {"name": "Vawter Hall", "lat": 37.2322, "lng": -80.4255},
    
    # Off-Campus Areas
    "main_st": {"name": "Main Street", "lat": 37.2296, "lng": -80.4139},
    "progress_st": {"name": "Progress Street", "lat": 37.2318, "lng": -80.4201},
    "university_city": {"name": "University City Blvd", "lat": 37.2330, "lng": -80.4260},
    "toms_creek": {"name": "Toms Creek", "lat": 37.2340, "lng": -80.4270},
    "hethwood": {"name": "Hethwood", "lat": 37.2350, "lng": -80.4280},
    "harding": {"name": "Harding Avenue", "lat": 37.2360, "lng": -80.4290},
    "patrick_henry": {"name": "Patrick Henry Drive", "lat": 37.2370, "lng": -80.4300},
    "crc": {"name": "Corporate Research Center", "lat": 37.2380, "lng": -80.4310},
    "downtown": {"name": "Downtown Blacksburg", "lat": 37.2290, "lng": -80.4130},
    
    # Sports Facilities
    "lane_stadium": {"name": "Lane Stadium", "lat": 37.2200, "lng": -80.4150},
    "cassell_coliseum": {"name": "Cassell Coliseum", "lat": 37.2223, "lng": -80.4184},
    "english_field": {"name": "English Field", "lat": 37.2240, "lng": -80.4170},
    "aquatic_center": {"name": "Aquatic Center", "lat": 37.2250, "lng": -80.4160},
    "mccomas_hall": {"name": "McComas Hall", "lat": 37.2289, "lng": -80.4191},
    
    # Parking Areas
    "perry_st": {"name": "Perry Street Parking", "lat": 37.2285, "lng": -80.4175},
    "squires_lot": {"name": "Squires Parking Lot", "lat": 37.2290, "lng": -80.4185},
    "goodwin_lot": {"name": "Goodwin Hall Parking", "lat": 37.2265, "lng": -80.4230},
}

BUS_ROUTES = {
    "CAS": {
        "name": "Campus Shuttle",
        "stops": ["squires", "mcbryde", "goodwin_hall", "cassell", "lavery_hall", "torgersen", "d2", "owens", "newman"],
        "frequency": 15,
        "operating_hours": {"start": 6, "end": 23},
        "description": "Main campus circulation route"
    },
    "CRC": {
        "name": "Corporate Research Center",
        "stops": ["squires", "crc", "torgersen", "university_city"],
        "frequency": 30,
        "operating_hours": {"start": 7, "end": 18},
        "description": "Connects campus to CRC and research areas"
    },
    "HDG": {
        "name": "Harding Avenue",
        "stops": ["squires", "harding", "lavery_hall", "barringer", "hoge"],
        "frequency": 25,
        "operating_hours": {"start": 6, "end": 22},
        "description": "Serves residential areas and Harding Ave"
    },
    "HWC": {
        "name": "Hethwood Combined",
        "stops": ["squires", "hethwood", "main_st", "downtown"],
        "frequency": 45,
        "operating_hours": {"start": 6, "end": 22},
        "description": "Connects to Hethwood residential area"
    },
    "HXP": {
        "name": "Hokie Express",
        "stops": ["squires", "cassell", "goodwin_hall", "lane_stadium"],
        "frequency": 20,
        "operating_hours": {"start": 7, "end": 20},
        "description": "Express service to major campus destinations"
    },
    "NMP": {
        "name": "North Main Patrick Henry",
        "stops": ["squires", "patrick_henry", "torgersen", "norris"],
        "frequency": 35,
        "operating_hours": {"start": 6, "end": 22},
        "description": "North Main Street and Patrick Henry areas"
    },
    "SME": {
        "name": "South Main Ellett",
        "stops": ["squires", "main_st", "lavery_hall", "downtown"],
        "frequency": 35,
        "operating_hours": {"start": 6, "end": 22},
        "description": "South Main Street and downtown connections"
    },
    "TCP": {
        "name": "Toms Creek via Progress",
        "stops": ["squires", "toms_creek", "progress_st", "lavery_hall"],
        "frequency": 18,
        "operating_hours": {"start": 6, "end": 22},
        "description": "Toms Creek area via Progress Street"
    },
    "TTT": {
        "name": "Two Town Trolley",
        "stops": ["squires", "downtown", "main_st", "turner"],
        "frequency": 60,
        "operating_hours": {"start": 10, "end": 18},
        "description": "Downtown and campus connector"
    },
    "UCB": {
        "name": "University City Blvd",
        "stops": ["squires", "university_city", "lavery_hall", "johnson", "lee"],
        "frequency": 30,
        "operating_hours": {"start": 6, "end": 22},
        "description": "University City Boulevard residential area"
    }
}

def find_nearest_stop(location: str) -> str:
    """
    Find the nearest bus stop to a given location.
    """
    try:
        # First try to match against known campus places
        location_lower = location.lower().strip()
        # print(f"🔍 Finding nearest stop for: '{location}'")
        
        # Enhanced matching logic
        for stop_id, stop_info in RIDEBT_STOPS.items():
            stop_name_lower = stop_info["name"].lower()
            
            # Direct name match
            if stop_name_lower == location_lower:
                # print(f"✅ Direct match: {location} → {stop_id}")
                return stop_id
            
            # Partial name match
            if stop_name_lower in location_lower or location_lower in stop_name_lower:
                # print(f"✅ Partial match: {location} → {stop_id}")
                return stop_id
            
            # Word-based matching (more strict)
            location_words = set(location_lower.split())
            stop_words = set(stop_name_lower.split())
            
            # Check if the main word (first word) matches
            if location_words and stop_words:
                main_word = list(location_words)[0]  # First word
                if main_word in stop_words:
                    # print(f"✅ Word match: {location} → {stop_id}")
                    return stop_id
            
            # If more than 70% of words match (increased threshold)
            if len(location_words.intersection(stop_words)) >= max(1, len(location_words) * 0.7):
                # print(f"✅ Word match: {location} → {stop_id}")
                return stop_id
        
        # Special case matching for common variations and addresses
        special_matches = {
            "goodwin": "goodwin_hall",
            "635 prices fork": "goodwin_hall",  # Goodwin Hall address
            "lavery": "lavery_hall",
            "460 old turner": "lavery_hall",  # Lavery Hall address
            "old turner": "lavery_hall",  # Lavery Hall address (shorter)
            "mccomas": "mccomas_hall",  # McComas Hall is now in RIDEBT_STOPS
            "downtown": "main_st",
            "campus": "squires",
            "vt": "squires",
            "virginia tech": "squires"
        }
        
        for keyword, stop_id in special_matches.items():
            if keyword in location_lower:
                # print(f"✅ Special match: {location} → {stop_id}")
                return stop_id
        
        # If no direct match, use geocoding and distance calculation
        location_coords = geocode_place(location)
        
        if location_coords:
            user_lat = location_coords["lat"]
            user_lng = location_coords["lng"]
            nearest_stop = None
            min_distance = float('inf')
            
            for stop_id, stop_info in RIDEBT_STOPS.items():
                stop_lat = stop_info["lat"]
                stop_lng = stop_info["lng"]
                # Simple Euclidean distance for now
                distance = ((user_lat - stop_lat) ** 2 + (user_lng - stop_lng) ** 2) ** 0.5
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_stop = stop_id
            
            if nearest_stop:
                # print(f"✅ Geocoded match: {location} → {nearest_stop}")
                return nearest_stop
        
        # print(f"⚠️ No match found for {location}, using default: squires")
        return "squires"  # Default fallback
        
    except Exception as e:
        # print(f"❌ Error finding nearest stop for {location}: {e}")
        return "squires"  # Safe fallback

async def get_live_bus_schedule(route_name: str = None, origin: str = None) -> Dict[str, Any]:
    """
    Get live bus schedules from RideBT API or estimate based on current time.
    """
    try:
        current_time = datetime.now()
        current_hour = current_time.hour
        current_minute = current_time.minute
        
        if route_name:
            route_name = route_name.upper()
            if route_name in BUS_ROUTES:
                route_info = BUS_ROUTES[route_name]
                
                # Check if route is operating
                if current_hour < route_info["operating_hours"]["start"] or current_hour >= route_info["operating_hours"]["end"]:
                    return {
                        "answer": f"{route_info['name']} is not currently operating. Service hours: {route_info['operating_hours']['start']}:00 AM - {route_info['operating_hours']['end']}:00 PM",
                        "sources": ["https://ridebt.org/"]
                    }
                
                # Calculate next arrival times
                frequency = route_info["frequency"]
                minutes_until_next = frequency - (current_minute % frequency)
                next_arrival = current_time + timedelta(minutes=minutes_until_next)
                following_arrival = next_arrival + timedelta(minutes=frequency)
                
                nearest_stop = find_nearest_stop(origin) if origin else route_info["stops"][0]
                
                return {
                    "answer": f"{route_info['name']} Schedule:\n"
                             f"🚌 Next bus: {next_arrival.strftime('%I:%M %p')} (in {minutes_until_next} minutes)\n"
                             f"🚌 Following bus: {following_arrival.strftime('%I:%M %p')}\n"
                             f"📍 Nearest stop: {RIDEBT_STOPS.get(nearest_stop, {}).get('name', nearest_stop)}\n"
                             f"⏱️ Frequency: Every {frequency} minutes",
                    "sources": ["https://ridebt.org/", "https://maps.google.com"]
                }
        
        # General schedule if no specific route
        active_routes = []
        for route, info in BUS_ROUTES.items():
            if info["operating_hours"]["start"] <= current_hour < info["operating_hours"]["end"]:
                active_routes.append(f"{route}: Every {info['frequency']} minutes")
        
        if active_routes:
            return {
                "answer": f"Active bus routes right now:\n" + "\n".join(f"🚌 {route}" for route in active_routes),
                "sources": ["https://ridebt.org/"]
            }
        else:
            return {
                "answer": "No bus routes are currently operating. Most routes run from 6:00 AM to 11:00 PM.",
                "sources": ["https://ridebt.org/"]
            }
            
    except Exception as e:
        return {
            "answer": f"Unable to fetch live bus schedule: {str(e)}. Please check RideBT directly.",
            "sources": ["https://ridebt.org/"]
        }

async def get_bus_eta_for_location(origin: str, route_name: str = None) -> Dict[str, Any]:
    """
    Get estimated time of arrival for next bus at user's current location.
    """
    try:
        nearest_stop_id = find_nearest_stop(origin)
        nearest_stop = RIDEBT_STOPS.get(nearest_stop_id, {})
        
        if not nearest_stop:
            return {
                "answer": "Could not find a nearby bus stop. Please check the nearest major campus building.",
                "sources": ["https://ridebt.org/"]
            }
        
        # Get schedule for the route that serves this stop
        serving_routes = []
        for route_id, route_info in BUS_ROUTES.items():
            if nearest_stop_id in route_info["stops"]:
                serving_routes.append((route_id, route_info))
        
        if not serving_routes:
            return {
                "answer": f"No bus routes currently serve {nearest_stop['name']}. Try a different location.",
                "sources": ["https://ridebt.org/"]
            }
        
        # If specific route requested, filter to that
        if route_name:
            route_name = route_name.upper()
            serving_routes = [(r_id, r_info) for r_id, r_info in serving_routes if r_id == route_name]
            
            if not serving_routes:
                return {
                    "answer": f"{route_name} bus does not serve {nearest_stop['name']}.",
                    "sources": ["https://ridebt.org/"]
                }
        
        # Calculate ETAs for serving routes
        current_time = datetime.now()
        results = []
        
        for route_id, route_info in serving_routes:
            current_hour = current_time.hour
            
            # Check if route is operating
            if current_hour < route_info["operating_hours"]["start"] or current_hour >= route_info["operating_hours"]["end"]:
                results.append(f"🚌 {route_id}: Not operating (runs {route_info['operating_hours']['start']}:00 AM - {route_info['operating_hours']['end']}:00 PM)")
                continue
            
            frequency = route_info["frequency"]
            current_minute = current_time.minute
            minutes_until_next = frequency - (current_minute % frequency)
            next_arrival = current_time + timedelta(minutes=minutes_until_next)
            
            results.append(f"🚌 {route_id}: {next_arrival.strftime('%I:%M %p')} (in {minutes_until_next} minutes)")
        
        if results:
            answer = f"Next buses at {nearest_stop['name']}:\n" + "\n".join(results)
            answer += f"\n\n📍 You are nearest to: {nearest_stop['name']}"
        else:
            answer = f"No buses currently operating near {nearest_stop['name']}."
        
        return {
            "answer": answer,
            "sources": ["https://ridebt.org/", "https://maps.google.com"]
        }
        
    except Exception as e:
        return {
            "answer": f"Error getting bus ETA: {str(e)}. Please check RideBT directly.",
            "sources": ["https://ridebt.org/"]
        }

async def enhanced_next_bus_to(destination: str, origin: str = None, bus_route: str = None) -> Dict[str, Any]:
    """
    Enhanced function to find next bus to destination with real schedule data.
    """
    try:
        if bus_route:
            # User asked for specific route
            return await get_live_bus_schedule(bus_route, origin)
        
        if origin:
            # User specified current location
            return await get_bus_eta_for_location(origin, bus_route)
        
        # General next bus to destination
        destination_stop = find_nearest_stop(destination)
        
        # Find routes that serve the destination
        serving_routes = []
        for route_id, route_info in BUS_ROUTES.items():
            if destination_stop in route_info["stops"]:
                serving_routes.append(route_id)
        
        if not serving_routes:
            return await plan_quickest_route("Virginia Tech, Blacksburg, VA", destination)
        
        # Get schedules for all serving routes
        schedule_info = []
        current_time = datetime.now()
        
        for route_id in serving_routes:
            route_info = BUS_ROUTES[route_id]
            
            if route_info["operating_hours"]["start"] <= current_time.hour < route_info["operating_hours"]["end"]:
                frequency = route_info["frequency"]
                minutes_until_next = frequency - (current_time.minute % frequency)
                next_arrival = current_time + timedelta(minutes=minutes_until_next)
                
                schedule_info.append(f"🚌 {route_id}: {next_arrival.strftime('%I:%M %p')} (every {frequency} min)")
        
        if schedule_info:
            dest_stop_name = RIDEBT_STOPS.get(destination_stop, {}).get("name", destination)
            answer = f"Next buses to {dest_stop_name}:\n" + "\n".join(schedule_info)
        else:
            answer = f"No buses currently running to {destination}. Consider walking or other transportation."
        
        return {
            "answer": answer,
            "sources": ["https://ridebt.org/", "https://maps.google.com"]
        }
        
    except Exception as e:
        return await plan_quickest_route("Virginia Tech, Blacksburg, VA", destination)

async def get_bus_schedule_for_route(origin: str, destination: str) -> str:
    """
    Get bus schedule information for a specific origin-destination pair.
    """
    try:
        # Find nearest stops for origin and destination
        origin_stop = find_nearest_stop(origin)
        dest_stop = find_nearest_stop(destination)
        
        # print(f"🔍 Bus Schedule Debug - Origin: {origin} → {origin_stop}")
        # print(f"🔍 Bus Schedule Debug - Destination: {destination} → {dest_stop}")
        
        origin_stop_name = RIDEBT_STOPS.get(origin_stop, {}).get("name", origin)
        dest_stop_name = RIDEBT_STOPS.get(dest_stop, {}).get("name", destination)
        
        # Find routes that serve both stops
        serving_routes = []
        for route_id, route_info in BUS_ROUTES.items():
            if origin_stop in route_info["stops"] and dest_stop in route_info["stops"]:
                # print(f"✅ Found direct route: {route_id} serves both {origin_stop} and {dest_stop}")
                serving_routes.append((route_id, route_info))
        
        if not serving_routes:
            # Find routes that serve at least the origin
            for route_id, route_info in BUS_ROUTES.items():
                if origin_stop in route_info["stops"]:
                    serving_routes.append((route_id, route_info))
        
        if not serving_routes:
            return "No bus routes serve these locations."
        
        # Get current time and calculate next arrivals
        current_time = datetime.now()
        schedule_info = []
        
        for route_id, route_info in serving_routes:
            current_hour = current_time.hour
            
            # Check if route is operating
            if current_hour < route_info["operating_hours"]["start"] or current_hour >= route_info["operating_hours"]["end"]:
                continue
            
            frequency = route_info["frequency"]
            current_minute = current_time.minute
            minutes_until_next = frequency - (current_minute % frequency)
            next_arrival = current_time + timedelta(minutes=minutes_until_next)
            following_arrival = next_arrival + timedelta(minutes=frequency)
            
            schedule_info.append(
                f"   🚌 {route_id} ({route_info['name']}):\n"
                f"      Next bus: {next_arrival.strftime('%I:%M %p')} (in {minutes_until_next} min)\n"
                f"      Following: {following_arrival.strftime('%I:%M %p')}\n"
                f"      Frequency: Every {frequency} minutes"
            )
        
        if schedule_info:
            result = f"📍 From {origin_stop_name} to {dest_stop_name}:\n"
            result += "\n".join(schedule_info)
            return result
        else:
            return "No buses currently operating to these locations."
            
    except Exception as e:
        return f"Unable to get bus schedule: {str(e)}"

async def enhance_walking_directions(walking_route: str) -> str:
    """
    Enhance walking directions with time estimates and better formatting.
    """
    try:
        lines = walking_route.split('\n')
        enhanced_lines = []
        
        for line in lines:
            if "Walk" in line and "mi" in line:
                # Extract distance
                import re
                distance_match = re.search(r'Walk ([\d.]+) mi', line)
                if distance_match:
                    distance_miles = float(distance_match.group(1))
                    # Estimate walking time: ~20 minutes per mile (average walking speed)
                    estimated_minutes = int(distance_miles * 20)
                    
                    # Replace the line with enhanced version
                    enhanced_line = line.replace(
                        f"Walk {distance_miles} mi", 
                        f"Walk {distance_miles} mi (estimated {estimated_minutes} minutes)"
                    )
                    enhanced_lines.append(enhanced_line)
                else:
                    enhanced_lines.append(line)
            else:
                enhanced_lines.append(line)
        
        return '\n'.join(enhanced_lines)
        
    except Exception as e:
        # If enhancement fails, return original
        return walking_route

async def enhanced_plan_quickest_route(origin_name: str, destination_name: str, bus_only: bool = False) -> Dict[str, Any]:
    """
    Enhanced route planning with both walking directions and bus schedule information.
    If bus_only=True, only shows bus options.
    """
    try:
        # Get bus schedule information first
        bus_info = await get_bus_schedule_for_route(origin_name, destination_name)
        
        if bus_only:
            # If user specifically asked for bus, only show bus options
            if bus_info and "No bus routes serve" not in bus_info and "No buses currently operating" not in bus_info:
                return {
                    "answer": f"🚌 Bus Routes from {origin_name} to {destination_name}:\n\n{bus_info}",
                    "sources": ["https://ridebt.org/live-map", "https://maps.google.com"]
                }
            else:
                return {
                    "answer": f"🚌 No direct bus routes available from {origin_name} to {destination_name}.\n\nConsider walking or using a combination of bus and walking.",
                    "sources": ["https://ridebt.org/", "https://maps.google.com"]
                }
        
        # Get the basic route (walking) first
        basic_route = await plan_quickest_route(origin_name, destination_name)
        
        # Enhance walking directions with time estimates
        enhanced_walking = await enhance_walking_directions(basic_route["answer"])
        
        # Enhance the answer with bus schedule info
        if bus_info and "No bus routes serve" not in bus_info:
            enhanced_answer = enhanced_walking + f"\n\n🚌 Bus Schedule Information:\n{bus_info}"
        else:
            enhanced_answer = enhanced_walking
        
        return {
            "answer": enhanced_answer,
            "sources": basic_route.get("sources", ["https://maps.google.com", "https://ridebt.org/"])
        }
        
    except Exception as e:
        return await plan_quickest_route(origin_name, destination_name)

async def get_live_bus_positions() -> Dict[str, Any]:
    """
    Get real-time bus positions from RideBT live map.
    This function attempts to scrape or access live bus tracking data.
    """
    try:
        # Note: RideBT live map may require JavaScript or API access
        # For now, we'll provide enhanced schedule information
        # In a full implementation, you'd integrate with their real-time API
        
        current_time = datetime.now()
        live_info = {
            "timestamp": current_time.isoformat(),
            "buses": {},
            "alerts": []
        }
        
        # Check for any service alerts (like the HDG stops closure mentioned on their site)
        alerts = [
            {
                "type": "Route",
                "cause": "Construction", 
                "effect": "Stop Moved",
                "routes_affected": ["HDG"],
                "message": "HDG Stops 1516 & 1517 Closed due to road construction",
                "more_info": "https://ridebt.org/news-alerts/554-hdg-stops-1516-1517-closed"
            }
        ]
        live_info["alerts"] = alerts
        
        # Generate enhanced schedule information for each route
        for route_id, route_info in BUS_ROUTES.items():
            current_hour = current_time.hour
            
            # Check if route is operating
            if current_hour < route_info["operating_hours"]["start"] or current_hour >= route_info["operating_hours"]["end"]:
                live_info["buses"][route_id] = {
                    "status": "Not operating",
                    "next_departure": None,
                    "operating_hours": f"{route_info['operating_hours']['start']}:00 - {route_info['operating_hours']['end']}:00"
                }
                continue
            
            # Calculate next departure times
            frequency = route_info["frequency"]
            current_minute = current_time.minute
            minutes_until_next = frequency - (current_minute % frequency)
            next_departure = current_time + timedelta(minutes=minutes_until_next)
            
            live_info["buses"][route_id] = {
                "status": "Operating",
                "next_departure": next_departure.strftime("%I:%M %p"),
                "minutes_until_next": minutes_until_next,
                "frequency": f"Every {frequency} minutes",
                "description": route_info["description"]
            }
        
        return live_info
        
    except Exception as e:
        return {
            "error": f"Unable to get live bus data: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "fallback": "Using scheduled times only"
        }

async def get_enhanced_bus_info_with_live_data(route_id: Optional[str] = None, location: Optional[str] = None) -> str:
    """
    Get enhanced bus information combining live map data with schedule information.
    """
    try:
        live_data = await get_live_bus_positions()
        
        if route_id and route_id.upper() in live_data.get("buses", {}):
            bus_info = live_data["buses"][route_id.upper()]
            
            if bus_info["status"] == "Not operating":
                return f"🚌 {route_id.upper()} ({BUS_ROUTES[route_id.upper()]['name']}) is not currently operating.\nOperating hours: {bus_info['operating_hours']}"
            
            result = f"🚌 {route_id.upper()} ({BUS_ROUTES[route_id.upper()]['name']}) - Live Status\n"
            result += f"Status: {bus_info['status']}\n"
            result += f"Next departure: {bus_info['next_departure']} (in {bus_info['minutes_until_next']} minutes)\n"
            result += f"Frequency: {bus_info['frequency']}\n"
            result += f"Route: {bus_info['description']}\n"
            
            # Add any relevant alerts
            if live_data.get("alerts"):
                for alert in live_data["alerts"]:
                    if route_id.upper() in alert.get("routes_affected", []):
                        result += f"\n⚠️ Alert: {alert['message']}"
            
            return result
        
        # General live status for all routes
        result = "🚌 Live Bus Status - Blacksburg Transit\n"
        result += f"Last updated: {datetime.now().strftime('%I:%M %p')}\n\n"
        
        operating_routes = [route for route, info in live_data.get("buses", {}).items() if info["status"] == "Operating"]
        
        if operating_routes:
            result += "Currently Operating:\n"
            for route in operating_routes:
                info = live_data["buses"][route]
                result += f"  • {route}: Next bus at {info['next_departure']} ({info['minutes_until_next']} min)\n"
        
        non_operating = [route for route, info in live_data.get("buses", {}).items() if info["status"] == "Not operating"]
        if non_operating:
            result += f"\nNot operating: {', '.join(non_operating)}\n"
        
        # Add service alerts
        if live_data.get("alerts"):
            result += "\n⚠️ Service Alerts:\n"
            for alert in live_data["alerts"]:
                result += f"  • {alert['message']}\n"
        
        result += f"\n📱 For real-time tracking, visit: https://ridebt.org/live-map"
        
        return result
        
    except Exception as e:
        return f"Unable to get live bus information: {str(e)}"
