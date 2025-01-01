# Bunpro LLM Grammar Assistant 🎌

A Streamlit-powered Japanese grammar assistant that leverages your Bunpro account data and LLM technology to provide personalized Japanese grammar explanations and assistance.

## Features

- 🔐 Secure Bunpro account integration
- 📚 Access to your personal Bunpro grammar data
- 🤖 AI-powered grammar explanations using Groq LLM
- 🌏 Bilingual support (Japanese/English)
- 🔄 Real-time data synchronization with Bunpro
- 💬 Interactive chat interface
- 🎯 Focused on your troubled grammar points and ghost reviews
- 🔒 Secure credential handling with Pydantic
- 🌐 Unicode support for Japanese text

## Prerequisites

- A Bunpro account (https://bunpro.jp/)
- Python 3.9+
- Groq API key (https://console.groq.com/)

## Installation

1. Clone the repository:
```sh
git clone https://github.com/yourusername/bunpro-llm.git
cd bunpro-llm
```

2. Create and activate a virtual environment:
```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```sh
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory:
```sh
GROQ_API_KEY=your_groq_api_key
```

5. (Optional) Create a `.streamlit/secrets.toml` file for storing credentials:
```toml
GROQ_API_KEY = "your_groq_api_key"

[bunpro]
email = "your_bunpro_email"
password = "your_bunpro_password"
```

## Required Dependencies

```txt
streamlit>=1.0.0
pydantic>=2.0.0
groq>=0.3.0
beautifulsoup4>=4.0.0
requests>=2.0.0
python-dotenv>=0.0.1
```

## Usage

1. Start the Streamlit app:
```sh
streamlit run streamlit_app.py
```

2. If you haven't set up credentials in `secrets.toml`:
   - Enter your Bunpro credentials in the sidebar
   - Ensure your Groq API key is set in environment variables or secrets

3. Click "Refresh Bunpro Data" to fetch your latest grammar data

4. Start chatting with the AI about Japanese grammar!

## Project Structure

```
bunpro-llm/
├── streamlit_app.py   # Main Streamlit application
├── bunpro.py         # Bunpro client for data fetching
├── bunpro_utils.py   # Utility functions for parsing Bunpro data
├── llm.py           # LLM client configuration
├── requirements.txt  # Project dependencies
└── .env             # Environment variables
```

## How It Works

1. Authentication:
   - Securely authenticates with Bunpro using Pydantic models
   - Validates and stores credentials securely

2. Data Fetching:
   - Retrieves troubled grammar points and ghost reviews
   - Parses and structures data using BeautifulSoup
   - Stores data locally for quick access

3. LLM Integration:
   - Initializes Groq client with proper error handling
   - Loads grammar data into LLM context
   - Streams responses for better user experience

4. Chat Interface:
   - Maintains chat history in session state
   - Handles Unicode Japanese text properly
   - Provides real-time response streaming

## Security Features

- Credentials handled securely using Pydantic's SecretStr
- Environment variables and Streamlit secrets for API keys
- Session-based authentication with Bunpro
- No permanent storage of sensitive data

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a Pull Request

## License

[MIT License](LICENSE)

## Acknowledgments

- [Bunpro](https://bunpro.jp/) - Japanese grammar learning platform
- [Groq](https://groq.com/) - LLM provider
- [Streamlit](https://streamlit.io/) - Web application framework
- [Pydantic](https://pydantic.dev/) - Data validation

## Disclaimer

This is an unofficial tool and is not affiliated with Bunpro or Groq. Use in accordance with respective terms of service.