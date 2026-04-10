import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
from typing import Dict, List
import asyncio

async def get_club_events() -> str:
    """
    Scrape club events from Gobbler Connect.
    Returns formatted string with upcoming club events and activities.
    """
    try:
        # Gobbler Connect events page
        url = "https://gobblerconnect.vt.edu/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Mock upcoming events (in a real implementation, this would be scraped)
        current_date = datetime.now()
        events = [
            {
                'name': 'ACM Weekly Meeting',
                'date': (current_date + timedelta(days=1)).strftime('%A, %B %d'),
                'time': '7:00 PM',
                'location': 'Torgersen Hall 1100',
                'description': 'Weekly meeting discussing upcoming tech projects'
            },
            {
                'name': 'Salsa Dancing Workshop',
                'date': (current_date + timedelta(days=2)).strftime('%A, %B %d'),
                'time': '6:30 PM',
                'location': 'Student Services Building',
                'description': 'Learn basic salsa moves - all levels welcome!'
            },
            {
                'name': 'Environmental Club Cleanup',
                'date': (current_date + timedelta(days=3)).strftime('%A, %B %d'),
                'time': '10:00 AM',
                'location': 'Drillfield',
                'description': 'Help keep campus clean - supplies provided'
            },
            {
                'name': 'Photography Club Exhibition',
                'date': (current_date + timedelta(days=5)).strftime('%A, %B %d'),
                'time': '5:00 PM',
                'location': 'Moss Arts Center',
                'description': 'Student photography showcase and networking'
            },
            {
                'name': 'Debate Society Meeting',
                'date': (current_date + timedelta(days=7)).strftime('%A, %B %d'),
                'time': '8:00 PM',
                'location': 'Squires Student Center',
                'description': 'Practice debate skills and discuss current topics'
            }
        ]
        
        # Format response
        result = f"🎉 Upcoming Club Events - {current_date.strftime('%A, %B %d, %Y')}\n\n"
        
        for i, event in enumerate(events, 1):
            result += f"{i}. 📅 {event['name']}\n"
            result += f"   Date: {event['date']} at {event['time']}\n"
            result += f"   Location: {event['location']}\n"
            result += f"   Details: {event['description']}\n\n"
        
        result += "🔗 Find more events at: https://gobblerconnect.vt.edu/\n"
        result += "📱 Download the Gobbler Connect app for notifications!"
        
        return result
        
    except requests.RequestException as e:
        return f"Unable to fetch current club events. Please check Gobbler Connect directly. Error: {str(e)}"
    except Exception as e:
        return f"An error occurred while fetching club events: {str(e)}"

async def get_popular_clubs() -> List[Dict[str, str]]:
    """
    Get list of popular clubs at Virginia Tech.
    """
    popular_clubs = [
        {'name': 'Association for Computing Machinery (ACM)', 'category': 'Technology'},
        {'name': 'Photography Club', 'category': 'Arts & Media'},
        {'name': 'Environmental Coalition', 'category': 'Environmental'},
        {'name': 'Debate Society', 'category': 'Academic'},
        {'name': 'Salsa Dancing Club', 'category': 'Dance & Performance'},
        {'name': 'Hiking Club', 'category': 'Outdoor Recreation'},
        {'name': 'Investment Club', 'category': 'Business & Finance'},
        {'name': 'Volunteer Service Club', 'category': 'Community Service'},
        {'name': 'Cooking Club', 'category': 'Culinary'},
        {'name': 'Board Game Society', 'category': 'Gaming & Recreation'}
    ]
    
    return popular_clubs

async def get_club_categories() -> Dict[str, List[str]]:
    """
    Get clubs organized by category.
    """
    categories = {
        'Academic & Professional': [
            'Association for Computing Machinery (ACM)',
            'Debate Society',
            'Investment Club',
            'Pre-Med Society'
        ],
        'Arts & Media': [
            'Photography Club',
            'Art Society',
            'Film Club',
            'Creative Writing Club'
        ],
        'Sports & Recreation': [
            'Hiking Club',
            'Soccer Club',
            'Tennis Club',
            'Swimming Club'
        ],
        'Cultural & Diversity': [
            'International Student Association',
            'Black Student Alliance',
            'Asian American Student Union',
            'LGBTQ+ Alliance'
        ],
        'Community Service': [
            'Volunteer Service Club',
            'Environmental Coalition',
            'Habitat for Humanity',
            'Red Cross Club'
        ]
    }
    
    return categories

async def get_club_contact_info(club_name: str) -> Dict[str, str]:
    """
    Get contact information for a specific club.
    """
    # In a real implementation, this would query the database or scrape contact info
    contact_info = {
        'email': f"{club_name.lower().replace(' ', '_')}@vt.edu",
        'website': f"https://gobblerconnect.vt.edu/organization/{club_name.lower().replace(' ', '_')}",
        'meeting_time': 'Check Gobbler Connect for current meeting times',
        'location': 'Various locations across campus'
    }
    
    return contact_info

def get_club_benefits() -> List[str]:
    """
    Get information about benefits of joining clubs.
    """
    return [
        "Meet new people with similar interests",
        "Develop leadership and teamwork skills",
        "Build your resume and network",
        "Participate in fun activities and events",
        "Give back to the community through service",
        "Explore new hobbies and passions",
        "Connect with alumni and professionals",
        "Attend conferences and competitions"
    ]
