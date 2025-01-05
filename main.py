import streamlit as st
from openai import OpenAI

st.title("OpenAI Connection Test")

# Show status information
st.info("This page tests the connection to OpenAI's API")

if st.button("Initialize OpenAI Client"):
    try:
        # Create client - simplest possible initialization
        client = OpenAI()

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
        st.info("💡 Make sure your OpenAI API key is correctly set")