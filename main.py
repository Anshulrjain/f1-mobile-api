import os
from fastapi import FastAPI
import fastf1
import uvicorn

app = FastAPI()

# FIX: Create the cache directory if it doesn't exist
CACHE_DIR = 'cache'
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# Enable caching using the folder we just checked/created
fastf1.Cache.enable_cache(CACHE_DIR) 

@app.get("/")
def home():
    return {"status": "F1 API is Online", "message": "Ready for telemetry requests"}

# ... rest of your code ...

@app.get("/race-data")
def get_race_telemetry(year: int, location: str, session_type: str, driver: str):
    try:
        session = fastf1.get_session(year, location, session_type)
        session.load()

        laps = session.laps.pick_driver(driver)
        fastest_lap = laps.pick_fastest()
        telemetry = fastest_lap.get_telemetry()

        data = telemetry[['X', 'Y', 'Speed', 'Time']].copy()
        data['Time'] = data['Time'].dt.total_seconds() 
        
        return {
            "driver": driver,
            "session": f"{year} {location}",
            "data": data.to_dict(orient="records")
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    # Render uses the PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
