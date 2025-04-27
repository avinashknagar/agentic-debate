# 📂 Software Requirements Specification (SRS)
**Project:** AI Debate - Knockout Challenge  
**Version:** 3.1  
**Author:** [You]

---

# 1. Project Overview
Build a multi-agent debate system where 1 "Position X" AI agent debates 4 "Position Y" AI agents in a knockout format. Each round is judged by the non-participating Position Y agents. The system must support easy switching of debate topics and participants.

---

# 2. Core Components

## 2.1 Agents
- **Position X Agent**: Represents one side of the debate topic.
- **4 Position Y Agents**: One actively debates while others serve as judges.

Agents must:
- Be initialized with a **customizable role description** and **debate topic**.
- Maintain consistent background knowledge through debate-specific context files.
- Allow easy replacement or addition of agents.

**Input Definition:**
```python
# Example input configuration
position_x = "Pro-Choice"  # Could be any debate position: "Atheist", "Democrat", etc.
position_y = "Pro-Life"    # Could be any opposing position: "Theist", "Republican", etc.
topic = "Should abortion be legal?"  # The central debate question
background_knowledge = {  # Standard facts/context provided to all agents
    "legal_precedents": ["Roe v. Wade", "Planned Parenthood v. Casey"],
    "key_concepts": ["bodily autonomy", "fetal viability", "constitutional rights"]
}
```

**Agent State Management:**
```python
class AgentMemory:
    def __init__(self):
        self.debate_history = []  # Stores all previous rounds' arguments
        self.key_points_made = []  # Tracks main points already covered
        self.opponent_points = []  # Tracks opponent's key arguments
    
    def update(self, debate_round):
        # Update agent's memory after each round
        pass
```

**Prompt Engineering Examples:**
```python
# Pro-Choice Agent Initialization
pro_choice_prompt = """
You are representing the Pro-Choice position in a debate on abortion rights.
Your core values include: bodily autonomy, reproductive freedom, and healthcare access.
Focus on constitutional rights, medical science, and social impacts.
When responding, maintain a respectful tone while firmly defending your position.
"""

# Pro-Life Agent Initialization
pro_life_prompt = """
You are representing the Pro-Life position in a debate on abortion rights.
Your core values include: sanctity of life, fetal rights, and ethical considerations.
Focus on moral arguments, biological development, and alternatives to abortion.
When responding, maintain a respectful tone while firmly defending your position.
"""
```

---

## 2.2 Debate Manager
- Orchestrates the full debate.
- Controls 1v1 matches.
- Manages timers (simulated "5 minutes").
- Handles topic switching.
- Facilitates Position Y rotation based on voting results.
- Manages debate flow and speaking order.

**Input Definition:**
```python
# Example manager configuration
rounds_per_debate = 6  # Total number of exchanges (3 per side)
rotation_iterations = 3  # Maximum number of Position Y rotations
starting_position = "X"  # Which position speaks first in each round
```

**Debate Flow Definition:**
```python
# What constitutes a round
class DebateRound:
    def __init__(self, round_number):
        self.round_number = round_number
        self.position_x_statement = None
        self.position_y_statement = None
        self.speaking_order = ["X", "Y"]  # Can be configured
        self.time_limit = 300  # seconds (5 minutes simulated)

# Transition between rounds
def transition_to_next_round(current_round, debate_transcript):
    """Handles the transition between debate rounds, including:
    1. Summarizing previous round
    2. Introducing the next round topic/focus
    3. Updating agent context with recent exchanges
    """
    pass
```

---

## 2.3 Judging System
- The 3 non-debating Position Y agents evaluate each debate round:
  - Vote on the performance of the debating Position Y agent
  - If majority vote is against the debating agent, rotation occurs
  - Evaluation based on Argument Strength, Relevance, Persuasiveness, and Clarity
- Judgement based on the entire **debate transcript**.

**Input Definition:**
```python
# Judging criteria weights and scoring guidelines
criteria = {
    "argument_strength": {
        "weight": 0.4,
        "scoring_guide": {
            "1": "No substantial arguments or evidence presented",
            "3": "Some valid points but weak supporting evidence",
            "5": "Strong arguments with compelling evidence"
        }
    },
    "relevance": {
        "weight": 0.2,
        "scoring_guide": {
            "1": "Arguments mostly off-topic or tangential",
            "3": "Arguments somewhat related to the debate topic",
            "5": "Arguments directly address the central question"
        }
    },
    "persuasiveness": {
        "weight": 0.3,
        "scoring_guide": {
            "1": "Unconvincing presentation of arguments",
            "3": "Moderately persuasive delivery",
            "5": "Highly compelling and convincing rhetoric"
        }
    },
    "clarity": {
        "weight": 0.1,
        "scoring_guide": {
            "1": "Confusing or poorly structured arguments",
            "3": "Reasonably clear but some disorganization",
            "5": "Exceptionally clear, well-organized arguments"
        }
    }
}

# Tie-breaking mechanism
def resolve_tie(votes):
    """
    Resolves ties in judge voting
    In case of a 1-1-1 split or abstention resulting in tie:
    1. Consider weighted scores rather than binary votes
    2. If still tied, default to continuing with current debater
    """
    pass

# Standardized evaluation format
evaluation_template = {
    "round_number": 0,
    "position_y_performance": {
        "argument_strength": 0,  # 1-5 scale
        "relevance": 0,          # 1-5 scale
        "persuasiveness": 0,     # 1-5 scale
        "clarity": 0             # 1-5 scale
    },
    "total_score": 0.0,          # Weighted average
    "comments": "",              # Justification for scores
    "continue_vote": True        # True = keep debater, False = rotate
}
```

