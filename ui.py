import chainlit as cl
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)

settings = {
    "model": "lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF",
    "temperature": 0.7,
    "max_tokens": 500,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0
}

@cl.on_chat_start
def start_chat():
    print("Chat started.")
    cl.user_session.set("message_history", [{"role": "system", "content": "You are an advanced artificial intelligence. You are a personel dietitian. You always provide well-reasoned answers that are both correct and helpful."}])
    print("Initial message history set.")

@cl.on_message
async def main(message: cl.Message):
    print(f"Received message: {message.content}")
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})

    msg = cl.Message(content="")
    await msg.send()
    print("Initial message sent.")

    try:
        response = client.chat.completions.create(
            messages=message_history, 
            stream=True, 
            **settings
        )
        print("Response received.")

        for part in response:
            token = part.choices[0].delta.content
            if token:
                print(f"Streaming token: {token}")
                await msg.stream_token(token)

        message_history.append({"role": "assistant", "content": msg.content})
        cl.user_session.set("message_history", message_history)
        print("Message history updated.")

        await msg.update()
        print("Message updated.")
    except Exception as e:
        await msg.update()
        print(f"An error occurred: {str(e)}")