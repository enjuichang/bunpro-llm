"""
Japanese Grammar Assistant Streamlit Application

This application provides a chat interface for Japanese language learning,
integrating Bunpro grammar data with LLM-powered responses.
"""

import streamlit as st
from llm import LLMConfig, LLMClient
import json
from bunpro import BunproClient
from typing import Dict, List, Union, Optional, Any
from pydantic import BaseModel, Field, SecretStr
import os
from groq import Groq  # Add this import for type hints
import time


class ChatMessage(BaseModel):
    """Pydantic model for chat messages"""
    role: str = Field(..., description="Role of the message sender (user/assistant/system)")
    content: str = Field(..., description="Content of the message")


class AppState(BaseModel):
    """Pydantic model for application state"""
    bunpro_credentials_set: bool = Field(default=False, description="Whether Bunpro credentials are set")
    bunpro_data_loaded: bool = Field(default=False, description="Whether Bunpro data is loaded")
    messages: List[ChatMessage] = Field(default_factory=list, description="Chat message history")
    bunpro_email: Optional[str] = Field(None, description="Bunpro account email")
    bunpro_password: Optional[str] = Field(None, description="Bunpro account password")


# Set page config FIRST - before any other Streamlit commands
st.set_page_config(
    page_title="Japanese Grammar Assistant",
    page_icon="🎌",
    layout="wide",
)


def decode_unicode(text: Union[str, Dict, List]) -> Union[str, Dict, List]:
    """
    Decode Unicode escape sequences in text.

    Args:
        text: Input text, dictionary, or list containing text to decode

    Returns:
        Decoded text in the same structure as input
    """
    if isinstance(text, str):
        return text.encode('utf-8').decode('unicode-escape').encode('latin1').decode('utf-8')
    elif isinstance(text, dict):
        return {k: decode_unicode(v) for k, v in text.items()}
    elif isinstance(text, list):
        return [decode_unicode(item) for item in text]
    return text


def load_bunpro_data() -> Optional[Dict]:
    """
    Load Bunpro grammar data from JSON file.

    Returns:
        Optional[Dict]: Dictionary containing grammar data or None if file not found
    """
    try:
        with open('bunpro_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def initialize_session_state() -> None:
    """Initialize Streamlit session state with default values"""
    # Initialize session states using Pydantic model defaults
    default_state = AppState()

    if 'bunpro_credentials_set' not in st.session_state:
        st.session_state.bunpro_credentials_set = default_state.bunpro_credentials_set

    if 'bunpro_data_loaded' not in st.session_state:
        st.session_state.bunpro_data_loaded = default_state.bunpro_data_loaded

    if "messages" not in st.session_state:
        st.session_state.messages = default_state.messages

    # Initialize LLM config with defaults if not set
    if 'llm_config' not in st.session_state:
        st.session_state.llm_config = {
            'provider': 'groq',
            'model_name': "llama-3.3-70b-versatile",
            'temperature': 0.7,
            'max_tokens': 2048
        }


def setup_sidebar() -> None:
    """Setup and handle sidebar UI elements"""
    with st.sidebar:
        st.title('🤖💬 Japanese Grammar Assistant / 日本語文法アシスタント')

        # LLM Settings section (always visible)
        with st.expander("🔧 LLM Settings", expanded=True):
            # Provider selection
            provider = st.selectbox(
                "Provider",
                options=["groq", "openai", "anthropic"],
                index=0,
                help="Select your LLM provider"
            )

            # Show warning for non-Groq providers
            if provider != "groq":
                st.warning(f"⚠️ {provider.title()} integration is coming soon! Please use Groq for now.")

            # Model selection based on provider
            if provider == "groq":
                model_options = [
                    "llama-3.3-70b-versatile",
                    "mixtral-8x7b-32768"
                ]
            else:
                model_options = ["Coming soon..."]

            model = st.selectbox(
                "Model",
                options=model_options,
                index=0,
                help="Select the model to use"
            )

            # Temperature slider
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.llm_config.get('temperature', 0.7),
                step=0.1,
                help="Higher values make output more creative, lower values more deterministic"
            )

            # Max tokens slider
            max_tokens = st.slider(
                "Max Tokens",
                min_value=256,
                max_value=4096,
                value=st.session_state.llm_config.get('max_tokens', 2048),
                step=256,
                help="Maximum length of the response"
            )

            # API Key input
            api_key = st.text_input(
                f"{provider.title()} API Key:", 
                value=st.session_state.llm_config.get('api_key', ''),
                type="password",
                help=f"Enter your {provider.title()} API key"
            )

            if api_key:  # Update config when API key is provided
                st.session_state.llm_config.update({
                    'provider': provider,
                    'api_key': api_key,
                    'model_name': model,
                    'temperature': temperature,
                    'max_tokens': max_tokens
                })

        # Bunpro credentials section
        if not st.session_state.get('bunpro_credentials_set'):
            with st.form("bunpro_credentials_form"):
                st.subheader("Bunpro Credentials")
                bunpro_email = st.text_input("Bunpro Email:", type="default")
                bunpro_password = st.text_input("Bunpro Password:", type="password")

                if st.form_submit_button("Save Bunpro Credentials"):
                    if bunpro_email and bunpro_password:
                        st.session_state.bunpro_email = bunpro_email
                        st.session_state.bunpro_password = bunpro_password
                        st.session_state.bunpro_credentials_set = True
                        st.success("Bunpro credentials saved!")
                        st.rerun()
                    else:
                        st.error("Please enter both email and password")

        # Show refresh button if all credentials are set
        if st.session_state.get('bunpro_credentials_set'):
            handle_refresh_button()

        # Add option to reset all credentials
        if st.button("Reset All Credentials"):
            for key in ['llm_config', 'bunpro_email', 'bunpro_password', 
                      'credentials_set', 'bunpro_credentials_set']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()


