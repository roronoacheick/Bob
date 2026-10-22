import subprocess


class VoiceSpeaker:
    def __init__(self, voice_name="Thomas"):
        self.voice_name = voice_name


    def speak(self, text_to_speak):
        if not text_to_speak:
            return

        subprocess.run( 
            ["say", "-v", self.voice_name],
            input=text_to_speak,
            text=True,
            check=True,
        )


if __name__ == "__main__":
    voice_speaker_object = VoiceSpeaker()

    voice_speaker_object.speak("Bonjour, je suis Bob. Recherche YouTube lancée pour : recettes de cury.")
    voice_speaker_object.speak("- Cette phrase commence par un tiret, et je la lis quand même.")
    voice_speaker_object.speak("")
    print("Tests terminés")