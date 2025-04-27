from typing import List, Dict, Any, Optional
import time
import copy
import subprocess
import os

# Update imports to use non-deprecated packages
from langchain_ollama import OllamaLLM
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from memory import AgentMemory
from config import (
    DEFAULT_MODEL, MODEL_TEMPERATURE, MAX_TOKENS, JUDGING_CRITERIA, 
    EVALUATION_TEMPLATE, DEFAULT_RESPONSE_STYLE, RESPONSE_STYLES
)

class Agent:
    """
    Represents a debate agent with memory and language model integration
    """
    def __init__(self, 
                 name: str, 
                 role_description: str, 
                 model: str = DEFAULT_MODEL, 
                 position: str = "X", 
                 topic: str = "",
                 response_style: str = None):
        self.name = name
        self.role_description = role_description
        self.model = model  # This will be like "llama3:latest"
        self.position = position  # "X" or "Y"
        self.topic = topic
        self.memory = AgentMemory()
        self.response_style = response_style or DEFAULT_RESPONSE_STYLE
        
        # Check if model exists, pull if it doesn't
        self._ensure_model_available()
        
        # Use updated OllamaLLM class with the exact model name
        self.llm = OllamaLLM(model=self.model, temperature=MODEL_TEMPERATURE)

    def _get_position_desc(self, position: str) -> str:
        """Returns a description based on the agent's position"""
        return "advocating" if position == 'X' else "challenging"
    
    def _ensure_model_available(self):
        """Check if the model is available and pull it if needed"""
        try:
            # Parse model name to handle tags like "llama3:latest"
            base_model = self.model.split(':')[0] if ':' in self.model else self.model
            
            # Check if model exists by listing models
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, check=True)
            
            # Check if either the exact model name or base model name is in the list
            if self.model not in result.stdout and base_model not in result.stdout:
                print(f"Model {self.model} not found. Pulling model...")
                # Use the full model name including tag when pulling
                subprocess.run(['ollama', 'pull', self.model], check=True)
                print(f"Model {self.model} successfully pulled.")
        except subprocess.CalledProcessError as e:
            print(f"Error checking or pulling model: {e}")
            print(f"Command output: {e.stdout}, {e.stderr}")
            print("Please ensure Ollama is installed and running.")
        except FileNotFoundError:
            print("Ollama command not found. Please ensure Ollama is installed and in your PATH.")

    def _create_system_prompt(self) -> str:
        """Creates the system prompt for the agent based on role and topic"""
        system_prompt = f"""You are {self.name}, representing the {self._get_position_desc(self.position)} position in a debate.
Topic: {self.topic}

{self.role_description}

IMPORTANT INSTRUCTIONS:
- Do NOT start your responses with phrases like "As a [your role]..." or identify yourself in any way
- Do NOT mention that you are an AI or language model
- Speak naturally as if you are a real person engaged in a live debate
- Jump directly into your arguments without any self-introduction
- Respond as the actual person you're representing, not as someone playing a role

Respond with clear, concise arguments. Keep your responses brief and to the point.
{RESPONSE_STYLES[self.response_style]['description']}
Maintain a respectful and professional tone at all times.
Focus on strong reasoning and evidence to support your position.
Your response should be structured and directly address the topic and opponent's arguments.

Stay consistent with your assigned perspective throughout the debate.
"""
        return system_prompt

    def _build_system_message(self):
        """This method is not used directly - kept for backwards compatibility"""
        return ""
    
    def _create_prompt_messages(self, message: str, conversation: List[Dict]) -> List[Any]:
        """Creates the full prompt with conversation history"""
        messages = [SystemMessage(content=self._create_system_prompt())]
        
        # Add brevity instruction as a separate system message for emphasis
        messages.append(SystemMessage(content=f"IMPORTANT: {RESPONSE_STYLES[self.response_style]['description']}"))
        
        # Add summarized context from agent memory
        memory_context = self.memory.get_context_summary()
        if memory_context:
            messages.append(SystemMessage(content=f"Previous debate context: {memory_context}"))
        
        # Add conversation history
        for turn in conversation[-5:]:  # Limited context window
            if 'position_x_statement' in turn:
                x_speaker = turn.get('position_x_name', 'Opponent')
                messages.append(HumanMessage(content=f"{x_speaker}: {turn['position_x_statement']}"))
            if 'position_y_statement' in turn:
                y_speaker = turn.get('position_y_name', 'You')
                messages.append(AIMessage(content=f"{y_speaker}: {turn['position_y_statement']}"))
        
        # Add current message
        messages.append(HumanMessage(content=message))
        
        return messages

    def send_message(self, message: str, conversation: List[Dict]) -> str:
        """
        Generates a response from the agent based on the message and conversation
        
        Args:
            message: The message/prompt to respond to
            conversation: The debate history
            
        Returns:
            str: Agent's response
        """
        try:
            messages = self._create_prompt_messages(message, conversation)
            
            # Use token limit from the configured response style
            token_limit = RESPONSE_STYLES[self.response_style]['token_limit']
            
            # Use num_predict instead of max_tokens for Ollama
            response = self.llm.invoke(
                messages,
                options={"num_predict": token_limit}
            )
            
            # Update agent memory with the new information
            latest_round = {}
            if self.position == "X":
                latest_round["position_x_name"] = self.name
                latest_round["position_x_statement"] = response
            else:
                latest_round["position_y_name"] = self.name
                latest_round["position_y_statement"] = response
            
            self.memory.update(latest_round)
            
            return response
        except Exception as e:
            print(f"Error generating response: {e}")
            print(f"Model being used: {self.model}")
            return "I apologize, but I'm unable to provide a response at this moment."
    
    def vote(self, transcript: List[Dict], current_round: int) -> Dict:
        """
        Evaluates a debate round and returns scoring
        Only used by Position Y agents acting as judges
        
        Args:
            transcript: Full debate transcript
            current_round: The round number being evaluated
            
        Returns:
            dict: Standardized evaluation with scores
        """
        if self.position != "Y":
            raise ValueError("Only Position Y agents can vote")
        
        # Create evaluation prompt
        eval_prompt = self._create_evaluation_prompt(transcript, current_round)
        
        try:
            # Direct invocation without trying to access .content
            response = self.llm.invoke(eval_prompt)
            
            # Parse the response to extract scores
            evaluation = self._parse_evaluation(response, current_round)
            return evaluation
            
        except Exception as e:
            print(f"Error during evaluation: {e}")
            # Return a default neutral evaluation if there's an error
            evaluation = copy.deepcopy(EVALUATION_TEMPLATE)
            evaluation["round_number"] = current_round
            evaluation["comments"] = "Unable to complete evaluation due to technical difficulties."
            evaluation["position_y_performance"] = {k: 3 for k in JUDGING_CRITERIA.keys()}
            # No continue_vote field, this will be determined by the debate manager
            return evaluation
    
    def _create_evaluation_prompt(self, transcript: List[Dict], current_round: int) -> str:
        """Creates prompt for evaluation"""
        prompt = f"""You are a debate judge evaluating round {current_round} on the topic: {self.topic}

Your task is to assess the performance of the second speaker (Challenging Position) against the first speaker (Advocating Position).

EVALUATION CRITERIA:
"""
        
        # Add criteria descriptions
        for criterion, details in JUDGING_CRITERIA.items():
            prompt += f"- {criterion.replace('_', ' ').title()} (weight: {details['weight']})\n"
            for score, description in details['scoring_guide'].items():
                prompt += f"  Score {score}: {description}\n"
        
        prompt += "\nDEBATE TRANSCRIPT (ROUND {current_round}):\n"
        
        # Add the relevant round from the transcript with clearer speaker identification
        if current_round <= len(transcript):
            round_data = transcript[current_round - 1]
            x_name = round_data.get('position_x_name', 'Advocating Speaker')
            y_name = round_data.get('position_y_name', 'Challenging Speaker')
            
            prompt += f"=== {x_name} (Advocating) ===\n{round_data.get('position_x_statement', 'No statement provided')}\n\n"
            prompt += f"=== {y_name} (Challenging) ===\n{round_data.get('position_y_statement', 'No statement provided')}\n\n"
        
        prompt += f"""REQUIRED EVALUATION FORMAT:

Argument Strength: [score 1-5]
Relevance: [score 1-5] 
Persuasiveness: [score 1-5]
Clarity: [score 1-5]

Comments: [Provide 2-3 sentences justifying your scores]

IMPORTANT INSTRUCTIONS:
1. All scores MUST be integers between 1-5
2. DO NOT calculate a total score
3. Be harsh, critical and objective in your evaluation
4. The debate continues only if Position Y (challenging side) performs poorly, so evaluate truthfully
5. Format your response EXACTLY as shown above
"""
        
        return prompt
    
    def _parse_evaluation(self, response: str, current_round: int) -> Dict:
        """
        Parses evaluation response to extract structured scores
        
        Args:
            response: The raw LLM evaluation response
            current_round: Current round number
            
        Returns:
            dict: Structured evaluation data
        """
        evaluation = copy.deepcopy(EVALUATION_TEMPLATE)
        evaluation["round_number"] = current_round
        
        # Extract scores - simplified parsing
        lines = response.strip().split('\n')
        for line in lines:
            line = line.strip().lower()
            
            # Parse criteria scores
            for criterion in JUDGING_CRITERIA.keys():
                criterion_text = criterion.replace('_', ' ').lower()
                if line.startswith(criterion_text):
                    try:
                        score = int(line.split(':')[1].strip()[0])
                        if 1 <= score <= 5:
                            evaluation["position_y_performance"][criterion] = score
                        else:
                            # Default to middle score if out of range
                            evaluation["position_y_performance"][criterion] = 3
                    except:
                        # Default to middle score if parsing fails
                        evaluation["position_y_performance"][criterion] = 3
            
            # Parse comments
            if line.startswith("comments"):
                try:
                    evaluation["comments"] = line.split(':', 1)[1].strip()
                except:
                    pass
        
        # Calculate weighted total score
        total_score = 0.0
        total_weight = 0.0
        for criterion, score in evaluation["position_y_performance"].items():
            weight = JUDGING_CRITERIA[criterion]["weight"]
            total_score += score * weight
            total_weight += weight
        
        # Normalize the score if we have weights
        if total_weight > 0:
            evaluation["total_score"] = round(total_score / total_weight, 2)
        else:
            # Fallback if no weights are defined
            evaluation["total_score"] = sum(evaluation["position_y_performance"].values()) / len(evaluation["position_y_performance"])
        
        return evaluation
