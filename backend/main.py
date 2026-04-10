"""
HokieAssist FastAPI application: REST API for chat, transit, dining, buses, and clubs.
See IMPLEMENTATION.md and docs/AI_USAGE_LOG.md for milestone and AI-disclosure notes.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv
from langchain_agent import get_ai_response
from scrapers.dining import get_dining_halls
from scrapers.bus import get_bus_times, enhanced_next_bus_to, get_live_bus_schedule, enhanced_plan_quickest_route, get_enhanced_bus_info_with_live_data
from scrapers.clubs import get_club_events
from nlu import parse_transit_query

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="HokieAssist API", version="1.0.0")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    sources: list[str]

class BusQuery(BaseModel):
    query: str
    origin: str | None = None

@app.get("/")
async def root():
    google_key_status = "set" if os.getenv("GOOGLE_MAPS_API_KEY") else "not_set"
    nvidia_key_status = "set" if os.getenv("NVIDIA_NIM_API_KEY") else "not_set"
    return {
        "message": "HokieAssist API is running.",
        "google_maps_key": google_key_status,
        "nvidia_nim_key": nvidia_key_status
    }

@app.get("/debug/parse/{query}")
async def debug_parse(query: str):
    """Debug endpoint to test query parsing"""
    from nlu import parse_transit_query
    result = parse_transit_query(query)
    return {"query": query, "parsed": result}

@app.post("/bus/query")
async def bus_query(q: BusQuery):
    """
    Dedicated endpoint for bus/transit queries with Google Maps integration.
    """
    try:
        parsed = parse_transit_query(q.query)
        origin = q.origin or parsed.get("origin") or "Virginia Tech, Blacksburg, VA"
        destination = parsed.get("destination")
        intent = parsed.get("intent")
        
        if destination and intent == "transit_route":
            bus_only = parsed.get("bus_only", False)
            return await enhanced_plan_quickest_route(origin, destination, bus_only)  # type: ignore
        if intent == "next_bus":
            parsed_route = parsed.get("bus_route")
            return await enhanced_next_bus_to(destination or "campus", origin, parsed_route)  # type: ignore
        
        return {
            "answer": "Please specify destination (and origin if needed). Try asking 'What's the quickest way from Lavery Hall to Goodwin Hall?' or 'When is the next bus to Goodwin Hall?'",
            "sources": ["https://maps.google.com", "https://ridebt.org/"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error planning route: {str(e)}")

@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """
    Main endpoint for campus queries: transit intent is handled via NLU + Maps/BT integrations;
    other topics use keyword routing to live scrapers (see langchain_agent.py).
    """
    try:
        parsed = parse_transit_query(request.query)
        
        if parsed.get("intent") in ("transit_route", "next_bus") and parsed.get("destination"):
            origin = parsed.get("origin") or "Virginia Tech, Blacksburg, VA"
            destination = parsed["destination"]
            bus_route = parsed.get("bus_route")
            
            bus_only = parsed.get("bus_only", False)
            plan = await (enhanced_plan_quickest_route(origin, destination, bus_only) if parsed["intent"] == "transit_route"
                         else enhanced_next_bus_to(destination, origin, bus_route))  # type: ignore
            return QueryResponse(answer=plan["answer"], sources=plan.get("sources", []))
        
        if parsed.get("intent") == "next_bus" and not parsed.get("destination"):
            origin = parsed.get("origin") or "Virginia Tech, Blacksburg, VA"
            bus_route = parsed.get("bus_route")
            
            if bus_route:
                live_info = await get_enhanced_bus_info_with_live_data(bus_route, origin)
                return QueryResponse(answer=live_info, sources=["https://ridebt.org/live-map"])
            else:
                plan = await get_live_bus_schedule(bus_route, origin)  # type: ignore
                return QueryResponse(answer=plan["answer"], sources=plan.get("sources", []))
        
        if parsed.get("intent") == "generic" and any(word in request.query.lower() for word in ["buses", "bus", "running", "live", "status", "routes"]):
            live_info = await get_enhanced_bus_info_with_live_data()
            return QueryResponse(answer=live_info, sources=["https://ridebt.org/live-map"])
        
        result = await get_ai_response(request.query)
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/dining")
async def get_dining_status():
    """
    Get current dining hall status from Virginia Tech dining services.
    """
    try:
        dining_data = await get_dining_halls()
        return {
            "dining_halls": dining_data,
            "sources": ["https://udc.vt.edu/"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dining data: {str(e)}")

@app.get("/bus")
async def get_bus_status():
    """
    Get current bus times from Blacksburg Transit.
    """
    try:
        bus_data = await get_bus_times()
        return {
            "bus_times": bus_data,
            "sources": ["https://ridebt.org/"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching bus data: {str(e)}")

@app.get("/clubs")
async def get_clubs_events():
    """
    Get upcoming club events from Gobbler Connect.
    """
    try:
        events_data = await get_club_events()
        return {
            "events": events_data,
            "sources": ["https://gobblerconnect.vt.edu/"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching club events: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
