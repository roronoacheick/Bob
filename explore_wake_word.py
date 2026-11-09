from voice_listener import VoiceListener
from voice_speaker import VoiceSpeaker
from llm_agent import ConversationAgent

voice_listener_object = VoiceListener()
voice_speaker_object = VoiceSpeaker()
conversation_agent_object = ConversationAgent()

print("Bob écoute. Dis « Dis Bob » suivi de ta demande (Ctrl + C pour arrêter).")
waiting_for_command = False

while True:
    audio_interaction = voice_listener_object.listen_for_phrase()
    if audio_interaction is None:
        waiting_for_command = False
        continue

    text_interaction = conversation_agent_object.transcribe(audio_interaction)
    print("Entendu :", text_interaction)

    if waiting_for_command:
        command = text_interaction
        waiting_for_command = False
    else:
        command = voice_listener_object.extract_command(text_interaction)

    if command is None:
        continue

    if command == "":
        voice_speaker_object.speak("Oui ?")
        waiting_for_command = True
        continue

    response = conversation_agent_object.ask_llm(command)
    print("Bob :", response)
    voice_speaker_object.speak(response)