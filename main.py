import streamlit as st
from openai import OpenAI

st.title("OpenAI Connection Test")

def init_openai():
    try:
        client = OpenAI()  # This will automatically use OPENAI_API_KEY from environment

        # Add a simple test message
        st.info("Testing connection...")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": "Say hello"}
            ]
        )

        if response and response.choices:
            st.success("✅ Connection successful!")
            st.write("Response:", response.choices[0].message.content)
        else:
            st.error("❌ No response received from OpenAI")

    except Exception as e:
        st.error("❌ Connection failed")
        st.error(str(e))
        if "api_key" in str(e).lower():
            st.info("💡 Make sure OPENAI_API_KEY is set in your environment variables")

# Initialize client button
if st.button("Initialize OpenAI Client"):
    init_openai()