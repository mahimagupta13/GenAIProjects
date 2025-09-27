import os
from supabase import create_client, Client
from config import Config

class DatabaseManager:
    def __init__(self):
        self.supabase: Client = None
        self.is_connected_flag = False
        
        # Initialize Supabase connection
        if Config.SUPABASE_URL and Config.SUPABASE_KEY:
            try:
                self.supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
                self.is_connected_flag = True
            except Exception as e:
                print(f"Failed to connect to Supabase: {e}")
                self.is_connected_flag = False
        else:
            print("Supabase credentials not found in environment variables")
    
    def is_connected(self):
        """Check if database connection is established"""
        return self.is_connected_flag
    
    def save_post(self, topic: str, generated_post: str) -> bool:
        """Save a generated post to the linkedin_posts table"""
        if not self.is_connected():
            return False
        
        try:
            # Insert the post into the linkedin_posts table
            result = self.supabase.table('linkedin_posts').insert({
                'topic': topic,
                'llm_generated_post': generated_post
            }).execute()
            
            if result.data:
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error saving post to database: {e}")
            return False
    
    def get_post_history(self, limit: int = 10):
        """Get recent posts from the linkedin_posts table"""
        if not self.is_connected():
            return []
        
        try:
            result = self.supabase.table('linkedin_posts').select(
                'id, topic, llm_generated_post, created_at'
            ).order('created_at', desc=True).limit(limit).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"Error fetching post history: {e}")
            return []
