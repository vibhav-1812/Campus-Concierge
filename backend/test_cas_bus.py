#!/usr/bin/env python3

import os
from dotenv import load_dotenv
load_dotenv()

# Add current directory to path so we can import our modules
import sys
sys.path.append('.')

from nlu import parse_transit_query
from scrapers.bus import get_live_bus_schedule

async def test_cas_bus():
    """Test CAS bus specific queries"""
    
    print("🧪 Testing CAS Bus Queries\n")
    print("=" * 60)
    
    test_queries = [
        "when is next CAS bus",
        "CAS schedule",
        "when does the CAS bus come",
        "CAS bus next",
        "when is next CAS",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        print("-" * 50)
        
        # Test parsing
        parsed = parse_transit_query(query)
        print(f"✅ Parsed: {parsed}")
        
        # Test CAS bus schedule
        if parsed.get("bus_route") == "CAS":
            print("🚌 CAS bus route detected!")
            try:
                result = await get_live_bus_schedule("CAS")
                print(f"🚌 CAS Schedule: {result.get('answer', 'No answer')}")
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print("❌ CAS route not detected")
        
        print()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_cas_bus())
