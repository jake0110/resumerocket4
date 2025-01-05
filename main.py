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
            # Create OpenAI client with minimal configuration
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.openai.com/v1"  # Explicitly set the base URL
            )

            # Test with a simple completion request
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10  # Limit response size for quick testing
            )

            st.success("✅ Successfully connected to OpenAI API!")
            st.write("Response:", response.choices[0].message.content)

        except Exception as e:
            st.error("❌ Connection failed")
            error_msg = str(e)
            st.error(f"Error details: {error_msg}")

            # Provide more specific guidance based on the error
            if "proxies" in error_msg.lower():
                st.info("💡 Try clearing your browser cache and refreshing the page")
            elif "invalid" in error_msg.lower() and "api" in error_msg.lower():
                st.info("💡 Please check if your API key is valid")
            else:
                st.info("💡 Make sure you have a stable internet connection")