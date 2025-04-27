from typing import List, Dict, Any

class AgentMemory:
    """
    Memory system for debate agents to maintain context across debate rounds
    """
    def __init__(self):
        self.debate_history = []  # Stores all previous rounds' arguments
        self.key_points_made = []  # Tracks main points already covered
        self.opponent_points = []  # Tracks opponent's key arguments
        
    def update(self, debate_round: Dict[str, Any]) -> None:
        """
        Updates the agent's memory with information from a new debate round
        
        Args:
            debate_round: Dictionary containing the round's statements and metadata
        """
        self.debate_history.append(debate_round)
        
        # If the round contains a position X statement, add it to opponent points
        # This assumes agent is position Y - will be ignored for position X agents
        if debate_round.get('position_x_statement'):
            self.opponent_points.append(debate_round['position_x_statement'])
            
        # If the round contains a position Y statement, add it to key points
        # This assumes agent is position Y - for position X agents, we track opponent's points
        if debate_round.get('position_y_statement'):
            self.key_points_made.append(debate_round['position_y_statement'])
    
    def get_context_summary(self, max_tokens: int = 2000) -> str:
        """
        Creates a condensed summary of the debate history for context
        
        Args:
            max_tokens: Maximum tokens to include in summary
            
        Returns:
            str: Formatted debate history summary
        """
        # Simplified implementation - in a real system, we would use
        # more sophisticated summarization techniques
        summary = "Debate History Summary:\n\n"
        
        # Add the most recent rounds first (most important)
        for i, round_data in enumerate(reversed(self.debate_history[-3:])):
            round_num = len(self.debate_history) - i
            summary += f"Round {round_num}:\n"
            if round_data.get('position_x_statement'):
                summary += f"Position X: {round_data['position_x_statement'][:200]}...\n"
            if round_data.get('position_y_statement'):
                summary += f"Position Y: {round_data['position_y_statement'][:200]}...\n"
            summary += "\n"
        
        # Add key points tracking
        summary += "Key Points Already Made:\n"
        for point in self.key_points_made[-5:]:
            summary += f"- {point[:100]}...\n"
            
        summary += "\nOpponent's Key Points:\n"
        for point in self.opponent_points[-5:]:
            summary += f"- {point[:100]}...\n"
            
        return summary
