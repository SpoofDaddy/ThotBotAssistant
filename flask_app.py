from flask import Flask, render_template, request, jsonify
import os
import subprocess
import psutil
import json
import logging
from simp_tracker import SimpTracker

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('cherry-dashboard')

app = Flask(__name__)

# Initialize the simp tracker
simp_tracker = SimpTracker()

# Store the current personality mode
current_personality = "default"

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
                          simp_scores=simp_scores,
                          personality=current_personality)

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

@app.route('/api/personality', methods=['GET', 'POST'])
def api_personality():
    """API endpoint to get or set the bot personality"""
    global current_personality
    
    if request.method == 'POST':
        data = request.get_json()
        if data and 'personality' in data:
            new_personality = data['personality']
            if new_personality in ['default', 'tsundere', 'wholesome', 'spicy', 'yandere']:
                logger.info(f"Changing personality to: {new_personality}")
                current_personality = new_personality
                # Future implementation: Signal the bot to change personality
                return jsonify({
                    'success': True,
                    'personality': current_personality,
                    'message': f"Personality changed to {current_personality}"
                })
            else:
                return jsonify({
                    'success': False,
                    'message': "Invalid personality type"
                }), 400
        return jsonify({
            'success': False,
            'message': "Missing personality parameter"
        }), 400
    
    # GET request
    return jsonify({
        'personality': current_personality
    })

@app.route('/api/commands')
def api_commands():
    """API endpoint to get all available commands"""
    commands = [
        {
            'name': '!flirt',
            'description': 'Cherry will send you a flirty message 💋',
            'usage': '!flirt'
        },
        {
            'name': '!compliment',
            'description': 'Cherry will compliment you or someone you mention 💖',
            'usage': '!compliment [@user]'
        },
        {
            'name': '!simp',
            'description': 'Check how much you or someone else has been simping for Cherry 😘',
            'usage': '!simp [@user]'
        },
        {
            'name': '!helpme',
            'description': 'Shows all available commands 💌',
            'usage': '!helpme'
        }
    ]
    
    return jsonify({
        'commands': commands
    })

@app.route('/api/coming_soon')
def api_coming_soon():
    """API endpoint to get all coming soon features"""
    features = [
        {
            'name': 'Welcome Messages',
            'description': 'Flirty intros when users join the server',
            'icon': '👋'
        },
        {
            'name': 'Roleplay Commands',
            'description': '!kiss, !hug, !pat, and more interactions with custom replies',
            'icon': '💏'
        },
        {
            'name': 'Memory System',
            'description': 'Cherry will remember past interactions with users',
            'icon': '🧠'
        },
        {
            'name': 'User Nicknames',
            'description': 'Cherry gives flirty pet names to repeat users',
            'icon': '📝'
        }
    ]
    
    return jsonify({
        'coming_soon': features
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)