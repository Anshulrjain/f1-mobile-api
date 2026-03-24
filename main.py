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
        
        # KEY CHANGE: Do NOT load the whole session first.
        # Just load the laps. This is much lighter on RAM.
        session.load(laps=True, telemetry=False, weather=False, messages=False)

        # Pick only the driver we need
        driver_laps = session.laps.pick_drivers(driver)
        if driver_laps.empty:
            return {"error": f"No data for {driver}"}

        fastest_lap = driver_laps.pick_fastest()
        
        # ONLY load telemetry for this one specific lap
        telemetry = fastest_lap.get_telemetry()

        # Slim down the data even more for the mobile app
        # We only need X, Y, and Speed. Time is converted to float.
        data = telemetry[['X', 'Y', 'Speed', 'Time']].copy()
        data['Time'] = data['Time'].dt.total_seconds()
        
        return {
            "driver": driver,
            "data": data.to_dict(orient="records")
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