---

## 2.4 Timer System
- Debate lasts for a simulated "5 minutes" per round.
- Each side gets equal time allocation.

**Technical Implementation:**
```python
class TimerSystem:
    def __init__(self, time_limit_seconds=300):
        self.time_limit = time_limit_seconds
        self.time_used = 0
        
    def estimate_response_time(self, response_length):
        """
        Converts response token length to simulated time
        - Average human speaking rate: ~150 words per minute
        - Average word: ~1.5 tokens
        - Therefore ~225 tokens per minute (3.75 tokens per second)
        """
        estimated_seconds = response_length / 3.75
        return estimated_seconds
    
    def enforce_limits(self, agent_response, max_tokens=800):
        """
        Prevents excessively long responses by:
        1. Setting max token limits for API calls
        2. Truncating responses that exceed limits
        3. Notifying when time limit is approaching
        """
        # 800 tokens ≈ 3.5 minutes of speaking time
        if len(agent_response) > max_tokens:
            # Truncate and add note about time limit
            return agent_response[:max_tokens] + "\n[Time limit reached]"
        return agent_response
```

---

## 2.5 Rotation System
- After each debate round:
  - 3 sitting Position Y agents vote on the debating agent's performance
  - If majority vote to switch (2+ negative votes), the current debating agent joins the judges
  - A randomly selected sitting Position Y agent becomes the next debater
- Each Position Y agent can debate at most once per full debate session
- The rotation system tracks which agents have already debated
- The Position X agent remains constant in all debates

**Input Definition:**
```python
# Rotation configuration
rotation_threshold = 2  # Number of negative votes needed to trigger rotation (majority)
rotation_limit = 3      # Maximum number of rotations allowed per debate
rotation_tracking = {   # Tracks which agents have already debated
    "position_y_1": False,
    "position_y_2": False,
    "position_y_3": False,
    "position_y_4": False
}

# Rotation flow handler
def handle_rotation(current_debater, judges, rotation_tracking):
    """
    Manages rotation flow:
    1. Selects eligible judge who hasn't yet debated
    2. If all have debated, continues with current debater
    3. Updates debate flow with proper transition text
    4. Preserves context/history for the new debater
    5. Returns new debater and updated judges list
    """
    pass
```

---

# 3. Technical Requirements

## 3.1 Programming Language
- Python 3.10+

## 3.2 Local Model Support
- System must interface with **local Ollama models**.
- Agents must utilize locally hosted Ollama models (e.g., `llama3`, `mistral`, `codellama`, etc).

**Input Definition:**
```python
# Model configuration
default_model = "llama3"
model_options = ["llama3", "mistral", "codellama"]
model_temperature = 0.7  # Controls randomness in responses
max_tokens = 1024        # Maximum response length
context_window = 8192    # Maximum context window size
```

**Technical Safeguards:**
```python
# Error handling for API failures
def safe_model_call(prompt, retry_attempts=3):
    """
    Handles potential API failures:
    1. Implements exponential backoff for retries
    2. Falls back to alternative models if primary fails
    3. Returns pre-defined emergency responses if all attempts fail
    """
    pass

# Context window management
def manage_context_window(debate_transcript, max_context_size=8192):
    """
    Handles growing transcript:
    1. Prioritizes most recent exchanges
    2. Summarizes older exchanges to save tokens
    3. Preserves key arguments and rebuttals
    4. Ensures context stays within model limits
    """
    pass
```

## 3.3 Flexibility
- Must allow:
  - Easy swapping of debate **topics**.
  - Easy swapping or addition/removal of **agents**.
  - Parameterized initialization for topics and agent behavior.

