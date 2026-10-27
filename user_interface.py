import streamlit as st

from llm_agent import ConversationAgent
from voice_speaker import VoiceSpeaker


class UserInterface:
    def __init__(self):
        st.set_page_config(page_title="Bob")
        st.title("Bob")
        self.conversation_agent_object = self.get_persistant_conversation_agent()
        self.voice_speaker_object = VoiceSpeaker()


    def get_persistant_conversation_agent(self):
        if "conversation_agent_object" not in st.session_state:
            st.session_state.conversation_agent_object = ConversationAgent()

        return st.session_state.conversation_agent_object


    @staticmethod
    def display_message(message):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


    def show_discussion_history(self):
        for message in self.conversation_agent_object.get_conversation_history():
            self.display_message(message)


    def get_text_interaction(self, user_interaction):
        if user_interaction.audio:
            return self.conversation_agent_object.transcribe(user_interaction.audio.getvalue())

        return user_interaction.text


    def run(self):
        user_interaction = st.chat_input(
            "Parle-moi ou écris-moi...",
            accept_audio=True,
        )

        response = None
        if user_interaction:
            with st.spinner("Bob réfléchit..."):
                text_interaction = self.get_text_interaction(user_interaction)
                response = self.conversation_agent_object.ask_llm(text_interaction)

        self.show_discussion_history()
        self.voice_speaker_object.speak(response)



if __name__ == "__main__":
    user_interface_object = UserInterface()
    user_interface_object.run()