client = OpenAI()  # Using environment variables for configuration
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a precise resume parser..."},
        {"role": "user", "content": prompt}
    ],
    response_format={"type": "json_object"}
)