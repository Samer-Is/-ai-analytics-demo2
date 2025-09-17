"""
Context Length Management for AI Data Analytics Tool
Handles conversation history truncation to prevent OpenAI API context limits
"""

import tiktoken
from typing import List, Dict, Any

class ContextManager:
    """Manages conversation context to prevent token limit exceeded errors"""
    
    def __init__(self, model_name: str = "gpt-4o", max_tokens: int = 120000):
        """
        Initialize context manager
        
        Args:
            model_name: OpenAI model name for token counting
            max_tokens: Maximum tokens to allow (buffer under 128k limit)
        """
        self.model_name = model_name
        self.max_tokens = max_tokens
        try:
            self.encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            # Fallback to cl100k_base for unknown models
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in a text string"""
        return len(self.encoding.encode(text))
    
    def count_message_tokens(self, messages: List[Dict[str, str]]) -> int:
        """Count total tokens in a list of messages"""
        total = 0
        for message in messages:
            # Add tokens for role and content
            total += self.count_tokens(message.get("role", ""))
            total += self.count_tokens(message.get("content", ""))
            # Add overhead tokens for message formatting
            total += 4  # Approximate overhead per message
        return total
    
    def truncate_conversation(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Truncate conversation to fit within token limits
        Keeps system message and recent messages while removing old ones
        """
        if not messages:
            return messages
        
        total_tokens = self.count_message_tokens(messages)
        
        if total_tokens <= self.max_tokens:
            return messages
        
        # Always keep system message if it exists
        result = []
        system_messages = [msg for msg in messages if msg.get("role") == "system"]
        if system_messages:
            result.extend(system_messages)
        
        # Keep the most recent user and assistant messages
        non_system_messages = [msg for msg in messages if msg.get("role") != "system"]
        
        # Start from the end and work backwards
        truncated_messages = []
        current_tokens = self.count_message_tokens(result)
        
        for message in reversed(non_system_messages):
            message_tokens = self.count_tokens(message.get("content", "")) + 4
            if current_tokens + message_tokens <= self.max_tokens:
                truncated_messages.insert(0, message)
                current_tokens += message_tokens
            else:
                break
        
        result.extend(truncated_messages)
        
        # Add a summary message if we truncated content
        if len(result) < len(messages):
            summary_msg = {
                "role": "assistant",
                "content": f"[Previous conversation history truncated - keeping {len(result)} of {len(messages)} messages to manage context length]"
            }
            result.insert(-1 if len(result) > 1 else 0, summary_msg)
        
        return result
    
    def prepare_messages_for_api(self, messages: List[Dict[str, str]], system_prompt: str = None) -> List[Dict[str, str]]:
        """
        Prepare messages for OpenAI API call with context management
        
        Args:
            messages: List of conversation messages
            system_prompt: Optional system prompt to prepend
            
        Returns:
            Truncated and formatted messages ready for API
        """
        # Add system prompt if provided
        if system_prompt:
            system_msg = {"role": "system", "content": system_prompt}
            messages = [system_msg] + [msg for msg in messages if msg.get("role") != "system"]
        
        # Truncate if needed
        truncated_messages = self.truncate_conversation(messages)
        
        return truncated_messages
