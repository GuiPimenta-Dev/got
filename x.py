from groq import Groq

client = Groq()
completion = client.chat.completions.create(
    model="gemma-7b-it",
    messages=[{"role": "user", "content": "Eu te amo!"}],
    temperature=1,
    max_tokens=1024,
    top_p=1,
    stream=False,
    stop=None,
)

print(completion.choices[0].message.content)
