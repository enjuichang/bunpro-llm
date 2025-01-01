# Code refactored from https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps

import streamlit as st
from llm import groq_client
import json
from bunpro import BunproClient

# Set page config FIRST - before any other Streamlit commands
st.set_page_config(
    page_title="Japanese Grammar Assistant",
    page_icon="🎌",
    layout="wide",
)

# Function to decode Unicode escape sequences
def decode_unicode(text):
    if isinstance(text, str):
        return text.encode('utf-8').decode('unicode-escape').encode('latin1').decode('utf-8')
    elif isinstance(text, dict):
        return {k: decode_unicode(v) for k, v in text.items()}
    elif isinstance(text, list):
        return [decode_unicode(item) for item in text]
    return text

# Function to load Bunpro data
def load_bunpro_data():
    try:
        with open('bunpro_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

# Initialize session states
if 'bunpro_credentials_set' not in st.session_state:
    st.session_state.bunpro_credentials_set = False

if 'bunpro_data_loaded' not in st.session_state:
    st.session_state.bunpro_data_loaded = False

if "messages" not in st.session_state:
    st.session_state.messages = []

# Add credentials input in sidebar
with st.sidebar:
    st.title('🤖💬 Japanese Grammar Assistant / 日本語文法アシスタント')
    
    # Check if credentials are in secrets
    if not st.session_state.bunpro_credentials_set:
        if 'bunpro' in st.secrets:
            st.session_state.bunpro_email = st.secrets.bunpro.email
            st.session_state.bunpro_password = st.secrets.bunpro.password
            st.session_state.bunpro_credentials_set = True
            st.success("Bunpro credentials loaded from secrets!")
        else:
            st.session_state.bunpro_email = st.text_input("Bunpro Email:", type="default")
            st.session_state.bunpro_password = st.text_input("Bunpro Password:", type="password")
            if st.button("Save Credentials"):
                if st.session_state.bunpro_email and st.session_state.bunpro_password:
                    st.session_state.bunpro_credentials_set = True
                    st.success("Credentials saved!")
                else:
                    st.error("Please enter both email and password")

    # Show refresh button only if credentials are set
    if st.session_state.bunpro_credentials_set:
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

# Load Bunpro data only if credentials are set
if not st.session_state.bunpro_credentials_set:
    st.warning("Please set your Bunpro credentials in the sidebar first.")
    st.stop()

# Load Bunpro data
bunpro_data = load_bunpro_data()
if bunpro_data is None:
    st.warning("No Bunpro data found. Please click 'Refresh Bunpro Data' to fetch the latest data.")
    st.stop()

# When loading Bunpro data
bunpro_data = decode_unicode(bunpro_data)

# Create system prompt with Bunpro data
SYSTEM_PROMPT = f"""You are a Japanese language tutor with access to the following grammar points from Bunpro:
{json.dumps(bunpro_data, indent=2, ensure_ascii=False)}
Use this information to help answer questions about Japanese grammar."""

# with st.sidebar:
#     st.title('🤖💬 Japanese Grammar Assistant')
    # if 'GROP_API_KEY' in st.secrets.llm_creds:
    #     st.success('API key already provided!', icon='✅')
    #     openai.api_key = st.secrets.llm_creds['GROP_API_KEY']
    # else:
    #     openai.api_key = st.text_input('Enter OpenAI API token:', type='password')
        # if not (openai.api_key.startswith('sk-') and len(openai.api_key)==51):
        #     st.warning('Please enter your credentials!', icon='⚠️')
        # else:
        #     st.success('Proceed to entering your prompt message!', icon='👉')

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(decode_unicode(message["content"]))

if prompt := st.chat_input("日本語の文法について質問してください..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *[{"role": m["role"], "content": m["content"]}
                  for m in st.session_state.messages]
            ],
            stream=True):
            chunk = response.choices[0].delta.content or ""
            full_response += chunk
            message_placeholder.markdown(decode_unicode(full_response + "▌"))
        message_placeholder.markdown(decode_unicode(full_response))
    st.session_state.messages.append({"role": "assistant", "content": full_response})