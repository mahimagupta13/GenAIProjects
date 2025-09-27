import streamlit as st
import requests
from config import Config

class LLMService:
    def __init__(self):
        self.api_url = Config.GROQ_API_URL
        self.model = Config.GROQ_MODEL
        self.prompt_template = Config.LINKEDIN_PROMPT
    
    def generate_linkedin_post(self, topic, api_key):
        """Generate LinkedIn post using GROQ API"""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = self.prompt_template.format(topic=topic)
        
        try:
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 500,
                "stream": False
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                st.success(f"✅ Successfully generated post using model: {self.model}")
                return result["choices"][0]["message"]["content"].strip()
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            st.error(f"Error generating post: {str(e)}")
            return None
