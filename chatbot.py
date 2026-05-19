import streamlit as st
import time
import os
import re
from groq import Groq

def get_api_key():
    # 1. Try Streamlit's built-in secrets (looks in .streamlit/secrets.toml)
    try:
        if "API_KEY" in st.secrets:
            return st.secrets["API_KEY"]
    except FileNotFoundError:
        pass
    
    # 2. Try manually reading from the user's custom toml paths
    custom_paths = [
        os.path.join("my_venv", "Scripts", "secrets.toml"),
        os.path.join("my_venv", "secrets.toml")
    ]
    for path in custom_paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                # Use regex to find API_KEY="..."
                match = re.search(r'API_KEY\s*=\s*[\'"]([^\'"]+)[\'"]', content)
                if match:
                    return match.group(1)
                    
    # 3. Fallback to environment variables
    return os.getenv("API_KEY")

API_KEY = get_api_key()
# Set up the page configuration
st.set_page_config(page_title="Axora - AI Chatbot", page_icon="🤖")

st.title("🤖 Axora - AI Chatbot")
st.write("Welcome to Axora! How can I help you today?")

# Try to configure the AI model if the API key is provided
try:
    if API_KEY and API_KEY.strip() != "":
        client = Groq(api_key=API_KEY)
        model = "llama-3.3-70b-versatile"
    else:
        client = None
        model = None
except Exception as e:
    st.error(f"Error configuring AI: {e}")
    client = None
    model = None

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Type your message here..."):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # --- AI INTEGRATION POINT ---
        if client is None:
            # Fallback if API key is not added yet
            simulated_response = "Oops! I'm running in simulation mode because you haven't added an API Key yet. Please add your key at the top of the file!"
            for chunk in simulated_response.split():
                full_response += chunk + " "
                time.sleep(0.05)
                message_placeholder.markdown(full_response + "▌")
        else:
            # Actual API call to Groq
            try:
                # We send the entire chat history for context
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    stream=True
                )
                
                # Stream the real AI response
                for chunk in response:
                    content = chunk.choices[0].delta.content
                    if content:
                        full_response += content
                        message_placeholder.markdown(full_response + "▌")
            except Exception as e:
                full_response = f"An error occurred: {e}"
        # ----------------------------

        # Display the final response without the cursor
        message_placeholder.markdown(full_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
