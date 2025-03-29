"""
Memory System for Cherry Discord Bot

This module handles storing and retrieving memories about users based on interactions.
It uses Replit's database when available, or falls back to local file storage similar to the SimpTracker.
"""

import os
import json
import time
import random
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('cherry-memory')

# Try to import Replit's database module 
try:
    import replit
    from replit import db
    USING_REPLIT_DB = True
    logger.info("Using Replit database for memory storage")
except ImportError:
    USING_REPLIT_DB = False
    logger.info("Replit database not available, using local JSON storage for memories")

class MemorySystem:
    """
    Stores and retrieves memories of user interactions with Cherry.
    Memories are categorized by user_id and contain timestamps and context.
    """
    
    def __init__(self):
        """Initialize the memory system with the appropriate storage method."""
        self.memories = {}
        self.last_save_time = time.time()
        
        if not USING_REPLIT_DB:
            # Create memories directory if it doesn't exist
            os.makedirs('data', exist_ok=True)
            self.memory_file = os.path.join('data', 'memories.json')
            self._load_local_db()
    
    def _load_local_db(self):
        """Load memories from local JSON file when not using Replit."""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    self.memories = json.load(f)
                logger.info(f"Loaded {len(self.memories)} user memories from local storage")
            else:
                logger.info("No existing memory file found, starting with empty memories")
                self.memories = {}
        except Exception as e:
            logger.error(f"Error loading memories from file: {e}")
            self.memories = {}
    
    def _save_local_db(self):
        """Save memories to local JSON file when not using Replit."""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.memories, f)
            self.last_save_time = time.time()
            logger.info(f"Saved {len(self.memories)} user memories to local storage")
        except Exception as e:
            logger.error(f"Error saving memories to file: {e}")
    
    def add_memory(self, user_id, memory_type, content, context=None):
        """
        Add a new memory for a user.
        
        Args:
            user_id (str): Discord user ID
            memory_type (str): Type of memory (e.g., 'command', 'interaction', 'preference')
            content (str): Content of the memory
            context (dict, optional): Additional context for the memory
        
        Returns:
            bool: True if memory was added successfully
        """
        user_id = str(user_id)  # Ensure user_id is a string
        timestamp = datetime.now().isoformat()
        
        if USING_REPLIT_DB:
            # Using Replit database
            memory_key = f"memory_{user_id}"
            
            try:
                if memory_key in db:
                    user_memories = db[memory_key]
                else:
                    user_memories = []
                
                # Add the new memory
                memory = {
                    "type": memory_type,
                    "content": content,
                    "timestamp": timestamp,
                    "context": context or {}
                }
                
                user_memories.append(memory)
                
                # Store back in the database
                db[memory_key] = user_memories
                logger.debug(f"Added memory for user {user_id}")
                return True
            
            except Exception as e:
                logger.error(f"Error adding memory to Replit DB: {e}")
                return False
        else:
            # Using local JSON storage
            try:
                if user_id not in self.memories:
                    self.memories[user_id] = []
                
                # Add the new memory
                memory = {
                    "type": memory_type,
                    "content": content,
                    "timestamp": timestamp,
                    "context": context or {}
                }
                
                self.memories[user_id].append(memory)
                
                # Save to disk periodically (not on every write to reduce I/O)
                if time.time() - self.last_save_time > 60:  # Save every minute at most
                    self._save_local_db()
                
                logger.debug(f"Added memory for user {user_id}")
                return True
            
            except Exception as e:
                logger.error(f"Error adding memory to local storage: {e}")
                return False
    
    def get_random_memory(self, user_id, memory_type=None, max_age_days=None):
        """
        Get a random memory for a user, optionally filtered by type and age.
        
        Args:
            user_id (str): Discord user ID
            memory_type (str, optional): Type of memory to filter by
            max_age_days (int, optional): Maximum age of memory in days
            
        Returns:
            dict or None: A random memory or None if no memories match the criteria
        """
        user_id = str(user_id)
        
        try:
            if USING_REPLIT_DB:
                memory_key = f"memory_{user_id}"
                if memory_key not in db:
                    return None
                
                memories = db[memory_key]
            else:
                if user_id not in self.memories:
                    return None
                
                memories = self.memories[user_id]
            
            if not memories:
                return None
            
            # Filter by memory type if specified
            if memory_type:
                memories = [m for m in memories if m["type"] == memory_type]
            
            # Filter by age if specified
            if max_age_days:
                cutoff_date = (datetime.now() - timedelta(days=max_age_days)).isoformat()
                memories = [m for m in memories if m["timestamp"] >= cutoff_date]
            
            if not memories:
                return None
            
            # Return a random memory
            return random.choice(memories)
        
        except Exception as e:
            logger.error(f"Error retrieving memory: {e}")
            return None
    
    def get_latest_memory(self, user_id, memory_type=None):
        """
        Get the most recent memory for a user, optionally filtered by type.
        
        Args:
            user_id (str): Discord user ID
            memory_type (str, optional): Type of memory to filter by
            
        Returns:
            dict or None: The most recent memory or None if no memories match
        """
        user_id = str(user_id)
        
        try:
            if USING_REPLIT_DB:
                memory_key = f"memory_{user_id}"
                if memory_key not in db:
                    return None
                
                memories = db[memory_key]
            else:
                if user_id not in self.memories:
                    return None
                
                memories = self.memories[user_id]
            
            if not memories:
                return None
            
            # Filter by memory type if specified
            if memory_type:
                memories = [m for m in memories if m["type"] == memory_type]
            
            if not memories:
                return None
            
            # Sort by timestamp and return the most recent
            return sorted(memories, key=lambda m: m["timestamp"], reverse=True)[0]
        
        except Exception as e:
            logger.error(f"Error retrieving latest memory: {e}")
            return None
    
    def get_memories_by_type(self, user_id, memory_type, limit=5):
        """
        Get memories of a specific type for a user.
        
        Args:
            user_id (str): Discord user ID
            memory_type (str): Type of memory to retrieve
            limit (int, optional): Maximum number of memories to return
            
        Returns:
            list: List of memories of the specified type
        """
        user_id = str(user_id)
        
        try:
            if USING_REPLIT_DB:
                memory_key = f"memory_{user_id}"
                if memory_key not in db:
                    return []
                
                memories = db[memory_key]
            else:
                if user_id not in self.memories:
                    return []
                
                memories = self.memories[user_id]
            
            # Filter by memory type
            filtered_memories = [m for m in memories if m["type"] == memory_type]
            
            # Sort by timestamp (newest first) and limit the results
            return sorted(filtered_memories, key=lambda m: m["timestamp"], reverse=True)[:limit]
        
        except Exception as e:
            logger.error(f"Error retrieving memories by type: {e}")
            return []
    
    def has_memory_about(self, user_id, content_keyword):
        """
        Check if Cherry has any memories containing a specific keyword for a user.
        
        Args:
            user_id (str): Discord user ID
            content_keyword (str): Keyword to search for in memory content
            
        Returns:
            bool: True if a memory with the keyword exists
        """
        user_id = str(user_id)
        
        try:
            if USING_REPLIT_DB:
                memory_key = f"memory_{user_id}"
                if memory_key not in db:
                    return False
                
                memories = db[memory_key]
            else:
                if user_id not in self.memories:
                    return False
                
                memories = self.memories[user_id]
            
            # Check if any memory contains the keyword
            for memory in memories:
                if content_keyword.lower() in memory["content"].lower():
                    return True
            
            return False
        
        except Exception as e:
            logger.error(f"Error checking memory content: {e}")
            return False
    
    def record_command(self, user_id, command, args=None):
        """
        Record a command used by a user.
        
        Args:
            user_id (str): Discord user ID
            command (str): The command used
            args (dict, optional): Any arguments passed to the command
            
        Returns:
            bool: True if the command was recorded successfully
        """
        content = f"Used the {command} command"
        context = {"command": command, "args": args or {}}
        return self.add_memory(user_id, "command", content, context)
    
    def record_interaction(self, user_id, interaction_type, target_id=None):
        """
        Record an interaction between a user and Cherry or another user.
        
        Args:
            user_id (str): Discord user ID
            interaction_type (str): Type of interaction (e.g., 'flirt', 'hug', 'kiss')
            target_id (str, optional): ID of the user being interacted with, if any
            
        Returns:
            bool: True if the interaction was recorded successfully
        """
        if target_id:
            content = f"Performed a {interaction_type} interaction with user {target_id}"
            context = {"interaction_type": interaction_type, "target_id": target_id}
        else:
            content = f"Received a {interaction_type} interaction from Cherry"
            context = {"interaction_type": interaction_type}
        
        return self.add_memory(user_id, "interaction", content, context)
    
    def record_preference(self, user_id, preference_type, preference_value):
        """
        Record a user preference.
        
        Args:
            user_id (str): Discord user ID
            preference_type (str): Type of preference (e.g., 'color', 'nickname')
            preference_value (str): Value of the preference
            
        Returns:
            bool: True if the preference was recorded successfully
        """
        content = f"Expressed preference for {preference_type}: {preference_value}"
        context = {"preference_type": preference_type, "value": preference_value}
        return self.add_memory(user_id, "preference", content, context)
    
    def get_memory_count(self, user_id):
        """
        Get the total number of memories for a user.
        
        Args:
            user_id (str): Discord user ID
            
        Returns:
            int: Number of memories stored for the user
        """
        user_id = str(user_id)
        
        try:
            if USING_REPLIT_DB:
                memory_key = f"memory_{user_id}"
                if memory_key not in db:
                    return 0
                
                memories = db[memory_key]
                return len(memories)
            else:
                if user_id not in self.memories:
                    return 0
                
                return len(self.memories[user_id])
        
        except Exception as e:
            logger.error(f"Error getting memory count: {e}")
            return 0
    
    def generate_memory_reference(self, user_id, personality="flirty"):
        """
        Generate a natural language reference to a past memory that Cherry can include in a message,
        based on the current personality.
        
        Args:
            user_id (str): Discord user ID
            personality (str): Current personality mode to match the tone
            
        Returns:
            str or None: A memory reference phrase or None if no suitable memory exists
        """
        # Try to find a recent command or interaction memory
        memory = self.get_random_memory(user_id, max_age_days=14)
        if not memory:
            return None
        
        # Get memory details
        memory_type = memory["type"]
        content = memory["content"]
        timestamp = datetime.fromisoformat(memory["timestamp"])
        days_ago = (datetime.now() - timestamp).days
        
        # Time references based on age
        if days_ago == 0:
            time_ref = "earlier today"
        elif days_ago == 1:
            time_ref = "yesterday"
        elif days_ago < 7:
            time_ref = f"{days_ago} days ago"
        elif days_ago < 14:
            time_ref = "last week"
        else:
            time_ref = "a while back"
        
        # Generate different references based on personality
        if personality == "flirty":
            references = [
                f"I remember when you {content.lower()} {time_ref}... that was fun~ 💕",
                f"Mmm, I haven't forgotten how you {content.lower()} {time_ref}... 💋",
                f"You know what I was thinking about? When you {content.lower()} {time_ref} 💭",
                f"I've been daydreaming about when you {content.lower()} {time_ref}... 😍"
            ]
        
        elif personality == "tsundere":
            references = [
                f"I-it's not like I remember you {content.lower()} {time_ref} or anything! 😤",
                f"You think I'd forget how you {content.lower()} {time_ref}? As if! 🙄",
                f"Don't think I've forgotten about you {content.lower()} {time_ref}! 😠",
                f"I happened to recall when you {content.lower()} {time_ref}... not that I care! 💢"
            ]
        
        elif personality == "wholesome":
            references = [
                f"I fondly remember when you {content.lower()} {time_ref}! Such a nice memory! 💖",
                f"It brought me joy to recall how you {content.lower()} {time_ref}! 🌈",
                f"I was just thinking about the wonderful time when you {content.lower()} {time_ref}! ✨",
                f"One of my favorite memories is when you {content.lower()} {time_ref}! 💝"
            ]
        
        elif personality == "spicy":
            references = [
                f"I keep thinking about when you {content.lower()} {time_ref}... it gets me all hot and bothered~ 🔥",
                f"Mmm, I haven't stopped thinking about you {content.lower()} {time_ref}... 💦",
                f"You know what drives me wild? Remembering when you {content.lower()} {time_ref}... 😈",
                f"I've had *very* vivid dreams about when you {content.lower()} {time_ref}... 🥵"
            ]
        
        elif personality == "gamer":
            references = [
                f"Achievement unlocked: I remembered when you {content.lower()} {time_ref}! 🏆",
                f"Loading memory: You {content.lower()} {time_ref}! Memory loaded successfully! 💾",
                f"Hey, I just leveled up my memory skill and recalled when you {content.lower()} {time_ref}! 📊",
                f"Quick saving... I just remembered when you {content.lower()} {time_ref}! GG! 🎮"
            ]
        
        else:
            # Default case
            references = [
                f"I remember when you {content.lower()} {time_ref}!",
                f"Didn't you {content.lower()} {time_ref}?",
                f"Last time when you {content.lower()} {time_ref}...",
                f"I recall you {content.lower()} {time_ref}!"
            ]
        
        return random.choice(references)

# Create a singleton instance
memory_system = MemorySystem()