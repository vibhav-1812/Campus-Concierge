"""
HokieAssist FastAPI application: REST API for chat, transit, dining, buses, and clubs.
See IMPLEMENTATION.md and docs/AI_USAGE_LOG.md for milestone and AI-disclosure notes.
Purpose:
- Central API layer that routes user queries to the correct service
- Handles transit, dining, clubs, and general AI queries
- Integrates NLU + external APIs (Google Maps, BT, scrapers)                                  
"""
import io
import shutil
import subprocess
import tempfile
from typing import List, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
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
    sources: List[str]

class BusQuery(BaseModel):
    query: str
    origin: Optional[str] = None

@app.get("/")
async def root():
    google_key_status = "set" if os.getenv("GOOGLE_MAPS_API_KEY") else "not_set"
    nvidia_key_status = "set" if os.getenv("NVIDIA_NIM_API_KEY") else "not_set"
    return {
        "message": "HokieAssist API is running.",
        "google_maps_key": google_key_status,
        "nvidia_nim_key": nvidia_key_status,
    }


def _transcribe_with_google(audio_bytes: bytes) -> str:
    """Free Google Speech Recognition via the SpeechRecognition library (no API key needed)."""
    import speech_recognition as sr

    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    audio_file = io.BytesIO(audio_bytes)
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
    try:
        return str(recognizer.recognize_google(audio_data))
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        raise RuntimeError(
            f"Could not reach Google speech service from the server ({e}). "
            "Check server internet access or set a real OPENAI_API_KEY for Whisper."
        ) from e


def _transcribe_with_openai(audio_bytes: bytes, filename: str) -> str:
    """OpenAI Whisper transcription (requires OPENAI_API_KEY)."""
    from openai import OpenAI

    api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    client = OpenAI(api_key=api_key)
    buf = io.BytesIO(audio_bytes)
    buf.name = filename
    result = client.audio.transcriptions.create(model="whisper-1", file=buf)
    return (getattr(result, "text", None) or "").strip()


def _convert_webm_to_wav(raw: bytes) -> bytes:
    """Convert browser-recorded audio (webm/opus, mp4, etc.) to 16 kHz mono WAV for SpeechRecognition."""
    ffmpeg_bin = shutil.which("ffmpeg")
    if not ffmpeg_bin:
        raise RuntimeError(
            "ffmpeg is not installed or not on PATH. Install it (e.g. brew install ffmpeg) and restart the backend."
        )

    fd_in, tmp_in_path = tempfile.mkstemp(suffix=".webm")
    fd_out, tmp_out_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd_in)
    os.close(fd_out)
    try:
        with open(tmp_in_path, "wb") as f:
            f.write(raw)
        proc = subprocess.run(
            [
                ffmpeg_bin,
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                tmp_in_path,
                "-ar",
                "16000",
                "-ac",
                "1",
                "-f",
                "wav",
                tmp_out_path,
            ],
            capture_output=True,
            timeout=30,
            check=False,
        )
        if proc.returncode != 0:
            err = (proc.stderr or b"").decode("utf-8", errors="replace").strip()
            raise RuntimeError(err or f"ffmpeg exited with code {proc.returncode}")
        with open(tmp_out_path, "rb") as f:
            return f.read()
    finally:
        for p in (tmp_in_path, tmp_out_path):
            try:
                os.unlink(p)
            except OSError:
                pass


@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Speech-to-text endpoint. Uses OpenAI Whisper if OPENAI_API_KEY is set, otherwise falls back to
    free Google Speech Recognition via the SpeechRecognition library (no key needed).
    """
    raw = await file.read()
    if len(raw) < 64:
        raise HTTPException(status_code=400, detail="Audio clip is empty or too short.")

    openai_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    has_openai = openai_key and openai_key != "your-openai-api-key-here"

    if has_openai:
        try:
            text = _transcribe_with_openai(raw, file.filename or "speech.webm")
            return {"text": text}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"OpenAI transcription failed: {e}")

    try:
        wav_bytes = _convert_webm_to_wav(raw)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Audio conversion failed (install ffmpeg and ensure it is on PATH): {e}",
        )

    try:
        text = _transcribe_with_google(wav_bytes)
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google speech recognition failed: {e}")

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
