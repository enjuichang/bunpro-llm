# Bunpro LLM Grammar Assistant 🎌

A Streamlit-powered Japanese grammar assistant that leverages your Bunpro account data and LLM technology to provide personalized Japanese grammar explanations and assistance.

## Demo Link
A [streamlit app](https://bunpro-llm.streamlit.app/) for testing purposes.

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

4. Set up your credentials in one of these ways:

   a. Using `.streamlit/secrets.toml`:
   ```toml
   [llm_creds]
   GROQ_API_KEY = "your_groq_api_key"

   [bunpro]
   email = "your_bunpro_email"
   password = "your_bunpro_password"
   ```

   b. Using environment variables:
   ```sh
   export GROQ_API_KEY=your_groq_api_key
   ```

   c. Using the Streamlit interface:
   - Enter your Groq API key in the sidebar
   - Enter your Bunpro credentials in the sidebar

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

2. Set up your credentials in one of these ways:

   a. Using `.streamlit/secrets.toml` (recommended):
   ```toml
   [llm_creds]
   GROQ_API_KEY = "your_groq_api_key"

   [bunpro]
   email = "your_bunpro_email"
   password = "your_bunpro_password"
   ```

   b. Using the Streamlit interface:
   - Fill in all credentials in the sidebar form:
     - Groq API Key
     - Bunpro Email
     - Bunpro Password
   - Click "Save All Credentials"
   - Use "Reset Credentials" button if you need to update them

3. After credentials are set:
   - Click "Refresh Bunpro Data" to fetch your latest grammar data
   - Start chatting with the AI about Japanese grammar!

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

- Unified credentials management:
  - All credentials are set together to prevent partial states
  - Secure password fields for sensitive information
  - Option to reset all credentials when needed
- Credentials handled securely using Pydantic's SecretStr
- Multiple configuration options:
  - Streamlit secrets (recommended)
  - Secure input form
- Session-based authentication
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
