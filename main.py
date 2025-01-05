import streamlit as st
from openai import OpenAI

st.title("OpenAI Connection Test")

# Add descriptive information
st.info("This page tests the connection to OpenAI's API")

# API key input field
api_key = st.text_input("Enter your OpenAI API key:", type="password")

if st.button("Initialize OpenAI Client"):
    if not api_key:
        st.error("❌ Please enter your OpenAI API key")
    else:
        try:
            # Basic client initialization with only the API key
            client = OpenAI()
            client.api_key = api_key

            # Simple test request
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test"}]
            )

            if response:
                st.success("✅ Successfully connected to OpenAI API!")
                st.write("Test response received:", response.choices[0].message.content)

        except Exception as e:
            error_msg = str(e)
            st.error("❌ Connection failed")
            st.error(f"Error details: {error_msg}")

            # Provide helpful guidance
            st.info("💡 Tips for troubleshooting:")
            st.markdown("""
            1. Verify your API key is correct and active
            2. Check your internet connection
            3. Try accessing api.openai.com directly in your browser
            """)