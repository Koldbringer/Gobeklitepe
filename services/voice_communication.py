"""
Voice Communication Module for HVAC CRM/ERP System

This module provides functionality for voice-based communication with clients,
including text-to-speech, speech-to-text, and voice analysis.
"""

import os
import logging
import base64
import json
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional, Union, Tuple
import io
import tempfile

from services import communication_service
from utils import db

# Configure logging
logger = logging.getLogger(__name__)

# Load configuration from environment variables
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_BASE_URL = os.getenv("ELEVENLABS_BASE_URL", "https://api.elevenlabs.io/v1")
ENABLE_VOICE = os.getenv("ENABLE_VOICE", "False").lower() == "true"

# Default voice settings
DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice
DEFAULT_MODEL_ID = "eleven_multilingual_v2"
DEFAULT_STABILITY = 0.5
DEFAULT_SIMILARITY_BOOST = 0.75
DEFAULT_STYLE = 0.0
DEFAULT_USE_SPEAKER_BOOST = True


class TextToSpeech:
    """Class for converting text to speech using ElevenLabs API."""
    
    @staticmethod
    def generate_speech(
        text: str,
        voice_id: str = DEFAULT_VOICE_ID,
        model_id: str = DEFAULT_MODEL_ID,
        stability: float = DEFAULT_STABILITY,
        similarity_boost: float = DEFAULT_SIMILARITY_BOOST,
        style: float = DEFAULT_STYLE,
        use_speaker_boost: bool = DEFAULT_USE_SPEAKER_BOOST
    ) -> Optional[bytes]:
        """
        Generate speech from text using ElevenLabs API.
        
        Returns the audio data as bytes or None if an error occurs.
        """
        if not ENABLE_VOICE:
            logger.warning("Voice functionality is disabled.")
            return None
        
        if not ELEVENLABS_API_KEY:
            logger.error("ElevenLabs API key is not set.")
            return None
        
        try:
            url = f"{ELEVENLABS_BASE_URL}/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": ELEVENLABS_API_KEY
            }
            
            data = {
                "text": text,
                "model_id": model_id,
                "voice_settings": {
                    "stability": stability,
                    "similarity_boost": similarity_boost,
                    "style": style,
                    "use_speaker_boost": use_speaker_boost
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                return response.content
            else:
                logger.error(f"Error generating speech: {response.status_code} - {response.text}")
                return None
        
        except Exception as e:
            logger.error(f"Error generating speech: {str(e)}")
            return None
    
    @staticmethod
    def get_available_voices() -> List[Dict[str, Any]]:
        """
        Get a list of available voices from ElevenLabs API.
        """
        if not ENABLE_VOICE:
            logger.warning("Voice functionality is disabled.")
            return []
        
        if not ELEVENLABS_API_KEY:
            logger.error("ElevenLabs API key is not set.")
            return []
        
        try:
            url = f"{ELEVENLABS_BASE_URL}/voices"
            
            headers = {
                "Accept": "application/json",
                "xi-api-key": ELEVENLABS_API_KEY
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                voices = response.json().get("voices", [])
                return voices
            else:
                logger.error(f"Error getting voices: {response.status_code} - {response.text}")
                return []
        
        except Exception as e:
            logger.error(f"Error getting voices: {str(e)}")
            return []
    
    @staticmethod
    def save_audio_file(audio_data: bytes, filename: str = None) -> str:
        """
        Save audio data to a file.
        
        Returns the path to the saved file.
        """
        if not audio_data:
            return ""
        
        try:
            if not filename:
                filename = f"speech_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
            
            # Create audio directory if it doesn't exist
            os.makedirs("static/audio", exist_ok=True)
            
            file_path = f"static/audio/{filename}"
            
            with open(file_path, "wb") as f:
                f.write(audio_data)
            
            return file_path
        
        except Exception as e:
            logger.error(f"Error saving audio file: {str(e)}")
            return ""
    
    @staticmethod
    def get_audio_data_uri(audio_data: bytes) -> str:
        """
        Convert audio data to a data URI for embedding in HTML.
        
        Returns a data URI string.
        """
        if not audio_data:
            return ""
        
        try:
            base64_audio = base64.b64encode(audio_data).decode("utf-8")
            return f"data:audio/mpeg;base64,{base64_audio}"
        
        except Exception as e:
            logger.error(f"Error creating audio data URI: {str(e)}")
            return ""


class SpeechToText:
    """Class for converting speech to text (placeholder for future implementation)."""
    
    @staticmethod
    def transcribe_audio(audio_data: bytes) -> str:
        """
        Transcribe audio data to text.
        
        This is a placeholder for future implementation.
        """
        if not ENABLE_VOICE:
            logger.warning("Voice functionality is disabled.")
            return ""
        
        # This is a placeholder - in a real implementation, you would use a
        # speech-to-text service like Google Speech-to-Text, AWS Transcribe, etc.
        logger.info("Speech-to-text functionality is not yet implemented.")
        return "This is a placeholder for speech-to-text transcription."


class VoiceAnalysis:
    """Class for analyzing voice data (placeholder for future implementation)."""
    
    @staticmethod
    def analyze_sentiment(audio_data: bytes) -> Dict[str, Any]:
        """
        Analyze the sentiment of voice data.
        
        This is a placeholder for future implementation.
        """
        if not ENABLE_VOICE:
            logger.warning("Voice functionality is disabled.")
            return {}
        
        # This is a placeholder - in a real implementation, you would use a
        # voice analysis service or library
        logger.info("Voice sentiment analysis is not yet implemented.")
        return {
            "sentiment": "neutral",
            "confidence": 0.7,
            "emotions": {
                "neutral": 0.7,
                "happy": 0.2,
                "sad": 0.05,
                "angry": 0.05
            }
        }


# Common voice communication functions
def generate_voice_message(
    client_id: int,
    text: str,
    voice_id: str = DEFAULT_VOICE_ID
) -> Dict[str, Any]:
    """
    Generate a voice message for a client and save it as a communication.
    
    Returns a dictionary with the communication ID and audio file path.
    """
    if not ENABLE_VOICE:
        logger.warning("Voice functionality is disabled.")
        return {"success": False, "error": "Voice functionality is disabled."}
    
    try:
        # Generate speech
        audio_data = TextToSpeech.generate_speech(text, voice_id=voice_id)
        
        if not audio_data:
            return {"success": False, "error": "Failed to generate speech."}
        
        # Save audio file
        filename = f"client_{client_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
        file_path = TextToSpeech.save_audio_file(audio_data, filename=filename)
        
        if not file_path:
            return {"success": False, "error": "Failed to save audio file."}
        
        # Create attachment
        attachments = [{
            "filename": filename,
            "file_path": file_path,
            "content_type": "audio/mpeg"
        }]
        
        # Save communication
        communication_id = communication_service.CommunicationManager.save_communication(
            client_id=client_id,
            comm_type="voice",
            direction="wychodzący",
            content=text,
            category="wiadomość głosowa",
            attachments=attachments
        )
        
        if not communication_id:
            return {"success": False, "error": "Failed to save communication."}
        
        return {
            "success": True,
            "communication_id": communication_id,
            "file_path": file_path,
            "data_uri": TextToSpeech.get_audio_data_uri(audio_data)
        }
    
    except Exception as e:
        logger.error(f"Error generating voice message: {str(e)}")
        return {"success": False, "error": str(e)}


def convert_text_to_voice_for_client(client_id: int, text: str) -> Dict[str, Any]:
    """
    Convert text to voice for a specific client, using their preferred voice settings.
    
    Returns a dictionary with the audio data URI and file path.
    """
    if not ENABLE_VOICE:
        logger.warning("Voice functionality is disabled.")
        return {"success": False, "error": "Voice functionality is disabled."}
    
    try:
        # Get client voice preferences (placeholder)
        # In a real implementation, you would get this from the database
        voice_id = DEFAULT_VOICE_ID
        
        # Generate speech
        audio_data = TextToSpeech.generate_speech(text, voice_id=voice_id)
        
        if not audio_data:
            return {"success": False, "error": "Failed to generate speech."}
        
        # Save audio file
        filename = f"client_{client_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
        file_path = TextToSpeech.save_audio_file(audio_data, filename=filename)
        
        return {
            "success": True,
            "file_path": file_path,
            "data_uri": TextToSpeech.get_audio_data_uri(audio_data)
        }
    
    except Exception as e:
        logger.error(f"Error converting text to voice: {str(e)}")
        return {"success": False, "error": str(e)}


# Initialize the module
def init():
    """Initialize the voice communication module."""
    if ENABLE_VOICE:
        if not ELEVENLABS_API_KEY:
            logger.warning("ElevenLabs API key is not set. Voice functionality will be limited.")
        else:
            logger.info("Voice communication module initialized")
    else:
        logger.info("Voice communication module is disabled")


# Initialize the module when imported
init()
