from openai import OpenAI

client = OpenAI(
    api_key="sk-proj-xxxxxxxxxxxxxxxxxxxx",
    project="proj_xxxxxxxxxxxxxxxxxxx"
)

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Say hello!"}]
)

print(response.choices[0].message.content)
