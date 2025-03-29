try:
    # Attempt to import replit for database functionality
    from replit import db
    USING_REPLIT = True
except ImportError:
    # Fallback to a local dictionary if not running on Replit
    USING_REPLIT = False
    import json
    import os
    import logging

    logger = logging.getLogger('cherry')
    logger.info("Replit module not found. Using local storage for simp tracking.")


class SimpTracker:
    """
    Tracks and manages user "simp scores" - how much users interact with Cherry.
    Uses Replit's database when available, or falls back to a local file.
    """
    
    def __init__(self):
        """Initialize the simp tracker with the appropriate storage method."""
        self.db_prefix = "simp_score_"
        
        if not USING_REPLIT:
            self.local_storage_file = "simp_scores.json"
            self.local_db = self._load_local_db()
    
    def _load_local_db(self):
        """Load the simp scores from local JSON file when not using Replit."""
        if os.path.exists(self.local_storage_file):
            try:
                with open(self.local_storage_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading simp scores: {e}")
                return {}
        return {}
    
    def _save_local_db(self):
        """Save the simp scores to local JSON file when not using Replit."""
        try:
            with open(self.local_storage_file, 'w') as f:
                json.dump(self.local_db, f)
        except Exception as e:
            logger.error(f"Error saving simp scores: {e}")
    
    def get_score(self, user_id):
        """Get the simp score for a user."""
        if USING_REPLIT:
            key = f"{self.db_prefix}{user_id}"
            return db.get(key, 0)
        else:
            return self.local_db.get(user_id, 0)
    
    def increment_score(self, user_id, amount=1):
        """Increment a user's simp score."""
        if USING_REPLIT:
            key = f"{self.db_prefix}{user_id}"
            current_score = db.get(key, 0)
            db[key] = current_score + amount
        else:
            current_score = self.local_db.get(user_id, 0)
            self.local_db[user_id] = current_score + amount
            self._save_local_db()
        
        return self.get_score(user_id)
    
    def reset_score(self, user_id):
        """Reset a user's simp score to zero."""
        if USING_REPLIT:
            key = f"{self.db_prefix}{user_id}"
            db[key] = 0
        else:
            self.local_db[user_id] = 0
            self._save_local_db()
    
    def get_top_simps(self, limit=10):
        """Get the top simps by score."""
        if USING_REPLIT:
            # Get all simp scores from Replit db
            scores = {}
            for key in db.keys():
                if key.startswith(self.db_prefix):
                    user_id = key[len(self.db_prefix):]
                    scores[user_id] = db[key]
        else:
            scores = self.local_db
        
        # Sort and return top simps
        sorted_simps = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_simps[:limit]
