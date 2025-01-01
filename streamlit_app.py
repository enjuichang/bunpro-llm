"""
Japanese Grammar Assistant Streamlit Application

This application provides a chat interface for Japanese language learning,
integrating Bunpro grammar data with LLM-powered responses.
"""

import streamlit as st
from llm import groq_client, LLMConfig, LLMClient
import json
from bunpro import BunproClient
from typing import Dict, List, Union, Optional
from pydantic import BaseModel, Field, SecretStr
import os
from groq import Groq  # Add this import for type hints


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


def setup_sidebar() -> None:
    """Setup and handle sidebar UI elements"""
    with st.sidebar:
        st.title('🤖💬 Japanese Grammar Assistant / 日本語文法アシスタント')

        # Check if credentials are in secrets
        credentials_in_secrets = (
            'llm_creds' in st.secrets and
            'GROQ_API_KEY' in st.secrets.llm_creds and
            'bunpro' in st.secrets and
            'email' in st.secrets.bunpro and
            'password' in st.secrets.bunpro
        )

        # Load from secrets if available
        if credentials_in_secrets and not st.session_state.get('credentials_set'):
            st.session_state.GROQ_API_KEY = st.secrets.llm_creds.GROQ_API_KEY
            st.session_state.bunpro_email = st.secrets.bunpro.email
            st.session_state.bunpro_password = st.secrets.bunpro.password
            st.session_state.credentials_set = True
            st.session_state.bunpro_credentials_set = True
            st.success("All credentials loaded from secrets!")

        # Otherwise, show input fields
        elif not st.session_state.get('credentials_set'):
            with st.form("credentials_form"):
                groq_api_key = st.text_input("Groq API Key:", type="password")
                bunpro_email = st.text_input("Bunpro Email:", type="default")
                bunpro_password = st.text_input("Bunpro Password:", type="password")

                if st.form_submit_button("Save All Credentials"):
                    if groq_api_key and bunpro_email and bunpro_password:
                        st.session_state.GROQ_API_KEY = groq_api_key
                        st.session_state.bunpro_email = bunpro_email
                        st.session_state.bunpro_password = bunpro_password
                        st.session_state.credentials_set = True
                        st.session_state.bunpro_credentials_set = True
                        st.success("All credentials saved!")
                        st.rerun()  # Refresh the page to update UI
                    else:
                        st.error("Please enter all credentials")

        # Show refresh button only if all credentials are set
        if st.session_state.get('credentials_set'):
            handle_refresh_button()

            # Add option to reset credentials
            if st.button("Reset Credentials"):
                for key in ['GROQ_API_KEY', 'bunpro_email', 'bunpro_password', 
                          'credentials_set', 'bunpro_credentials_set']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()  # Refresh the page to show credential form


def handle_refresh_button() -> None:
    """Handle the Refresh Bunpro Data button click"""
    if st.button("Refresh Bunpro Data"):
        with st.spinner("Updating Bunpro data..."):
            client = BunproClient(
                email=st.session_state.bunpro_email,
                password=st.session_state.bunpro_password
            )
            if client.update_grammar_data():
                st.success("Successfully updated Bunpro data!")
                st.session_state.bunpro_data_loaded = True
            else:
                st.error("Failed to update Bunpro data")


def initialize_llm_client() -> Optional[Groq]:
    """Initialize the LLM client with proper error handling."""
    try:
        # Check for API key in session state, secrets, or environment
        api_key = (st.session_state.get('GROQ_API_KEY') or 
                  st.secrets.get("llm_creds", {}).get("GROQ_API_KEY") or 
                  os.environ.get("GROQ_API_KEY"))

        if not api_key:
            st.error("No Groq API key found. Please provide your API key in the sidebar.")
            return None

        # Initialize LLM client
        config = LLMConfig(api_key=SecretStr(api_key))
        client = LLMClient(config)
        return client.groq_client

    except Exception as e:
        st.error(f"Failed to initialize LLM client: {str(e)}")
        return None


def handle_chat_interaction(system_prompt: str, llm_client: Optional[Groq]) -> None:
    """
    Handle chat interactions with the LLM.

    Args:
        system_prompt (str): System prompt containing Bunpro grammar data
        llm_client (Optional[Groq]): Initialized Groq client
    """
    if llm_client is None:
        st.error("LLM client not initialized. Please check your API key configuration.")
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
                for response in llm_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        *[{"role": m["role"], "content": m["content"]}
                          for m in st.session_state.messages]
                    ],
                    stream=True):
                    chunk = response.choices[0].delta.content or ""
                    full_response += chunk
                    message_placeholder.markdown(decode_unicode(full_response + "▌"))
                message_placeholder.markdown(decode_unicode(full_response))
            
            # Add assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")


def main():
    """Main application function"""
    # Initialize LLM client
    llm_client = initialize_llm_client()
    if llm_client is None:
        st.error("Cannot proceed without LLM client. Please check your configuration.")
        st.stop()

    # Initialize session state
    initialize_session_state()

    # Setup sidebar
    setup_sidebar()

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