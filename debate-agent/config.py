from typing import Dict, List, Any

# Model configuration
DEFAULT_MODEL = "llama3:latest"
MODEL_OPTIONS = ["llama3:latest", "mistral", "codellama"]
MODEL_TEMPERATURE = 0.7
MAX_TOKENS = 1024
CONTEXT_WINDOW = 8192

# Debate configuration
DEFAULT_ROUNDS = 6
MAX_ROTATION_COUNT = 3
DEFAULT_STARTING_POSITION = "X"

# Judging criteria
JUDGING_CRITERIA = {
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

# Evaluation template
EVALUATION_TEMPLATE = {
    "round_number": 0,
    "position_y_performance": {
        "argument_strength": 0,
        "relevance": 0,
        "persuasiveness": 0,
        "clarity": 0
    },
    "total_score": 0.0,
    "comments": "",
    "continue_vote": True
}

# Timer configuration
DEFAULT_TIME_LIMIT_SECONDS = 300  # 5 minutes
TOKENS_PER_SECOND = 3.75  # Based on ~150 words per minute

# Response length configuration
RESPONSE_STYLES = {
    "concise": {
        "description": "Keep your response extremely concise. Use no more than 3-4 sentences total.",
        "token_limit": 150,
        "max_chars": 500
    },
    "standard": {
        "description": "Provide a clear, focused response. Use 5-7 sentences to make your points.",
        "token_limit": 300,
        "max_chars": 1000
    },
    "detailed": {
        "description": "Develop your arguments thoroughly. Use up to 10 sentences to articulate your position.",
        "token_limit": 500,
        "max_chars": 2000
    },
    "comprehensive": {
        "description": "Present a comprehensive argument with detailed explanations and evidence.",
        "token_limit": 800,
        "max_chars": 3500
    }
}

# Default response style (can be "concise", "standard", "detailed", or "comprehensive")
DEFAULT_RESPONSE_STYLE = "detailed"
