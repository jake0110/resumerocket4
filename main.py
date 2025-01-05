import streamlit as st
from openai import OpenAI

st.title("OpenAI Connection Test")

# Initialize client button
if st.button("Initialize OpenAI Client"):
    try:
        # Simple client initialization without any extra parameters
        client = OpenAI()
        st.success("OpenAI client initialized successfully!")

        # Test the connection with a simple completion
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello, are you there?"}],
            max_tokens=10
        )
        st.success(f"Successfully connected to OpenAI! Response: {response.choices[0].message.content}")
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.info("Make sure you have set your OPENAI_API_KEY in the environment variables")