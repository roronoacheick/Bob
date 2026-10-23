from groq import Groq
from dotenv import load_dotenv
import os
import json

from action_executor import ActionExecutor


class ConversationAgent:
    def __init__(self):
        load_dotenv()
        self.groq_client = Groq(api_key=os.environ["GROQ_KEY"])
        self.action_executor_object = ActionExecutor()
        self.tools_description = ActionExecutor.get_tools_description()
        self.conversation_history = [
            {
                "role": "system",
                "content": self.read_file(file_path="./context.txt"),
            }
        ]


    @staticmethod
    def read_file(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()


    def get_conversation_history(self):
        return [
            message
            for message in self.conversation_history[1:]
            if message["role"] in ("user", "assistant") and message.get("content")
        ]


    def update_conversation_history(self, role, text_interaction):
        self.conversation_history.append({"role": role, "content": text_interaction})


    def transcribe(self, audio_interaction):
        transcription = self.groq_client.audio.transcriptions.create(
            file=("audio.wav", audio_interaction),
            model="whisper-large-v3-turbo",
            language="fr",
            temperature=0.0,
        )
        return transcription.text


    def request_llm(self):
        return self.groq_client.chat.completions.create(
            messages=self.conversation_history,
            model="qwen/qwen3.8-27b",
            tools=self.tools_description,
            include_reasoning=False,
        ).choices[0].message


    def add_tool_calls_to_history(self, llm_message):
        tool_calls = []
        for tool_call in llm_message.tool_calls:
            tool_calls.append({
                "id": tool_call.id,
                "type": "function",
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments,
                },
            })

        self.conversation_history.append({
            "role": "assistant",
            "content": llm_message.content,
            "tool_calls": tool_calls,
        })


    def execute_tool_calls(self, tool_calls):
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            tool_arguments = json.loads(tool_call.function.arguments)

            tool_result = self.action_executor_object.execute_action(tool_name, tool_arguments)

            self.conversation_history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_name,
                "content": tool_result,
            })


    def ask_llm(self, text_interaction):
        self.update_conversation_history(role="user", text_interaction=text_interaction)

        llm_message = self.request_llm()

        while llm_message.tool_calls:
            self.add_tool_calls_to_history(llm_message)
            self.execute_tool_calls(llm_message.tool_calls)
            llm_message = self.request_llm()

        response = llm_message.content
        self.update_conversation_history(role="assistant", text_interaction=response)
        return response



if __name__ == "__main__":
    conversation_agent_object = ConversationAgent()
    print("Parle à Jarvis (tape 'quit' pour arrêter)")

    while True:
        text_interaction = input("\nToi : ")
        if text_interaction == "quit":
            break
        print("Bob :", conversation_agent_object.ask_llm(text_interaction))

    print("\n--- Historique complet envoyé au LLM ---")
    print(json.dumps(conversation_agent_object.conversation_history, indent=2, ensure_ascii=False))