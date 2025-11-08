# TerraPet - Sentient Eco-Companion

## Overview
TerraPet is a Tamagotchi-style web application that creates an emotional connection between users and environmental action. The digital pet evolves based on user eco-actions and responds to real-time NASA climate data, making sustainability awareness engaging and interactive.

## Project Status
- **Created**: November 8, 2025
- **Status**: MVP Complete
- **Tech Stack**: Python 3.11, Flask 2.3.3, p5.js, SQLite

## Key Features
1. **Animated Pet Evolution**: Four distinct forms (Seed → Sprout → Tree → Dragon) based on XP thresholds
2. **Dynamic Mood System**: Pet's emotional state calculated from user XP and NASA climate data
3. **Real NASA Data Integration**: Live CO₂ and temperature anomaly data with automatic fallbacks
4. **Eco-Action Rewards**: Six interactive actions that award XP (bike, recycle, plant, carpool, solar, compost)
5. **Global Leaderboard**: Top 10 "Planet Parents" ranked by eco-impact
6. **Auto-refresh**: Pet state updates every 10 seconds, leaderboard every 15 seconds

## Architecture

### Backend (main.py)
- Flask server on port 5000
- SQLite database for persistent user profiles
- NASA data fetching with fallback values
- Emotion calculation algorithm
- RESTful API routes

### Frontend (static/index.html)
- p5.js canvas animations with custom pet drawings
- Vanilla JavaScript for interactivity
- Responsive CSS with dark navy theme
- Google Fonts (Fredoka One, Poppins)

### Database Schema
```sql
users (
  user_id TEXT PRIMARY KEY,
  username TEXT,
  xp INTEGER DEFAULT 0,
  created_at TIMESTAMP,
  last_action TIMESTAMP
)
```

## Evolution System
- **Seed** (🌱): 0-99 XP - Starting form
- **Sprout** (🌿): 100-249 XP - Growing with leaves
- **Tree** (🌳): 250-499 XP - Full foliage
- **Dragon** (🐉): 500+ XP - Ultimate eco-warrior

## Mood Calculation
```python
base = XP // 20
co2_penalty = max(0, (CO2 - 400) / 5)
temp_penalty = max(0, temp * 15)
score = base - (co2_penalty + temp_penalty)

Moods:
- Joyful 😄: score ≥ 15
- Calm 🙂: score ≥ 8
- Worried 😟: score ≥ 2
- Sad 😢: score < 2
```

## NASA Data Integration
- **CO₂ Source**: https://data.giss.nasa.gov/global/co2/co2_annual.txt (Fallback: 420.0 ppm)
- **Temperature Source**: https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv (Fallback: 1.2°C)
- Note: NASA data URLs may occasionally be unavailable; fallback values ensure app stability

## Running the Project
```bash
python main.py
```
Server starts on http://0.0.0.0:5000

## Recent Changes
- November 8, 2025: Initial MVP implementation
  - Created Flask backend with NASA data integration
  - Built p5.js frontend with animated pet forms
  - Implemented SQLite database for user persistence
  - Added global leaderboard functionality
  - Configured workflow for automatic server start

## Future Enhancements (v2)
- User accounts with persistent login
- Achievement badges and milestone rewards
- Pet customization (names, accessories, themes)
- Historical climate data visualizations
- PWA features with offline support
- Push notifications for daily eco-reminders
- Social sharing of achievements
