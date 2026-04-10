#!/usr/bin/env python3

import os
from dotenv import load_dotenv
load_dotenv()

# Add current directory to path so we can import our modules
import sys
sys.path.append('.')

from nlu import parse_transit_query
from scrapers.bus import get_enhanced_bus_info_with_live_data, enhanced_plan_quickest_route

async def test_comprehensive_campus():
    """Test comprehensive campus location recognition and live bus features"""
    
    print("🧪 Testing Comprehensive Campus Recognition & Live Bus Features\n")
    print("=" * 80)
    
    # Test various campus location queries
    test_queries = [
        # Basic campus buildings
        "how to get from Goodwin Hall to Lavery Hall using the bus",
        "when is next bus to Squires",
        "fastest route from Torgersen to Newman Library",
        
        # Dining halls
        "how to get from D2 to Owens Food Court",
        "when is next bus to Turner Place",
        "route from Hokie Grill to campus",
        
        # Residential halls
        "how to get from Barringer Hall to Johnson Hall",
        "when is next bus from Slusher Hall",
        "fastest route to Vawter Hall",
        
        # Off-campus areas
        "how to get from Main Street to campus",
        "when is next CRC bus",
        "route from Harding Avenue to downtown",
        
        # Sports facilities
        "how to get from Lane Stadium to Cassell Coliseum",
        "when is next bus to English Field",
        
        # Specific bus routes
        "when is next CAS bus",
        "CAS schedule",
        "when does HDG bus come",
        "TCP bus times",
        "HXP express schedule",
        
        # General queries
        "what buses are running now",
        "live bus status",
        "all bus routes",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        print("-" * 60)
        
        try:
            # Test NLU parsing
            parsed = parse_transit_query(query)
            print(f"🔍 Parsed: {parsed}")
            
            # Test specific bus route queries
            if any(route in query.upper() for route in ["CAS", "HDG", "TCP", "HXP", "CRC", "NMP", "SME", "TTT", "UCB", "HWC"]):
                print(f"🚌 Testing live bus info...")
                route_match = None
                for route in ["CAS", "HDG", "TCP", "HXP", "CRC", "NMP", "SME", "TTT", "UCB", "HWC"]:
                    if route in query.upper():
                        route_match = route
                        break
                
                if route_match:
                    live_info = await get_enhanced_bus_info_with_live_data(route_match)
                    print(f"✅ Live Bus Info:\n{live_info[:200]}...")
            
            # Test route planning for location queries
            elif parsed.get("intent") == "transit_route" and parsed.get("origin") and parsed.get("destination"):
                print(f"🗺️ Testing route planning...")
                route_result = await enhanced_plan_quickest_route(parsed["origin"], parsed["destination"])
                print(f"✅ Route Result:\n{route_result.get('answer', 'No answer')[:200]}...")
            
            print("✅ Query processed successfully")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

    # Test live bus status for all routes
    print("\n" + "=" * 80)
    print("🚌 Testing Live Bus Status for All Routes")
    print("=" * 80)
    
    try:
        live_status = await get_enhanced_bus_info_with_live_data()
        print(f"✅ Live Status:\n{live_status[:300]}...")
    except Exception as e:
        print(f"❌ Error getting live status: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_comprehensive_campus())
