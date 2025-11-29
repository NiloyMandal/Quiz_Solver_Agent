from langchain_core.tools import tool
import os
from google.cloud import speech_v1
from google.oauth2 import service_account
import requests
from pathlib import Path

@tool
def transcribe_audio(audio_url: str) -> str:
    """
    Download and transcribe an audio file to text using Google Speech-to-Text API.
    
    This tool downloads an audio file from a URL, then uses Google's Speech-to-Text
    service to convert the spoken words into text. Useful for solving tasks that
    require transcribing audio passphrases, voice messages, or spoken content.
    
    Args:
        audio_url (str): The URL of the audio file to download and transcribe.
                        Supports common formats like .mp3, .wav, .flac, .m4a
    
    Returns:
        str: The transcribed text from the audio file, or an error message if
             transcription fails.
    
    Example:
        >>> result = transcribe_audio("https://example.com/audio.mp3")
        >>> print(result)
        "the quick brown fox jumps over the lazy dog 42"
    """
    try:
        # Download the audio file
        print(f"\nDownloading audio from: {audio_url}")
        response = requests.get(audio_url, timeout=30)
        response.raise_for_status()
        
        # Determine file extension
        audio_ext = Path(audio_url).suffix or '.mp3'
        audio_filename = f"LLMFiles/audio{audio_ext}"
        
        # Create directory if it doesn't exist
        os.makedirs("LLMFiles", exist_ok=True)
        
        # Save the audio file
        with open(audio_filename, 'wb') as f:
            f.write(response.content)
        
        print(f"Audio saved to: {audio_filename}")
        
        # Try using Google Speech-to-Text API if credentials are available
        try:
            from google.cloud import speech
            
            client = speech.SpeechClient()
            
            # Read the audio file
            with open(audio_filename, 'rb') as audio_file:
                content = audio_file.read()
            
            audio = speech.RecognitionAudio(content=content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.MP3,
                language_code="en-US",
                enable_automatic_punctuation=False,
            )
            
            response = client.recognize(config=config, audio=audio)
            
            if response.results:
                transcript = response.results[0].alternatives[0].transcript
                print(f"Transcription: {transcript}")
                return transcript.strip()
            else:
                return "No speech detected in audio file"
                
        except Exception as google_error:
            print(f"Google Speech API failed: {google_error}")
            
            # Fallback to SpeechRecognition library
            try:
                import speech_recognition as sr
                from pydub import AudioSegment
                
                # Convert to WAV if needed
                if audio_ext.lower() != '.wav':
                    print("Converting audio to WAV format...")
                    audio = AudioSegment.from_file(audio_filename)
                    wav_filename = "LLMFiles/audio.wav"
                    audio.export(wav_filename, format="wav")
                    audio_filename = wav_filename
                
                recognizer = sr.Recognizer()
                with sr.AudioFile(audio_filename) as source:
                    audio_data = recognizer.record(source)
                
                # Try multiple recognition services
                try:
                    text = recognizer.recognize_google(audio_data)
                    print(f"Transcription (Google): {text}")
                    return text.strip()
                except:
                    try:
                        text = recognizer.recognize_sphinx(audio_data)
                        print(f"Transcription (Sphinx): {text}")
                        return text.strip()
                    except:
                        return "Could not transcribe audio - speech recognition failed"
                        
            except ImportError:
                return "Error: SpeechRecognition library not installed. Run: uv add SpeechRecognition pydub"
            except Exception as sr_error:
                return f"Transcription error: {str(sr_error)}"
    
    except requests.RequestException as e:
        return f"Failed to download audio: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"