Example config structure:
```python
agents = [
  Agent(name="Position X", role_description="Debate for position X", model="llama3", position="X"),
  Agent(name="Position Y-1", role_description="Debate for position Y", model="mistral", position="Y"),
  Agent(name="Position Y-2", role_description="Debate for position Y", model="mistral", position="Y"),
  Agent(name="Position Y-3", role_description="Debate for position Y", model="mistral", position="Y"),
  Agent(name="Position Y-4", role_description="Debate for position Y", model="mistral", position="Y"),
]

# Can be easily configured for different debate scenarios:
# Example 1: Atheist vs Theists
# position_x = "Atheist", position_y = "Theist", topic = "Does God exist?"

# Example 2: Liberal vs Conservatives
# position_x = "Liberal", position_y = "Conservative", topic = "Should healthcare be universal?"

current_topic = "Chosen debate topic"
```

---

# 4. Class and Function Design

## 4.1 Class: `Agent`
```python
class Agent:
    def __init__(self, name: str, role_description: str, model: str, position: str, topic: str):
        self.name = name
        self.role_description = role_description
        self.model = model
        self.position = position
        self.topic = topic
        self.memory = AgentMemory()  # Maintains state between rounds

    def send_message(self, message: str, conversation: list) -> str:
        # Format prompt with memory and context
        # Call model with error handling
        # Update agent memory with new information
        # Return response within token limitations
        pass

    def vote(self, transcript: list) -> dict:
        """Returns structured evaluation with scores and vote"""
        # Analyze debate transcript
        # Score according to criteria
        # Return formatted evaluation
        pass
```

## 4.2 Class: `DebateManager`
```python
class DebateManager:
    def __init__(self, position_x: Agent, position_y_agents: list[Agent], topic: str,
                 rounds: int = 6, starting_position: str = "X"):
        self.position_x = position_x
        self.position_y_agents = position_y_agents
        self.topic = topic
        self.rounds = rounds
        self.rotation_count = 0
        self.rotation_limit = 3
        self.rotation_tracking = {agent.name: False for agent in position_y_agents}
        self.current_position_y = position_y_agents[0]
        self.judges = position_y_agents[1:]
        self.timer = TimerSystem()
        self.speaking_order = [starting_position, "Y" if starting_position == "X" else "X"]
        self.debate_transcript = []

    def start_debate(self):
        """Runs the full debate with all rounds and rotations"""
        # Initialize debate with introduction
        # Loop through rounds
        # Handle rotations
        # Present final results
        pass

    def debate_round(self, position_x: Agent, debating_position_y: Agent) -> list:
        """Manages a single round of debate exchange"""
        # Enforce speaking order
        # Apply time limits to responses
        # Handle context window limitations
        # Add round to transcript
        # Return round results
        pass

    def collect_votes(self, transcript: list, judging_position_y_agents: list[Agent]) -> dict:
        """
        Collects and tallies votes from judges
        Returns voting results with detailed evaluations
        Handles tie-breaking scenarios
        """
        pass

    def rotate_agents(self, debating_position_y: Agent, judging_position_y_agents: list[Agent]):
        """
        Rotates Position Y agents based on voting results
        Selects eligible judges who haven't debated yet
        Handles case when all agents have already debated
        Updates rotation tracking and counts
        """
        pass

    def switch_topic(self, new_topic: str):
        # Reset debate state for new topic
        # Update all agents with new topic
        pass

    def switch_agents(self, new_position_x: Agent, new_position_y_agents: list[Agent]):
        # Replace agents
        # Reset rotation tracking
        pass
```

---

# 5. Example Execution Flow

1. Initialize Position X and 4 Position Y agents with a topic.
2. Select 1 Position Y agent for debate, 3 for judging.
3. DebateManager starts 1v1 match: **Position X vs Selected Position Y**.
   - Position X speaks first (configurable).
   - Each side gets 5 minutes (simulated) per round.
4. After each complete exchange (both sides spoke):
   - 3 judging Position Y agents evaluate the debating agent.
   - Each judge submits standardized scoring using the evaluation template.
5. Based on voting:
   - If fewer than 2 negative votes, continue with same debating agent.
   - If 2+ negative votes, rotate a new Position Y agent into the debate position.
   - Rotation only selects from judges who haven't debated yet.
6. Repeat for up to 3 rotations or until all rounds complete.
7. If all Position Y agents have debated and rounds remain, continue with final agent.
8. Print Final Result and debate statistics.

---

# 6. Non-Functional Requirements
- **Performance**: Each debate round must complete within 30 seconds (real processing time).
- **Extensibility**: Should allow for quick addition of more agents, topics, or rules.
- **Portability**: Entire system must run offline with local Ollama models.
- **Error Resilience**: System must handle API failures gracefully.

---

# 7. Stretch Goals (Optional)
- Add Human spectator voting option.
- Add point-based scoring system.
- Add Spectator Mode for live commentaries.

---

# ✅ Conclusion
This SRS provides a modular, clear, and flexible blueprint for building a full Knockout Challenge AI Debate framework with local Ollama model support, agent/topic flexibility, and Position Y rotation based on peer evaluation.

---

# 🌟 Future Enhancements
- Web UI for live debates
- Historical leaderboards
- Debate analytics with argument scoring

