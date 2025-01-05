import streamlit as st
from openai import OpenAI

st.title("OpenAI Connection Test")

api_key = "sk-..." # We'll replace this with your actual key

# Initialize client button
if st.button("Initialize OpenAI Client"):
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.openai.com/v1")
        st.success("OpenAI client initialized successfully!")

        # Test the connection with a simple completion
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello"}]
        )
        st.success(f"Response received: {response.choices[0].message.content}")
    except Exception as e:
        st.error(f"Failed to initialize OpenAI client: {str(e)}")