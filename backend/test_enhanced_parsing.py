#!/usr/bin/env python3

import os
from dotenv import load_dotenv
load_dotenv()

# Add current directory to path so we can import our modules
import sys
sys.path.append('.')

from nlu import parse_transit_query
from scrapers.bus import enhanced_next_bus_to, get_live_bus_schedule

def test_enhanced_queries():
    """Test the enhanced parsing and bus functions"""
    
    test_queries = [
        "fastest route to Goodwin Hall",
        "how to get to Goodwin Hall from 300 edgeway Blacksburg VA",
        "when is next CAS bus",
        "I am at Goodwin Hall right now, when is the next bus",
        "directions from Lavery Hall to Goodwin Hall",
        "travel from 300 edge way to prices fork road",
        "when does the CAS bus come",
        "next bus to squires",
    ]
    
    print("🧪 Testing Enhanced NLU Parsing and Bus Functions\n")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        print("-" * 50)
        
        # Test parsing
        parsed = parse_transit_query(query)
        print(f"✅ Parsed: {parsed}")
        
        # Test if it would be handled by transit logic
        if parsed.get("intent") in ("transit_route", "next_bus"):
            print("🚌 Would be handled by transit logic")
            
            if parsed.get("intent") == "next_bus":
                try:
                    # Test enhanced bus function
                    result = await enhanced_next_bus_to(
                        parsed.get("destination", "campus"),
                        parsed.get("origin"),
                        parsed.get("bus_route")
                    )
                    print(f"🚌 Bus result: {result.get('answer', 'No answer')[:100]}...")
                except Exception as e:
                    print(f"❌ Bus function error: {e}")
        else:
            print("❌ Would fall back to general AI")
        
        print()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_enhanced_queries())
