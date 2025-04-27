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
