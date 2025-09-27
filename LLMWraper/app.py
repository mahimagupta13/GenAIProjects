import streamlit as st
from config import Config
from llm_service import LLMService
from database import DatabaseManager

# Page configuration
st.set_page_config(
    page_title="LinkedIn Post Generator",
    page_icon="🚀",
    layout="centered"
)


def main():
    """Simplified LinkedIn Post Generator"""
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Header
    st.title("🚀 LinkedIn Post Generator")
    
    # Show connection status
    if db_manager.is_connected():
        #st.success("✅ Connected to Supabase database")
        pass
    else:
        st.warning("⚠️ Database not connected - posts won't be saved")
    
    # Check GROQ API key from environment
    api_key = Config.GROQ_API_KEY
    if api_key:
        #st.success("✅ GROQ API Key loaded from .env file")
        pass
    else:
        st.error("❌ GROQ_API_KEY not found in .env file. Please add it to your .env file.")
        st.stop()
    
    # Topic input
    topic = st.text_area(
        "Enter your topic or context for the LinkedIn post:",
        placeholder="e.g., The future of remote work, My experience with AI tools, Why I switched careers...",
        height=100
    )
    
    # Generate button
    if st.button("🚀 Generate LinkedIn Post", type="primary", use_container_width=True):
        if not topic.strip():
            st.error("Please enter a topic for your LinkedIn post")
        else:
            with st.spinner("🤖 Generating your LinkedIn post..."):
                llm_service = LLMService()
                generated_post = llm_service.generate_linkedin_post(topic, api_key)
                
                if generated_post:
                    st.session_state.generated_post = generated_post
                    st.session_state.current_topic = topic
                    
                    # Save to database
                    if db_manager.is_connected():
                        if db_manager.save_post(topic, generated_post):
                            st.success("✅ Post saved to database!")
                        else:
                            st.warning("⚠️ Post generated but could not be saved to database")
    
    # Display generated post in text area
    if hasattr(st.session_state, 'generated_post') and st.session_state.generated_post:
        st.markdown("---")
        st.subheader("📝 Your Generated LinkedIn Post")
        
        # Simple text area for output
        st.text_area(
            "Generated Post",
            value=st.session_state.generated_post,
            height=300,
            help="Copy this text to use in your LinkedIn post"
        )
        
        # Simple action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Generate New", use_container_width=True):
                if 'generated_post' in st.session_state:
                    del st.session_state.generated_post
                st.rerun()
        
        with col2:
            if st.button("📋 Copy to Clipboard", use_container_width=True):
                st.write("Copy this text:")
                st.code(st.session_state.generated_post)
    
    # Show recent posts history
    if db_manager.is_connected():
        st.markdown("---")
        st.subheader("📚 Recent Posts")
        
        if st.button("🔄 Refresh History"):
            st.rerun()
        
        history = db_manager.get_post_history(5)  # Get last 5 posts
        if history:
            for i, post in enumerate(history):
                with st.expander(f"Post {i+1} - {post['topic'][:30]}..."):
                    st.write(f"**Topic:** {post['topic']}")
                    st.write(f"**Created:** {post['created_at']}")
                    st.write(f"**Post:** {post['llm_generated_post'][:200]}...")
        else:
            st.info("No posts found. Generate your first post!")

if __name__ == "__main__":
    main()
