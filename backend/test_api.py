#!/usr/bin/env python3

import requests
import json

def test_ask_endpoint():
    url = "http://localhost:8000/ask"
    headers = {"Content-Type": "application/json"}
    
    # Test the problematic query
    query = "fastest route from Lavery Hall to Goodwin Hall"
    data = {"query": query}
    
    print(f"Testing query: {query}")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            result = response.json()
            if "transit" in result["answer"].lower() or "route" in result["answer"].lower():
                print("✅ Transit query processed successfully!")
            else:
                print("❌ Query was not processed as transit")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_ask_endpoint()
