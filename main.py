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
            client = OpenAI(api_key=api_key)

            # Test with a simple completion request
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )

            st.success("✅ Successfully connected to OpenAI API!")
            st.write("Response:", response.choices[0].message.content)

        except Exception as e:
            st.error("❌ Connection failed")
            error_msg = str(e)
            st.error(f"Error details: {error_msg}")

            # Provide more specific guidance based on the error
            if "proxy" in error_msg.lower() or "proxies" in error_msg.lower():
                st.info("💡 The connection might be blocked. Try using a different network connection or contact your network administrator.")
            elif "invalid" in error_msg.lower() and "api" in error_msg.lower():
                st.info("💡 Please check if your API key is valid")
            else:
                st.info("💡 Check your network connection and try again")