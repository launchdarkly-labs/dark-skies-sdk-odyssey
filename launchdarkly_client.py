# launchdarkly_client.py

# Placeholder for LaunchDarkly integration
# This function can later evaluate a real flag using the LD Python SDK or REST API

import ldclient
from ldclient.config import Config
from ldclient import Context
import os
import logging

# configure logging for LD
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LaunchDarklyClient:
    def __init__(self, sdk_key=None):
        """
        Initialize LaunchDarkly client
        SDK key can be passed directly or set as environment variable LD_SDK_KEY
        """
        self.sdk_key = sdk_key or os.getenv('LD_SDK_KEY')
        self.client = None
        self.is_initialized = False
        
        if self.sdk_key:
            try:
                ldclient.set_config(Config(self.sdk_key))
                self.client = ldclient.get()
                self.is_initialized = True
                logger.info("LaunchDarkly client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize LaunchDarkly client: {e}")
                self.is_initialized = False
        else:
            logger.warning("No LaunchDarkly SDK key provided. Using default values.")
    
    def get_user_context(self, user_key="demo-player-001"):
        """Create a user context for flag evaluation"""
        return Context.builder(user_key).kind('user').name('Dark Skies Player').set('game', 'dark-skies').set('version', '1.0').build()
    
    def should_mute_sound(self, user_context=None):
        """
        Check if sound should be muted at game start
        Flag: mute-sound (boolean)
        Default: False (sound enabled)
        """
        if user_context is None:
            user_context = self.get_user_context()
        
        try:
            flag_value = self.client.variation("mute-sound-dark-skies", user_context, False)
            logger.info(f"mute-sound-dark-skies flag returned: {flag_value}")
            return flag_value
        except Exception as e:
            logger.error(f"Error evaluating mute-sound flag: {e}")
            return False
    
    def get_enabled_trivia_difficulties(self, user_context=None):
        """
        Get which trivia difficulty levels are enabled
        Flags: trivia-easy-enabled, trivia-medium-enabled, trivia-hard-enabled
        Returns: list of enabled difficulty levels
        """
        if user_context is None:
            user_context = self.get_user_context()
        
        enabled_difficulties = []
        
        try:
            # check each difficulty for flag
            if self.client.variation("trivia-easy-enabled", user_context, True):
                enabled_difficulties.append("easy")
            if self.client.variation("trivia-medium-enabled", user_context, True):
                enabled_difficulties.append("medium")
            if self.client.variation("trivia-hard-enabled", user_context, True):
                enabled_difficulties.append("hard")
            
            # fallback: if no difficulties are enabled, enable all
            if not enabled_difficulties:
                logger.warning("No trivia difficulties enabled, falling back to all difficulties")
                enabled_difficulties = ["easy", "medium", "hard"]
                
        except Exception as e:
            logger.error(f"Error evaluating trivia difficulty flags: {e}")
            enabled_difficulties = ["easy", "medium", "hard"]
        
        logger.info(f"Enabled trivia difficulties: {enabled_difficulties}")
        return enabled_difficulties
    
    def filter_trivia_by_difficulty(self, trivia_data, user_context=None):
        """
        Filter trivia questions based on enabled difficulty levels
        """
        enabled_difficulties = self.get_enabled_trivia_difficulties(user_context)
        
        filtered_trivia = [
            question for question in trivia_data 
            if question.get("difficulty", "easy") in enabled_difficulties
        ]
        
        # fallback: if no questions match, return all questions
        if not filtered_trivia:
            logger.warning("No trivia questions match enabled difficulties, returning all questions")
            return trivia_data
        
        logger.info(f"Filtered trivia: {len(filtered_trivia)} questions from {len(trivia_data)} total")
        return filtered_trivia
    
    def close(self):
        """Close the LaunchDarkly client"""
        if self.client:
            try:
                self.client.close()
                logger.info("LaunchDarkly client closed")
            except Exception as e:
                logger.error(f"Error closing LaunchDarkly client: {e}")