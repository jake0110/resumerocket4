import streamlit as st
import os
from openai import OpenAI

# Initialize OpenAI client with direct environment variable
client = None
api_key = "YOUR-API-KEY-HERE"  # Replace this with your actual API key

# Configure page
st.title("OpenAI Connection Test")

# Initialize client button
if st.button("Initialize OpenAI Client"):
    try:
        client = OpenAI(api_key=api_key)
        st.success("OpenAI client initialized successfully!")
    except Exception as e:
        st.error(f"Failed to initialize OpenAI client: {str(e)}")

# Test OpenAI Connection
if client and st.button("Test OpenAI Connection"):
    try:
        # Simple test completion
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello, are you there?"}],
            max_tokens=10
        )
        st.success(f"Successfully connected to OpenAI! Response: {response.choices[0].message.content}")
    except Exception as e:
        st.error(f"Failed to connect to OpenAI: {str(e)}")