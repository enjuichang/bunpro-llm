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

## Prerequisites

- A Bunpro account (https://bunpro.jp/)
- Python 3.9+
- Groq API key

## Installation

1. Clone the repository:
```sh
git clone https://github.com/yourusername/bunpro-llm.git
```

2. Install dependencies:
```sh
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory:
```sh
GROQ_API_KEY=your_groq_api_key
```
OR Any other llm providers

4. (Optional) Create a `.streamlit/secrets.toml` file for storing skipping logging into Bunpro everytime:
```toml
[bunpro]
email = "your_bunpro_email"
password = "your_bunpro_password"
```

## Usage

1. Start the Streamlit app:
```sh
streamlit run streamlit_app.py
```


2. If you haven't set up credentials in `secrets.toml`, enter your Bunpro credentials in the sidebar.

3. Click "Refresh Bunpro Data" to fetch your latest grammar data.

4. Start chatting with the AI about Japanese grammar!

## Project Structure

- `streamlit_app.py`: Main Streamlit application
- `bunpro.py`: Bunpro client for data fetching
- `bunpro_utils.py`: Utility functions for parsing Bunpro data
- `llm.py`: LLM client configuration

## How It Works

1. The app authenticates with your Bunpro account
2. Fetches your troubled grammar points and ghost reviews
3. Loads this data into the LLM's context
4. Provides personalized grammar explanations based on your Bunpro data

## Security Note

Your Bunpro credentials are stored securely and are only used to fetch your grammar data. We recommend using Streamlit's secrets management for storing credentials.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)

## Acknowledgments

- Built on top of [Bunpro](https://bunpro.jp/)'s excellent Japanese grammar learning platform
- Powered by [Groq](https://groq.com/)'s LLM technology
- Built with [Streamlit](https://streamlit.io/)

## Disclaimer

This is an unofficial tool and is not affiliated with Bunpro. Make sure you comply with Bunpro's terms of service when using this tool.