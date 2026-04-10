#!/usr/bin/env python3

import os
from dotenv import load_dotenv
load_dotenv()

# Add current directory to path so we can import our modules
import sys
sys.path.append('.')

from nlu import parse_transit_query, simple_parse, nvidia_nim_parse

def test_query(query):
    print(f"\n=== Testing: '{query}' ===")
    
    # Test simple parsing
    simple_result = simple_parse(query)
    print(f"Simple parse: {simple_result}")
    
    # Test NVIDIA NIMs parsing
    nvidia_result = nvidia_nim_parse(query)
    print(f"NVIDIA NIMs parse: {nvidia_result}")
    
    # Test full parsing
    full_result = parse_transit_query(query)
    print(f"Full parse: {full_result}")
    
    return full_result

if __name__ == "__main__":
    # Test the problematic query
    test_query("fastest route from 300 edge way Blacksburg Virginia to prices Fork Road Blacksburg")
    
    # Test a simpler campus query
    test_query("fastest route from Lavery Hall to Goodwin Hall")
    
    # Test another pattern
    test_query("quickest way from 300 edge way to prices fork road")
