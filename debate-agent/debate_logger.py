import os
import datetime
import json
from typing import Dict, List, Any, Optional

class DebateLogger:
    """
    Handles logging and saving debate transcripts with timestamps
    """
    def __init__(self, output_dir: str = 'output', verbose: bool = True):
        """
        Initialize the debate logger
        
        Args:
            output_dir: Directory to store debate logs
            verbose: Whether to print full responses to console
        """
        self.verbose = verbose
        self.output_dir = output_dir
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_filename = None
        self.ensure_output_dir()
        
    def ensure_output_dir(self) -> None:
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"Created output directory: {self.output_dir}")
    
    def get_log_path(self, topic: str = "") -> str:
        """Generate a log filename with timestamp and sanitized topic"""
        # Sanitize topic for filename
        sanitized_topic = "".join(c if c.isalnum() else "_" for c in topic)[:30]
        if sanitized_topic:
            filename = f"debate_{sanitized_topic}_{self.timestamp}.json"
        else:
            filename = f"debate_{self.timestamp}.json"
            
        self.log_filename = os.path.join(self.output_dir, filename)
        return self.log_filename
    
    def log_round(self, round_data: Dict, round_num: int, position_x_name: str, position_y_name: str) -> None:
        """
        Log a debate round to console
        
        Args:
            round_data: Data from the debate round
            round_num: Current round number
            position_x_name: Name of Position X agent
            position_y_name: Name of Position Y agent
        """
        print(f"\n--- Round {round_num} ---")
        
        # Position X statement
        print(f"\n{position_x_name}:")
        if self.verbose:
            # Print full statement
            print(round_data.get("position_x_statement", "No statement"))
        else:
            # Print truncated statement
            statement = round_data.get("position_x_statement", "No statement")
            print(f"{statement[:100]}..." if len(statement) > 100 else statement)
        
        # Position Y statement
        print(f"\n{position_y_name}:")
        if self.verbose:
            # Print full statement
            print(round_data.get("position_y_statement", "No statement"))
        else:
            # Print truncated statement
            statement = round_data.get("position_y_statement", "No statement")
            print(f"{statement[:100]}..." if len(statement) > 100 else statement)
    
    def log_votes(self, voting_results: Dict, current_position_y: str) -> None:
        """
        Log voting results to console
        
        Args:
            voting_results: Results from judge voting
            current_position_y: Name of the current Position Y debater
        """
        print("\n--- Judge Voting ---")
        print(f"Continue votes: {voting_results['continue_votes']}")
        print(f"Replace votes: {voting_results['replace_votes']}")
        
        if voting_results['continue']:
            print(f"The judges have voted to continue with {current_position_y}.")
        else:
            print(f"The judges have voted to replace {current_position_y}.")
            
        # Log detailed evaluations if verbose
        if self.verbose:
            print("\nDetailed Evaluations:")
            for i, eval_data in enumerate(voting_results['evaluations']):
                print(f"Judge {i+1}:")
                print(f"  Total Score: {eval_data['total_score']}")
                print(f"  Vote: {'CONTINUE' if eval_data['continue_vote'] else 'REPLACE'}")
                print(f"  Comments: {eval_data['comments']}")
    
    def save_debate(self, debate_data: Dict) -> None:
        """
        Save debate transcript and results to a JSON file
        
        Args:
            debate_data: Complete debate data including transcript and results
        """
        log_path = self.get_log_path(debate_data.get("topic", ""))
        
        # Add timestamp to debate data
        debate_data["timestamp"] = self.timestamp
        
        # Format the transcript to ensure voting results are properly included
        for round_data in debate_data["transcript"]:
            if "voting_results" in round_data:
                # Ensure voting results are properly formatted
                voting = round_data["voting_results"]
                round_data["voting_results"] = {
                    "continue": voting["continue"],
                    "continue_votes": voting["continue_votes"],
                    "replace_votes": voting["replace_votes"],
                    "evaluations": []
                }
                
                # Format each judge's evaluation
                for i, eval_data in enumerate(voting["evaluations"]):
                    judge_evaluation = {
                        "judge_number": i+1,
                        "total_score": eval_data["total_score"],
                        "vote": "CONTINUE" if eval_data["continue_vote"] else "REPLACE",
                        "comments": eval_data["comments"],
                        "criteria_scores": eval_data.get("position_y_performance", {})
                    }
                    round_data["voting_results"]["evaluations"].append(judge_evaluation)
        
        try:
            with open(log_path, 'w') as f:
                json.dump(debate_data, f, indent=2)
            print(f"\nDebate saved to: {log_path}")
        except Exception as e:
            print(f"Error saving debate: {e}")
    
    def print_debate_summary(self, results: Dict) -> None:
        """
        Print a summary of the debate results
        
        Args:
            results: Debate results data
        """
        print("\n=== Debate Summary ===")
        print(f"Topic: {results['topic']}")
        print(f"Position X: {results['position_x']}")
        print(f"Position Y debaters: {', '.join(results['position_y_debaters'])}")
        print(f"Total rounds: {results['rounds']}")
        print(f"Total rotations: {results['rotations']}")
        
        if self.log_filename:
            print(f"\nFull transcript saved to: {self.log_filename}")
