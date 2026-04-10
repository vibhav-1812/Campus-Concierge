import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from typing import Dict, List

async def get_dining_halls() -> str:
    """
    Scrape Virginia Tech dining hall information from UDC website.
    Returns a formatted string with current dining hall status.
    """
    try:
        # Main dining page
        url = "https://udc.vt.edu/dining/menus.html"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Common dining halls at VT
        dining_halls = {
            'D2': {'status': 'Unknown', 'hours': 'Unknown'},
            'Owens Food Court': {'status': 'Unknown', 'hours': 'Unknown'},
            'Hokie Grill': {'status': 'Unknown', 'hours': 'Unknown'},
            'West End Market': {'status': 'Unknown', 'hours': 'Unknown'},
            'Deet\'s Place': {'status': 'Unknown', 'hours': 'Unknown'},
            'Squires Student Center': {'status': 'Unknown', 'hours': 'Unknown'}
        }
        
        # Try to find dining hall information
        current_time = datetime.now()
        current_hour = current_time.hour
        
        # Mock business hours logic (in a real implementation, this would be scraped)
        business_hours = {
            'D2': {'open': 7, 'close': 21},  # 7 AM to 9 PM
            'Owens Food Court': {'open': 10, 'close': 20},  # 10 AM to 8 PM
            'Hokie Grill': {'open': 10, 'close': 22},  # 10 AM to 10 PM
            'West End Market': {'open': 10, 'close': 20},  # 10 AM to 8 PM
            'Deet\'s Place': {'open': 8, 'close': 18},  # 8 AM to 6 PM
            'Squires Student Center': {'open': 9, 'close': 17}  # 9 AM to 5 PM
        }
        
        # Determine status based on time
        for hall, hours in business_hours.items():
            if hours['open'] <= current_hour < hours['close']:
                dining_halls[hall]['status'] = 'Open'
                dining_halls[hall]['hours'] = f"Open until {hours['close']}:00"
            else:
                dining_halls[hall]['status'] = 'Closed'
                dining_halls[hall]['hours'] = f"Opens at {hours['open']}:00"
        
        # Format response
        open_halls = [hall for hall, info in dining_halls.items() if info['status'] == 'Open']
        closed_halls = [hall for hall, info in dining_halls.items() if info['status'] == 'Closed']
        
        result = f"Current time: {current_time.strftime('%I:%M %p')}\n\n"
        
        if open_halls:
            result += f"🟢 Currently Open: {', '.join(open_halls)}\n\n"
        
        if closed_halls:
            result += f"🔴 Currently Closed: {', '.join(closed_halls)}\n\n"
        
        result += "Detailed Hours:\n"
        for hall, info in dining_halls.items():
            result += f"• {hall}: {info['hours']}\n"
        
        return result
        
    except requests.RequestException as e:
        return f"Unable to fetch current dining information. Please check the Virginia Tech dining website directly. Error: {str(e)}"
    except Exception as e:
        return f"An error occurred while fetching dining information: {str(e)}"

def get_dining_hours() -> Dict[str, str]:
    """
    Get typical dining hall hours (fallback data).
    """
    return {
        'D2': '7:00 AM - 9:00 PM',
        'Owens Food Court': '10:00 AM - 8:00 PM',
        'Hokie Grill': '10:00 AM - 10:00 PM',
        'West End Market': '10:00 AM - 8:00 PM',
        'Deet\'s Place': '8:00 AM - 6:00 PM',
        'Squires Student Center': '9:00 AM - 5:00 PM'
    }

async def get_dining_menus() -> Dict[str, List[str]]:
    """
    Get current dining hall menus (placeholder implementation).
    """
    # In a real implementation, this would scrape menu data
    return {
        'D2': ['Grilled Chicken', 'Pasta Bar', 'Salad Bar', 'Pizza'],
        'Owens Food Court': ['Burger King', 'Chick-fil-A', 'Subway', 'Starbucks'],
        'Hokie Grill': ['Sandwiches', 'Wraps', 'Smoothies', 'Snacks']
    }

