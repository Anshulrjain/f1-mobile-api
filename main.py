from fastapi import FastAPI
import fastf1
import pandas as pd
import os # <-- Added for Render port detection

app = FastAPI()

# Enable caching
fastf1.Cache.enable_cache('cache') 

# 1. Health Check (Very helpful to see if Render is awake)
@app.get("/")
def home():
    return {"status": "F1 API is Online", "message": "Ready for telemetry requests"}

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