from typing import List, Dict, Any, Tuple
import random
from agent import Agent
from timer import TimerSystem
from debate_logger import DebateLogger
from config import DEFAULT_ROUNDS, DEFAULT_STARTING_POSITION, MAX_ROTATION_COUNT

class DebateRound:
    """Represents a single round of debate"""
    def __init__(self, round_number: int):
        self.round_number = round_number
        self.position_x_statement = None
        self.position_y_statement = None
        self.speaking_order = ["X", "Y"]
        self.time_limit = 300  # seconds

class DebateManager:
    """
    Manages the debate process, including rounds, rotations, and judging
    """
    def __init__(self, 
                 position_x: Agent, 
                 position_y_agents: List[Agent], 
                 topic: str,
                 rounds: int = DEFAULT_ROUNDS, 
                 starting_position: str = DEFAULT_STARTING_POSITION,
                 verbose: bool = True,
                 response_style: str = None):
        if len(position_y_agents) < 4:
            raise ValueError("Need at least 4 Position Y agents")
            
        self.position_x = position_x
        self.position_y_agents = position_y_agents
        self.topic = topic
        self.rounds = rounds
        self.rotation_count = 0
        self.rotation_limit = MAX_ROTATION_COUNT
        self.rotation_tracking = {agent.name: False for agent in position_y_agents}
        self.current_position_y = position_y_agents[0]
        self.rotation_tracking[self.current_position_y.name] = True
        self.judges = position_y_agents[1:]

        
        self.timer = TimerSystem()
        self.speaking_order = [starting_position, "Y" if starting_position == "X" else "X"]
        self.debate_transcript = []
        self.logger = DebateLogger(verbose=verbose)
        
        # Set response style for all agents if provided
        if response_style:
            position_x.response_style = response_style
            for agent in position_y_agents:
                agent.response_style = response_style

    def start_debate(self) -> Dict:
        """
        Runs the full debate with all rounds and rotations
        
        Returns:
            dict: Debate results and statistics
        """
        print(f"=== Starting Debate: {self.topic} ===")
        print(f"Position X: {self.position_x.name}")
        print(f"Position Y: {self.current_position_y.name}")
        print("Judges:", ", ".join([j.name for j in self.judges]))
        print("=" * 50)
        
        # Initialize debate with introduction
        intro_prompt = f"We are beginning a debate on the topic: {self.topic}. Please make your opening statement."
        
        # Debate rounds
        for round_num in range(1, self.rounds + 1):
            print(f"\n--- Round {round_num} ---")
            
            # Run the debate round
            round_result = self.debate_round(round_num, self.position_x, self.current_position_y)
            self.debate_transcript.append(round_result)
            
            # Log the round using our logger
            self.logger.log_round(
                round_result, 
                round_num, 
                self.position_x.name, 
                self.current_position_y.name
            )
            
            # Collect votes from judges (except in the final round)
            if round_num < self.rounds:
                print("\n--- Judge Voting ---")
                voting_results = self.collect_votes(round_num)
                
                # Store voting results in the round data
                round_result["voting_results"] = voting_results
                
                # Log voting results
                self.logger.log_votes(voting_results, self.current_position_y.name)
                
                # Handle rotation if needed
                if not voting_results["continue"] and self.rotation_count < self.rotation_limit:
                    print("\n--- Rotation ---")
                    self.rotate_agents()
                    print(f"New Position Y debater: {self.current_position_y.name}")
                    print("New Judges:", ", ".join([j.name for j in self.judges]))
        
        # Present final results
        print("\n=== Debate Concluded ===")
        debate_results = {
            "topic": self.topic,
            "position_x": self.position_x.name,
            "position_y_debaters": [name for name, debated in self.rotation_tracking.items() if debated],
            "rounds": self.rounds,
            "rotations": self.rotation_count,
            "transcript": self.debate_transcript
        }
        
        # Save the debate results
        self.logger.save_debate(debate_results)
        
        # Print summary
        self.logger.print_debate_summary(debate_results)
        
        return debate_results

    def debate_round(self, round_num: int, position_x: Agent, debating_position_y: Agent) -> Dict:
        """
        Manages a single round of debate exchange
        
        Args:
            round_num: Current round number
            position_x: Position X agent
            debating_position_y: Current Position Y debater
            
        Returns:
            dict: Round results including statements from both positions
        """
        round_data = {"round": round_num}
        self.timer.reset()
        
        # Store agent names in round data
        round_data["position_x_name"] = position_x.name
        round_data["position_y_name"] = debating_position_y.name
        
        # Generate debate prompts based on round number
        if round_num == 1:
            x_prompt = f"This is round 1 of our debate on '{self.topic}'. Please make your opening statement."
            y_prompt = f"This is round 1 of our debate on '{self.topic}'. Your opponent made the following opening statement. Please respond with your opening statement:"
        else:
            x_prompt = f"This is round {round_num} of our debate. Please continue your arguments based on the previous exchanges."
            y_prompt = f"This is round {round_num} of our debate. Please continue your arguments based on the previous exchanges."
        
        # Follow the speaking order
        for position in self.speaking_order:
            if position == "X":
                print(f"Position X ({position_x.name}) is speaking...")
                response = position_x.send_message(x_prompt, self.debate_transcript)
                limited_response = self.timer.enforce_limits(response)
                round_data["position_x_statement"] = limited_response
                print(f"Position X: {limited_response[:100]}...\n")
                
                # Update prompt for Position Y to include X's statement
                y_prompt += f"\n\nPosition X's statement: {limited_response}"
                
            else:  # position == "Y"
                print(f"Position Y ({debating_position_y.name}) is speaking...")
                response = debating_position_y.send_message(y_prompt, self.debate_transcript)
                limited_response = self.timer.enforce_limits(response)
                round_data["position_y_statement"] = limited_response
                print(f"Position Y: {limited_response[:100]}...\n")
        
        return round_data

    def collect_votes(self, round_num: int) -> Dict:
        """
        Collects and tallies votes from judges
        
        Args:
            round_num: Current round number
            
        Returns:
            dict: Voting results with detailed evaluations
        """
        votes = []
        continue_votes = 0
        replace_votes = 0
 
        
        for judge in self.judges:
            print(f"Judge {judge.name} is evaluating...")
            evaluation = judge.vote(self.debate_transcript, round_num)
            
            # Add judge name to the evaluation data
            evaluation["judge_name"] = judge.name
            
            
            # Determine continue/replace based on average score
            # If average score is less than 4.0, consider it a vote to replace
            continue_vote = evaluation["total_score"] >= 4.0
            evaluation["continue_vote"] = continue_vote
            
            votes.append(evaluation)
            
            if continue_vote:
                continue_votes += 1
            else:
                replace_votes += 1
                
            print(f"Judge {judge.name} votes: {'CONTINUE' if continue_vote else 'REPLACE'} - Score: {evaluation['total_score']}")

        
        # Determine majority vote
        continue_debater = continue_votes >= len(self.judges) / 2
        
        if not continue_debater:
            print(f"The judges have voted to replace the current Position Y debater ({self.current_position_y.name}).")
        else:
            print(f"The judges have voted to continue with the current Position Y debater ({self.current_position_y.name}).")
        
        return {
            "continue": continue_debater,
            "continue_votes": continue_votes,
            "replace_votes": replace_votes,
            "evaluations": votes,
        }

    def rotate_agents(self) -> None:
        """
        Rotates Position Y agents based on voting results
        """
        self.rotation_count += 1
        
        # Find eligible judges who haven't debated yet
        eligible_judges = [judge for judge in self.judges 
                          if not self.rotation_tracking.get(judge.name, True)]
        
        if not eligible_judges:
            print("All Position Y agents have already debated. Continuing with current debater.")
            return
        
        # Select a random eligible judge to become the new debater
        new_debater = random.choice(eligible_judges)
        
        # Update rotation tracking
        self.rotation_tracking[new_debater.name] = True
        
        # Move current debater to judges
        self.judges.append(self.current_position_y)
        
        # Remove new debater from judges
        self.judges = [j for j in self.judges if j.name != new_debater.name]
        
        # Set new debater
        self.current_position_y = new_debater

    def switch_topic(self, new_topic: str) -> None:
        """
        Switches the debate to a new topic
        
        Args:
            new_topic: The new debate topic
        """
        self.topic = new_topic
        self.position_x.topic = new_topic
        self.rotation_count = 0
        self.debate_transcript = []
        
        for agent in self.position_y_agents:
            agent.topic = new_topic
            
        # Reset rotation tracking
        self.rotation_tracking = {agent.name: False for agent in self.position_y_agents}
        self.rotation_tracking[self.current_position_y.name] = True

    def switch_agents(self, new_position_x: Agent, new_position_y_agents: List[Agent]) -> None:
        """
        Replaces the agents in the debate
        
        Args:
            new_position_x: New Position X agent
            new_position_y_agents: New list of Position Y agents
        """
        self.position_x = new_position_x
        self.position_y_agents = new_position_y_agents
        self.current_position_y = new_position_y_agents[0]
        self.judges = new_position_y_agents[1:]
        self.rotation_count = 0
        self.debate_transcript = []
        
        # Reset rotation tracking
        self.rotation_tracking = {agent.name: False for agent in new_position_y_agents}
        self.rotation_tracking[self.current_position_y.name] = True
