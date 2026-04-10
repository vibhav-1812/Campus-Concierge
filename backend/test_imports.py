#!/usr/bin/env python3

print("Testing imports...")

try:
    from nlu import parse_transit_query
    print("✅ nlu import successful")
    
    result = parse_transit_query("fastest route from Lavery Hall to Goodwin Hall")
    print(f"✅ Parsing works: {result}")
    
    from scrapers.bus import plan_quickest_route
    print("✅ bus scraper import successful")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
