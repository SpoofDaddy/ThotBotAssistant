from flask import Flask, render_template, request, jsonify
import os
import subprocess
import psutil
import json
import logging
from simp_tracker import SimpTracker
from responses import PERSONALITY_TYPES, DEFAULT_PERSONALITY
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('cherry-dashboard')

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize the simp tracker
simp_tracker = SimpTracker()

# Store the current personality mode from environment or default
current_personality = os.environ.get("CURRENT_PERSONALITY", DEFAULT_PERSONALITY)

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
    
    # Get upcoming features for the dashboard
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
    
    return render_template('index.html', 
                          bot_status=bot_status,
                          simp_scores=simp_scores,
                          current_personality=current_personality,
                          personalities=PERSONALITY_TYPES,
                          coming_soon=features)

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
            if new_personality in PERSONALITY_TYPES:
                logger.info(f"Changing personality to: {new_personality}")
                # Update the current personality
                current_personality = new_personality
                
                try:
                    # Set environment variable to persist across restarts
                    os.environ["CURRENT_PERSONALITY"] = new_personality
                    
                    # Also update the environment file for persistence across reboots
                    env_path = os.path.join(os.path.dirname(__file__), '.env')
                    
                    # Read existing .env file
                    env_content = ""
                    personality_line_found = False
                    
                    if os.path.exists(env_path):
                        with open(env_path, 'r') as env_file:
                            lines = env_file.readlines()
                            for line in lines:
                                if line.startswith('CURRENT_PERSONALITY='):
                                    # Replace the existing personality line
                                    env_content += f'CURRENT_PERSONALITY={new_personality}\n'
                                    personality_line_found = True
                                else:
                                    env_content += line
                    
                    # If personality line wasn't found, add it
                    if not personality_line_found:
                        env_content += f'\nCURRENT_PERSONALITY={new_personality}\n'
                    
                    # Write back to .env file
                    with open(env_path, 'w') as env_file:
                        env_file.write(env_content)
                        
                    logger.info(f"Updated .env file with new personality: {new_personality}")
                except Exception as e:
                    logger.error(f"Error updating .env file: {e}")
                    # Continue anyway, as we've at least updated the current environment
                
                # Return success response with personality info
                return jsonify({
                    'success': True,
                    'personality': current_personality,
                    'details': PERSONALITY_TYPES[current_personality],
                    'message': f"Personality changed to {PERSONALITY_TYPES[current_personality]['name']}"
                })
            else:
                return jsonify({
                    'success': False,
                    'message': "Invalid personality type",
                    'valid_types': list(PERSONALITY_TYPES.keys())
                }), 400
        return jsonify({
            'success': False,
            'message': "Missing personality parameter"
        }), 400
    
    # GET request - return all personality types and current selection
    return jsonify({
        'current_personality': current_personality,
        'personalities': PERSONALITY_TYPES
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