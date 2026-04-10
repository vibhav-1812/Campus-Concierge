"""
General-purpose query path for HokieAssist (legacy module name).

LangChain is not used here; this module routes non-transit questions to scrapers via
keywords. Generative-AI tooling assisted early drafts; see docs/AI_USAGE_LOG.md.
"""
from typing import Dict, Any

from scrapers.dining import get_dining_halls
from scrapers.bus import get_bus_times
from scrapers.clubs import get_club_events


async def get_ai_response(query: str) -> Dict[str, Any]:
    """
    Resolve a natural-language query by fetching live campus data when keywords match.
    """
    try:
        return await get_simple_response(query)

    except Exception:
        fallback_response = f"I'm sorry, I encountered an issue processing your question about '{query}'. "
        fallback_response += "Please try rephrasing your question or check the Virginia Tech website directly."

        return {
            "answer": fallback_response,
            "sources": ["https://vt.edu/"]
        }


async def get_simple_response(query: str) -> Dict[str, Any]:
    """
    Call dining, bus, and club scrapers based on simple keyword presence in the query.
    """
    query_lower = query.lower()
    sources = []
    answer_parts = []

    if any(keyword in query_lower for keyword in ['dining', 'food', 'meal', 'eat', 'restaurant', 'open']):
        try:
            dining_data = await get_dining_halls()
            answer_parts.append(f"Dining Information: {dining_data}")
            sources.append("https://udc.vt.edu/")
        except Exception:
            answer_parts.append("Sorry, I couldn't fetch current dining information.")

    if any(keyword in query_lower for keyword in ['bus', 'transport', 'transit', 'ride']):
        try:
            bus_data = await get_bus_times()
            answer_parts.append(f"Bus Information: {bus_data}")
            sources.append("https://ridebt.org/")
        except Exception:
            answer_parts.append("Sorry, I couldn't fetch current bus information.")

    if any(keyword in query_lower for keyword in ['club', 'event', 'activity', 'social']):
        try:
            events_data = await get_club_events()
            answer_parts.append(f"Club Events: {events_data}")
            sources.append("https://gobblerconnect.vt.edu/")
        except Exception:
            answer_parts.append("Sorry, I couldn't fetch current club events.")

    if not answer_parts:
        answer_parts.append(
            "I can help you with dining, transportation, and club events at Virginia Tech. Please ask about specific topics!"
        )
        sources = ["https://vt.edu/"]

    return {
        "answer": " ".join(answer_parts),
        "sources": sources
    }
