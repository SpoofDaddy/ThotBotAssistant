from flask import Flask, render_template, request, jsonify
import os
import subprocess
import psutil
import json
from simp_tracker import SimpTracker

app = Flask(__name__)

# Initialize the simp tracker
simp_tracker = SimpTracker()

def is_bot_running():
    """Check if the bot process is running"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Check if this is a Python process running main.py
            if proc.info['name'] == 'python' and any('main.py' in cmd for cmd in proc.info['cmdline'] if cmd):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

@app.route('/')
def index():
    """Main dashboard page"""
    # Check if the bot is running
    bot_status = is_bot_running()
    
    # Get top simps
    simp_scores = simp_tracker.get_top_simps(10)
    
    return render_template('index.html', 
                          bot_status=bot_status,
                          simp_scores=simp_scores)

@app.route('/api/status')
def api_status():
    """API endpoint to check bot status"""
    return jsonify({
        'status': 'online' if is_bot_running() else 'offline'
    })

@app.route('/api/top_simps')
def api_top_simps():
    """API endpoint to get top simps"""
    limit = request.args.get('limit', 10, type=int)
    simp_scores = simp_tracker.get_top_simps(limit)
    
    return jsonify({
        'top_simps': [{'user_id': user_id, 'score': score} for user_id, score in simp_scores]
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)