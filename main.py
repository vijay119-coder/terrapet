import os
import sqlite3
import uuid
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
import requests
import pandas as pd
from io import StringIO

app = Flask(__name__, static_folder='static')

DATABASE = 'terrapets.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                xp INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_action TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def fetch_nasa_co2():
    try:
        url = 'https://data.giss.nasa.gov/global/co2/co2_annual.txt'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        lines = response.text.strip().split('\n')
        data_lines = lines[56:]
        
        if data_lines:
            last_line = data_lines[-1].strip().split()
            if len(last_line) >= 2:
                co2_ppm = float(last_line[1])
                return co2_ppm
    except Exception as e:
        print(f"Error fetching CO2 data: {e}")
    
    return 420.0

def fetch_nasa_temp():
    try:
        url = 'https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        df = pd.read_csv(StringIO(response.text), skiprows=1)
        
        if 'J-D' in df.columns and len(df) > 0:
            last_temp = df['J-D'].iloc[-1]
            return float(last_temp)
    except Exception as e:
        print(f"Error fetching temperature data: {e}")
    
    return 1.2

def calculate_mood(xp, co2, temp):
    base = xp // 20
    co2_penalty = max(0, (co2 - 400) / 5)
    temp_penalty = max(0, temp * 15)
    score = base - (co2_penalty + temp_penalty)
    
    if score >= 15:
        return 'joyful'
    elif score >= 8:
        return 'calm'
    elif score >= 2:
        return 'worried'
    else:
        return 'sad'

def get_form(xp):
    if xp >= 500:
        return 'dragon'
    elif xp >= 250:
        return 'tree'
    elif xp >= 100:
        return 'sprout'
    else:
        return 'seed'

def get_user_id():
    user_id = request.cookies.get('user_id')
    if not user_id:
        user_id = str(uuid.uuid4())
    return user_id

def get_or_create_user(user_id):
    with get_db() as conn:
        user = conn.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
        if not user:
            conn.execute(
                'INSERT INTO users (user_id, username, xp) VALUES (?, ?, ?)',
                (user_id, f'EcoWarrior_{user_id[:6]}', 0)
            )
            conn.commit()
            user = conn.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
    return dict(user)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/pet', methods=['GET'])
def get_pet():
    user_id = get_user_id()
    user = get_or_create_user(user_id)
    
    co2 = fetch_nasa_co2()
    temp = fetch_nasa_temp()
    
    xp = user['xp']
    mood = calculate_mood(xp, co2, temp)
    form = get_form(xp)
    
    response = jsonify({
        'xp': xp,
        'mood': mood,
        'form': form,
        'co2': round(co2, 2),
        'temp': round(temp, 2),
        'username': user['username']
    })
    response.set_cookie('user_id', user_id, max_age=31536000)
    
    return response

@app.route('/feed/<action>', methods=['POST'])
def feed_pet(action):
    user_id = get_user_id()
    user = get_or_create_user(user_id)
    
    action_xp = {
        'bike': 25,
        'recycle': 15,
        'plant': 30,
        'carpool': 20,
        'solar': 35,
        'compost': 18
    }
    
    xp_gain = action_xp.get(action, 10)
    
    with get_db() as conn:
        conn.execute(
            'UPDATE users SET xp = xp + ?, last_action = CURRENT_TIMESTAMP WHERE user_id = ?',
            (xp_gain, user_id)
        )
        conn.commit()
        
        user = conn.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
    
    co2 = fetch_nasa_co2()
    temp = fetch_nasa_temp()
    
    xp = user['xp']
    mood = calculate_mood(xp, co2, temp)
    form = get_form(xp)
    
    messages = {
        'bike': '💚 You biked instead of drove — TerraPet smiles!',
        'recycle': '♻️ Recycling makes the Earth cleaner!',
        'plant': '🌱 A new tree — TerraPet feels the oxygen!',
        'carpool': '🚗 Sharing rides saves energy!',
        'solar': '☀️ Solar power brightens TerraPet\'s day!',
        'compost': '🌿 Composting feeds the soil!'
    }
    
    response = jsonify({
        'xp': xp,
        'mood': mood,
        'form': form,
        'co2': round(co2, 2),
        'temp': round(temp, 2),
        'message': messages.get(action, '✨ Great eco-action!'),
        'xp_gain': xp_gain
    })
    response.set_cookie('user_id', user_id, max_age=31536000)
    
    return response

@app.route('/leaderboard', methods=['GET'])
def leaderboard():
    with get_db() as conn:
        top_users = conn.execute(
            'SELECT username, xp FROM users ORDER BY xp DESC LIMIT 10'
        ).fetchall()
    
    leaderboard_data = [
        {'username': user['username'], 'xp': user['xp']}
        for user in top_users
    ]
    
    return jsonify(leaderboard_data)

if __name__ == '__main__':
    init_db()
    print("🌍 TerraPet server starting...")
    print("🔗 NASA climate data integration active")
    app.run(host='0.0.0.0', port=5000, debug=False)
