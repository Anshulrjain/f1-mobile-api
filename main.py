import os
from fastapi import FastAPI
import fastf1
import uvicorn

app = FastAPI()

# Setup Cache
CACHE_DIR = 'cache'
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)
fastf1.Cache.enable_cache(CACHE_DIR)

@app.get("/")
def home():
    return {"status": "Online"}

@app.get("/race-data")
def get_race_telemetry(year: int, location: str, session_type: str, driver: str):
    try:
        session = fastf1.get_session(year, location, session_type)
        
        # 1. We load LAPS (very light) and TELEMETRY (but we filter it later)
        # We MUST keep telemetry=True here, but we set weather/messages to False
        session.load(laps=True, telemetry=True, weather=False, messages=False)

        # 2. Pick only the driver we want
        laps = session.laps.pick_drivers(driver)
        if laps.empty:
            return {"error": f"No data for driver {driver}"}

        # 3. Get the fastest lap
        fastest_lap = laps.pick_fastest()
        
        # 4. Extract the telemetry for just this lap
        telemetry = fastest_lap.get_telemetry()

        # 5. Clean and slim the data for Kotlin
        data = telemetry[['X', 'Y', 'Speed', 'Time']].copy()
        data['Time'] = data['Time'].dt.total_seconds() 
        
        return {
            "driver": driver,
            "session": f"{year} {location}",
            "data": data.to_dict(orient="records")
        }
    except Exception as e:
        # This will help us see exactly what went wrong in the browser
        return {"error": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
