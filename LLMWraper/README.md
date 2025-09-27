# LinkedIn Post Generator

A full-fledged LLM wrapper application that generates professional LinkedIn posts using GROQ API and stores them in Supabase.

## Features

- 🚀 **Streamlit UI** - Clean, intuitive interface for generating LinkedIn posts
- 🤖 **GROQ API Integration** - Uses LLaMA 3 model for high-quality content generation
- 🗄️ **Supabase Database** - Stores post history with user authentication
- 🔐 **Authentication Layer** - Simple user authentication system
- 📚 **Post History** - View and manage previously generated posts
- ✍️ **Custom LinkedIn Style** - Generates posts following professional LinkedIn content patterns

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
# GROQ API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
```

**Important:** The application will automatically load these environment variables from the `.env` file. If any variables are missing, the app will show appropriate warnings and allow manual input as fallback.

### 3. Set up Supabase Database

1. Create a new Supabase project
2. Create a table called `linkedin_posts` with the following schema:

```sql
CREATE TABLE linkedin_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic TEXT NOT NULL,
    llm_generated_post TEXT NOT NULL,
    user_id TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 4. Get GROQ API Key

1. Visit [GROQ Console](https://console.groq.com/)
2. Sign up for an account
3. Generate an API key
4. Add it to your `.env` file

### 5. Run the Application

```bash
streamlit run app.py
```

## Usage

1. **Login**: Use the demo credentials (admin/admin123) or configure your own authentication
2. **Enter API Key**: Add your GROQ API key in the sidebar
3. **Generate Post**: Enter a topic or context for your LinkedIn post
4. **Review & Save**: Review the generated post and save it to your history

## Demo Credentials

- **Username**: `admin`
- **Password**: `admin123`

## Features Overview

### LinkedIn Post Generation
- Follows professional LinkedIn content structure
- Balances personal storytelling with professional insights
- Generates 150-250 word posts optimized for engagement
- Uses conversational yet authoritative tone

### Database Storage
- Stores generated posts with metadata
- Tracks user-specific post history
- Includes timestamps and topic information

### User Interface
- Clean, responsive Streamlit interface
- Real-time post generation
- Post history management
- Copy-to-clipboard functionality

## API Integration

The application uses:
- **GROQ API** for LLM-powered content generation
- **Supabase** for database storage and user management
- **Streamlit** for the web interface

## Customization

You can customize the LinkedIn post style by modifying the `LINKEDIN_PROMPT` in the `Config` class within `app.py`.

## Troubleshooting

1. **API Key Issues**: Ensure your GROQ API key is valid and has sufficient credits
2. **Database Connection**: Verify your Supabase URL and key are correct in the `.env` file
3. **Environment Variables**: Make sure your `.env` file is in the project root and contains all required variables
4. **Authentication**: Check that the demo credentials work or implement proper authentication

## License

This project is open source and available under the MIT License.
