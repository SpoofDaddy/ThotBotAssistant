from flask import Flask, render_template, request, jsonify
import os
import subprocess
import psutil
import json
import logging
from simp_tracker import SimpTracker
from memory_system import memory_system
from responses import PERSONALITY_TYPES, DEFAULT_PERSONALITY
from dotenv import load_dotenv
from config import ENABLE_MEMORY, ENABLE_WELCOME_MESSAGES, ENABLE_USER_RECOGNITION

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
    
    # Get upcoming features for the dashboard (in priority order)
    features = [
        {
            'name': 'Memory Stats',
            'description': 'View memory statistics and user interaction history',
            'icon': '🧠'
        },
        {
            'name': 'Server Stats',
            'description': 'Dashboard showing server activity statistics',
            'icon': '📊'
        },
        {
            'name': 'Theme Switcher',
            'description': 'Switch between light and dark mode for the dashboard',
            'icon': '🌓'
        }
    ]
    
    # Get active features
    active_features = [
        {
            'name': 'User Nicknames',
            'description': 'Cherry gives personality-based nicknames to users',
            'icon': '📝'
        },
        {
            'name': 'Welcome Messages',
            'description': 'Personalized greetings for new server members',
            'icon': '👋'
        },
        {
            'name': 'Expanded Roleplay',
            'description': 'Interactive commands like !cuddle, !dance, !headpat, and !highfive',
            'icon': '💋'
        }
    ]
    
    return render_template('index.html', 
                          bot_status=bot_status,
                          simp_scores=simp_scores,
                          current_personality=current_personality,
                          personalities=PERSONALITY_TYPES,
                          coming_soon=features,
                          active_features=active_features)

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
    basic_commands = [
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
            'name': '!nickname',
            'description': 'Cherry will give you or someone else a cute nickname 💕',
            'usage': '!nickname [@user]'
        }
    ]
    
    roleplay_commands = [
        {
            'name': '!hug',
            'description': 'Cherry will give you or someone you mention a hug 🤗',
            'usage': '!hug [@user]'
        },
        {
            'name': '!kiss',
            'description': 'Cherry will kiss you or someone you mention 😘',
            'usage': '!kiss [@user]'
        },
        {
            'name': '!pat',
            'description': 'Cherry will pat you or someone you mention 👐',
            'usage': '!pat [@user]'
        },
        {
            'name': '!cuddle',
            'description': 'Cherry will cuddle with you or someone you mention 🫂',
            'usage': '!cuddle [@user]'
        },
        {
            'name': '!dance',
            'description': 'Cherry will dance with you or someone you mention 💃',
            'usage': '!dance [@user]'
        },
        {
            'name': '!headpat',
            'description': 'Cherry will let you or someone else pat her head 🥰',
            'usage': '!headpat [@user]'
        },
        {
            'name': '!highfive',
            'description': 'Cherry will give you or someone you mention a high five 🙌',
            'usage': '!highfive [@user]'
        }
    ]
    
    utility_commands = [
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
    
    # Combine all command categories
    commands = basic_commands + roleplay_commands + utility_commands
    
    return jsonify({
        'commands': commands
    })

@app.route('/api/welcome_messages', methods=['GET', 'POST'])
def api_welcome_messages():
    """API endpoint to get or toggle welcome messages feature"""
    if request.method == 'POST':
        data = request.get_json()
        if data and 'enabled' in data:
            try:
                enabled_flag = data['enabled']
                # Make sure it's a boolean
                if not isinstance(enabled_flag, bool):
                    return jsonify({
                        'success': False,
                        'message': "The 'enabled' parameter must be a boolean"
                    }), 400
                
                # Update environment variable to persist across restarts
                os.environ["ENABLE_WELCOME_MESSAGES"] = str(enabled_flag).lower()
                
                # Also update the environment file for persistence across reboots
                env_path = os.path.join(os.path.dirname(__file__), '.env')
                
                # Read existing .env file
                env_content = ""
                welcome_flag_found = False
                
                if os.path.exists(env_path):
                    with open(env_path, 'r') as env_file:
                        lines = env_file.readlines()
                        for line in lines:
                            if line.startswith('ENABLE_WELCOME_MESSAGES='):
                                # Replace the existing line
                                env_content += f'ENABLE_WELCOME_MESSAGES={str(enabled_flag).lower()}\n'
                                welcome_flag_found = True
                            else:
                                env_content += line
                
                # If flag wasn't found, add it
                if not welcome_flag_found:
                    env_content += f'\nENABLE_WELCOME_MESSAGES={str(enabled_flag).lower()}\n'
                
                # Write back to .env file
                with open(env_path, 'w') as env_file:
                    env_file.write(env_content)
                    
                logger.info(f"Updated .env file with ENABLE_WELCOME_MESSAGES={str(enabled_flag).lower()}")
                
                return jsonify({
                    'success': True,
                    'enabled': enabled_flag,
                    'message': f"Welcome messages {'enabled' if enabled_flag else 'disabled'}"
                })
            except Exception as e:
                logger.error(f"Error updating welcome messages setting: {e}")
                return jsonify({
                    'success': False,
                    'message': f"Error updating welcome messages setting: {str(e)}"
                }), 500
        else:
            return jsonify({
                'success': False,
                'message': "Missing 'enabled' parameter"
            }), 400
    
    # GET request - return current setting
    return jsonify({
        'success': True,
        'enabled': ENABLE_WELCOME_MESSAGES
    })

@app.route('/api/memory')
def api_memory():
    """API endpoint to get memory system statistics"""
    # Get total memory count
    try:
        # Memory stats aren't tied to individual users on the dashboard yet
        # Just get overall system stats for now
        memory_stats = {
            'enabled': ENABLE_MEMORY,
            'total_memories': 0  # Placeholder - we'll add actual stats in future
        }
        
        return jsonify({
            'success': True,
            'stats': memory_stats
        })
    except Exception as e:
        logger.error(f"Error getting memory stats: {e}")
        return jsonify({
            'success': False,
            'message': f"Error retrieving memory statistics: {str(e)}"
        }), 500

@app.route('/api/coming_soon')
def api_coming_soon():
    """API endpoint to get all coming soon features"""
    features = [
        {
            'name': 'Memory Stats',
            'description': 'View memory statistics and user interaction history',
            'icon': '🧠'
        },
        {
            'name': 'Server Stats',
            'description': 'Dashboard showing server activity statistics',
            'icon': '📊'
        },
        {
            'name': 'Theme Switcher',
            'description': 'Switch between light and dark mode for the dashboard',
            'icon': '🌓'
        },
        {
            'name': 'Mobile Improvements',
            'description': 'Better mobile experience for the dashboard',
            'icon': '📱'
        },
        {
            'name': 'Event Calendar',
            'description': 'Schedule and manage server events',
            'icon': '📅'
        }
    ]
    
    # Get list of active features
    active_features = [
        {
            'name': 'User Nicknames',
            'description': 'Cherry gives personality-based nicknames to users',
            'icon': '📝'
        },
        {
            'name': 'Welcome Messages',
            'description': 'Personalized greetings for new server members',
            'icon': '👋'
        },
        {
            'name': 'Expanded Roleplay',
            'description': 'Interactive commands like !cuddle, !dance, !headpat, and !highfive',
            'icon': '💋'
        }
    ]
    
    return jsonify({
        'coming_soon': features,
        'active_features': active_features
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)