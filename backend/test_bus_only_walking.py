#!/usr/bin/env python3

import os
from dotenv import load_dotenv
load_dotenv()

# Add current directory to path so we can import our modules
import sys
sys.path.append('.')

from nlu import parse_transit_query
from scrapers.bus import enhanced_plan_quickest_route

async def test_bus_only_and_walking():
    """Test bus-only queries and enhanced walking directions"""
    
    print("🧪 Testing Bus-Only Queries & Enhanced Walking Directions\n")
    print("=" * 70)
    
    # Test queries
    test_queries = [
        "bus from Goodwin Hall to Lavery Hall",  # Should show only bus
        "how to get from Goodwin Hall to Lavery Hall using the bus",  # Should show only bus
        "take bus from McComas Hall to Squires",  # Should show only bus
        "how to get from Goodwin Hall to Lavery Hall",  # Should show walking + bus info
        "fastest route from D2 to Owens",  # Should show walking + bus info
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        print("-" * 50)
        
        try:
            # Test NLU parsing
            parsed = parse_transit_query(query)
            print(f"🔍 Parsed: {parsed}")
            
            # Test route planning
            if parsed.get("intent") == "transit_route" and parsed.get("destination"):
                origin = parsed.get("origin") or "Virginia Tech, Blacksburg, VA"
                destination = parsed["destination"]
                bus_only = parsed.get("bus_only", False)
                
                print(f"📍 Origin: {origin}")
                print(f"📍 Destination: {destination}")
                print(f"🚌 Bus Only: {bus_only}")
                
                result = await enhanced_plan_quickest_route(origin, destination, bus_only)
                print(f"✅ Result:\n{result.get('answer', 'No answer')[:400]}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_bus_only_and_walking())
