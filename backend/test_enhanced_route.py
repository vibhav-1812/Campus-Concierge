#!/usr/bin/env python3

import os
from dotenv import load_dotenv
load_dotenv()

# Add current directory to path so we can import our modules
import sys
sys.path.append('.')

from scrapers.bus import enhanced_plan_quickest_route, get_bus_schedule_for_route

async def test_enhanced_route():
    """Test enhanced route planning with bus schedule info"""
    
    print("🧪 Testing Enhanced Route Planning\n")
    print("=" * 60)
    
    test_routes = [
        ("Goodwin Hall", "Lavery Hall"),
        ("635 Prices Fork Rd, Blacksburg, VA 24061", "460 Old Turner St, Blacksburg, VA 24060"),
        ("Squires Student Center", "Torgersen Hall"),
    ]
    
    for i, (origin, destination) in enumerate(test_routes, 1):
        print(f"\n{i}. Route: {origin} → {destination}")
        print("-" * 50)
        
        try:
            result = await enhanced_plan_quickest_route(origin, destination)
            print(f"✅ Enhanced Route Result:")
            print(result.get('answer', 'No answer')[:300] + "..." if len(result.get('answer', '')) > 300 else result.get('answer', 'No answer'))
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_enhanced_route())
