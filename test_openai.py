from openai import OpenAI

client = OpenAI(
    api_key="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",
    project="proj_7EqGQg2RKl5FeRaNsYxzC2w"
)

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Say hello!"}]
)

print(response.choices[0].message.content)
