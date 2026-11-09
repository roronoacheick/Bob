import io
import wave

import numpy as np
import sounddevice as sd


class VoiceListener:
    def __init__(self, volume_threshold=300, silence_duration=1.0, max_waiting_duration=5.0, max_phrase_duration=15.0, wake_word="Bob"):
        self.sample_rate = 16000      # 16 000 mesures par seconde, la fréquence de Whisper
        self.block_duration = 0.1     # on analyse le micro par tranches de 0,1 seconde
        self.volume_threshold = volume_threshold
        self.silence_duration = silence_duration
        self.max_waiting_duration = max_waiting_duration
        self.max_phrase_duration = max_phrase_duration
        self.wake_word = wake_word.lower()

    @staticmethod
    def get_volume(audio_block):
        # Conversion en int32 : abs(-32768) ne tient pas dans un int16
        return np.abs(audio_block.astype(np.int32)).mean()


    def convert_to_wav(self, audio_data):
        # On fabrique un vrai fichier WAV, mais en mémoire, sans l'écrire sur le disque
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        return wav_buffer.getvalue()


    def listen_for_phrase(self):
        block_size = int(self.sample_rate * self.block_duration)
        phrase_blocks = []
        waiting_time = 0
        silence_time = 0

        with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype="int16") as microphone_stream:
            while True:
                audio_block, _ = microphone_stream.read(block_size)
                is_speaking = self.get_volume(audio_block) > self.volume_threshold

                # Phase 1 : personne ne parle encore, on attend (mais pas indéfiniment)
                if not phrase_blocks:
                    if is_speaking:
                        phrase_blocks.append(audio_block)
                    else:
                        waiting_time += self.block_duration
                        if waiting_time >= self.max_waiting_duration:
                            return None
                    continue

                # Phase 2 : une phrase est en cours, on enregistre jusqu'à un silence assez long
                phrase_blocks.append(audio_block)
                if is_speaking:
                    silence_time = 0
                else:
                    silence_time += self.block_duration

                phrase_time = len(phrase_blocks) * self.block_duration
                if silence_time >= self.silence_duration or phrase_time >= self.max_phrase_duration:
                    break

        return self.convert_to_wav(np.concatenate(phrase_blocks))


    def extract_command(self, text_interaction):
        # None : on ne parlait pas à Bob / "" : "Dis Bob" seul / sinon : la demande
        if not text_interaction:
            return None

        wake_word_position = text_interaction.lower().find(self.wake_word)
        if wake_word_position == -1:
            return None

        command = text_interaction[wake_word_position + len(self.wake_word):]
        return command.strip(" ,.!?;:")



if __name__ == "__main__":
    voice_listener_object = VoiceListener()

    sample_transcriptions = [
        "Dis Bob, ouvre YouTube.",
        "Bob mets-moi des vidéos de recettes de mafé",
        "Dis Bob.",
        "On mange quoi ce soir ?",
        "Sous-titres réalisés par la communauté d'Amara.org",
        "",
    ]

    for text_interaction in sample_transcriptions:
        command = voice_listener_object.extract_command(text_interaction)
        print(repr(text_interaction), "→", repr(command))