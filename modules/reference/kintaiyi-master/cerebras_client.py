import os
from cerebras.cloud.sdk import Cerebras

# Default model to use across all functions
#DEFAULT_MODEL = "deepseek-r1-distill-llama-70b" # Updated to lowercase to match common Cerebras model IDs
DEFAULT_MODEL = "qwen-3-235b-a22b-thinking-2507"


class CerebrasClient:
    def __init__(self, api_key):
        # This client now strictly requires an api_key to be passed by the caller.
        # The caller (cerebras_chat_main.py) is responsible for sourcing this key.
        if not api_key:
            # This should ideally be caught before calling, but as a safeguard.
            raise ValueError("CerebrasClient must be initialized with an API key.")
        
        # Directly use the provided api_key for Cerebras SDK initialization.
        self.client = Cerebras(api_key=api_key)

    def get_chat_completion(self, messages, model=DEFAULT_MODEL, **kwargs):
        # messages is expected to be a list of message dicts, e.g.:
        # [{"role": "system", "content": "You are helpful"},
        #  {"role": "user", "content": "Hello!"}]
        # **kwargs will capture any other parameters like max_completion_tokens, temperature, etc.
        
        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=model,
            **kwargs # Pass through any additional arguments
            # stream=True # Consider adding streaming support later
        )
        return chat_completion

    # Text completion can be kept if desired, but chat is the focus
    def get_text_completion(self, user_message, model=DEFAULT_MODEL):
        text_completion = self.client.completions.create(
            prompt=user_message,
            model=model,
            max_completion_tokens=20480, # Example, can be configured
            top_p=1
        )
        return text_completion

# We will primarily use the CerebrasClient class directly in the Streamlit app. 
