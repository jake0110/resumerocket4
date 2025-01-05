import streamlit as st
import requests
import json

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
            # Direct API request without using the OpenAI client
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": "Test"}],
                "max_tokens": 10
            }

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                st.success("✅ Successfully connected to OpenAI API!")
                st.write("Test response received:", result['choices'][0]['message']['content'])
            else:
                st.error("❌ API request failed")
                st.error(f"Status code: {response.status_code}")
                st.error(f"Error details: {response.text}")

        except requests.exceptions.RequestException as e:
            st.error("❌ Connection failed")
            error_msg = str(e)
            st.error(f"Network error: {error_msg}")

            # Provide helpful guidance
            st.info("💡 Network Troubleshooting Tips:")
            st.markdown("""
            1. Check if you can access api.openai.com in your browser
            2. Verify your internet connection
            3. Try using a different network if possible
            4. If you're behind a corporate network, check with your IT department
            """)

        except Exception as e:
            st.error("❌ Unexpected error")
            st.error(f"Error details: {str(e)}")
            st.info("💡 Please verify your API key and try again")