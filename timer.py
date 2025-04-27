from config import DEFAULT_TIME_LIMIT_SECONDS, TOKENS_PER_SECOND

class TimerSystem:
    """
    System to track and enforce time limits in debates
    """
    def __init__(self, time_limit_seconds=DEFAULT_TIME_LIMIT_SECONDS):
        self.time_limit = time_limit_seconds
        self.time_used = 0
        
    def estimate_response_time(self, response_length: int) -> float:
        """
        Converts response token length to simulated time
        
        Args:
            response_length: Length of response in tokens
            
        Returns:
            float: Estimated time in seconds
        """
        estimated_seconds = response_length / TOKENS_PER_SECOND
        return estimated_seconds
    
    def enforce_limits(self, agent_response: str, max_tokens: int = 800) -> str:
        """
        Prevents excessively long responses
        
        Args:
            agent_response: The full response from the agent
            max_tokens: Maximum allowed tokens
            
        Returns:
            str: Truncated response if needed
        """
        # Simplified token counting - in production we'd use a proper tokenizer
        tokens = len(agent_response.split())
        
        if tokens > max_tokens:
            # Truncate and add note about time limit
            words = agent_response.split()
            truncated = " ".join(words[:max_tokens])
            print(agent_response)  # Show full response in console
            return truncated + "\n[Time limit reached]"
        
        # Update time used
        self.time_used += self.estimate_response_time(tokens)
        print(agent_response)  # Show full response in console
        return agent_response
    
    def reset(self):
        """Reset the timer for a new round"""
        self.time_used = 0
        
    def time_remaining(self) -> float:
        """Returns remaining time in seconds"""
        return max(0, self.time_limit - self.time_used)