def handle_refresh_button() -> None:
    """Handle the refresh button click"""
    if st.button("🔄 Refresh Bunpro Data"):
        with st.spinner('Authenticating with Bunpro...'):
            client = BunproClient(
                email=st.session_state.bunpro_email,
                password=st.session_state.bunpro_password
            )
            success, message = client.update_grammar_data()

            if success:
                st.session_state.bunpro_data_loaded = True
                st.success("✅ Successfully updated Bunpro data!")
                st.rerun()
            else:
                if "Invalid email or password" in message:
                    st.error("❌ Invalid Bunpro credentials")
                    st.warning("Please check your email and password and try again.")
                    # Reset Bunpro credentials
                    st.session_state.bunpro_credentials_set = False
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(f"Error: {message}")


def initialize_llm_client() -> Optional[Any]:
    """Initialize the LLM client with proper error handling."""
    try:
        if not st.session_state.get('llm_config'):
            st.error("No LLM configuration found. Please configure in the sidebar.")
            return None

        # Check if API key is set
        if not st.session_state.llm_config.get('api_key'):
            st.error("Please enter your API key in the LLM Settings.")
            return None

        config = LLMConfig(
            provider=st.session_state.llm_config['provider'],
            api_key=SecretStr(st.session_state.llm_config['api_key']),
            model_name=st.session_state.llm_config['model_name'],
            temperature=st.session_state.llm_config['temperature'],
            max_tokens=st.session_state.llm_config['max_tokens']
        )

        client = LLMClient(config)
        return client.provider.client

    except Exception as e:
        error_msg = str(e)
        if "'api_key'" in error_msg:
            st.error("API key is required. Please enter your API key in the LLM Settings.")
        else:
            st.error(f"Failed to initialize LLM client: {error_msg}")
        return None


def handle_chat_interaction(system_prompt: str, llm_client: Optional[Any]) -> None:
    """Handle chat interactions with the LLM."""
    if llm_client is None:
        st.error("LLM client not initialized. Please check your configuration.")
        return

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(decode_unicode(message["content"]))

    # Handle new user input
    if prompt := st.chat_input("日本語の文法について質問してください..."):
        try:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate and display assistant response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""

                # Use current LLM settings from session state
                config = st.session_state.llm_config
                for response in llm_client.chat.completions.create(
                    model=config['model_name'],
                    messages=[
                        {"role": "system", "content": system_prompt},
                        *[{"role": m["role"], "content": m["content"]}
                          for m in st.session_state.messages]
                    ],
                    temperature=config['temperature'],
                    max_tokens=config['max_tokens'],
                    stream=True):
                    chunk = response.choices[0].delta.content or ""
                    full_response += chunk
                    message_placeholder.markdown(decode_unicode(full_response + "▌"))
                message_placeholder.markdown(decode_unicode(full_response))

            # Add assistant response to history
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )

        except Exception as e:
            st.error(f"Error generating response: {str(e)}")


def main():
    """Main application function"""
    # Initialize session state first
    initialize_session_state()

    # Setup sidebar (this will set credentials if needed)
    setup_sidebar()

    # Initialize LLM client after sidebar setup
    llm_client = initialize_llm_client()
    if llm_client is None:
        st.error("Cannot proceed without LLM client. Please check your configuration.")
        st.stop()

    # Check credentials and load data
    if not st.session_state.bunpro_credentials_set:
        st.warning("Please set your Bunpro credentials in the sidebar first.")
        st.stop()

    # Load and process Bunpro data
    bunpro_data = load_bunpro_data()
    if bunpro_data is None:
        st.warning("No Bunpro data found. Please click 'Refresh Bunpro Data' to fetch the latest data.")
        st.stop()

    # Decode Unicode in Bunpro data
    bunpro_data = decode_unicode(bunpro_data)

    # Create system prompt
    system_prompt = f"""You are a Japanese language tutor with access to the following grammar points from Bunpro:
    {json.dumps(bunpro_data, indent=2, ensure_ascii=False)}
    - Use this information to help answer questions about Japanese grammar.
    - You MUST use Japanese characters instead of Romaji"""

    # Handle chat interactions
    handle_chat_interaction(system_prompt, llm_client)


if __name__ == "__main__":
    main()