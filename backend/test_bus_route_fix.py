#!/usr/bin/env python3

import os
from dotenv import load_dotenv
load_dotenv()

# Add current directory to path so we can import our modules
import sys
sys.path.append('.')

from scrapers.bus import enhanced_plan_quickest_route, find_nearest_stop

async def test_bus_route_fix():
    """Test the improved bus route detection"""
    
    print("🧪 Testing Improved Bus Route Detection\n")
    print("=" * 60)
    
    # Test the problematic queries
    test_cases = [
        ("Goodwin Hall", "Lavery Hall"),
        ("McComas Hall", "Virginia Tech, Blacksburg, VA"),
    ]
    
    for i, (origin, destination) in enumerate(test_cases, 1):
        print(f"\n{i}. Route: {origin} → {destination}")
        print("-" * 50)
        
        try:
            # Test stop detection
            origin_stop = find_nearest_stop(origin)
            dest_stop = find_nearest_stop(destination)
            print(f"📍 Origin stop: {origin_stop}")
            print(f"📍 Destination stop: {dest_stop}")
            
            # Test full route planning
            result = await enhanced_plan_quickest_route(origin, destination)
            print(f"✅ Route Result:\n{result.get('answer', 'No answer')[:300]}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_bus_route_fix())
