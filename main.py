import streamlit as st
from openai import OpenAI

st.title("OpenAI Connection Test")

# Add descriptive information
st.info("This page tests the connection to OpenAI's API")

# Initialize session state for API key if not exists
if 'api_key' not in st.session_state:
    st.session_state.api_key = ''

# API key input field
api_key = st.text_input("Enter your OpenAI API key:", 
                        type="password",
                        value=st.session_state.api_key)

if st.button("Initialize OpenAI Client"):
    if not api_key:
        st.error("❌ Please enter your OpenAI API key.")
    else:
        try:
            # Store API key in session state
            st.session_state.api_key = api_key

            # Create client with API key
            client = OpenAI(api_key=api_key)

            # Test with minimal completion request
            st.info("Testing API connection...")
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Using 3.5-turbo as it's more reliable for testing
                messages=[
                    {"role": "user", "content": "Hi"}
                ]
            )

            if response.choices[0].message.content:
                st.success("✅ Successfully connected to OpenAI API!")
                st.write("API Response:", response.choices[0].message.content)
        except Exception as e:
            st.error("❌ Connection failed")
            st.error(f"Error details: {str(e)}")
            st.info("💡 Check your OpenAI API key and network connection.")