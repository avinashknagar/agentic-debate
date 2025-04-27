from agent import Agent
from debate_manager import DebateManager
import argparse
from config_loader import load_config
import os
import sys

def create_agents_from_config(config):
    """
    Creates agents from configuration
    
    Args:
        config: Loaded configuration dictionary
        
    Returns:
        tuple: (topic, position_x_agent, position_y_agents)
    """
    topic = config["topic"]
    
    # Create Position X agent
    position_x_config = config["position_x"]
    position_x_agent = Agent(
        name=position_x_config["name"],
        role_description=position_x_config["role_description"],
        model=position_x_config.get("model", "llama3:latest"),
        position="X",
        topic=topic
    )
    
    # Create Position Y agents
    position_y_agents = []
    for pos_y_config in config["position_y"]:
        position_y_agents.append(
            Agent(
                name=pos_y_config["name"],
                role_description=pos_y_config["role_description"],
                model=pos_y_config.get("model", "llama3:latest"),
                position="Y",
                topic=topic
            )
        )
    
    return topic, position_x_agent, position_y_agents

def create_example_debate(topic_choice=None):
    """
    Creates a sample debate based on the selected topic
    
    Args:
        topic_choice: Selected debate topic
        
    Returns:
        tuple: (topic, position_x, position_y, position_x_agent, position_y_agents)
    """
    # Define available debate topics
    topics = {
        1: {
            "topic": "Should abortion be legal?",
            "position_x": "Pro-Choice",
            "position_y": "Pro-Life",
            "position_x_desc": """You are representing the Pro-Choice position in a debate on abortion rights.
Your core values include: bodily autonomy, reproductive freedom, and healthcare access.
Focus on constitutional rights, medical science, and social impacts.
When responding, maintain a respectful tone while firmly defending your position.""",
            "position_y_desc": """You are representing the Pro-Life position in a debate on abortion rights.
Your core values include: sanctity of life, fetal rights, and ethical considerations.
Focus on moral arguments, biological development, and alternatives to abortion.
When responding, maintain a respectful tone while firmly defending your position."""
        },
        2: {
            "topic": "Does God exist?",
            "position_x": "Atheist",
            "position_y": "Theist",
            "position_x_desc": """You are representing the Atheist position in a debate on God's existence.
Your core values include: empirical evidence, scientific method, and rational thinking.
Focus on lack of evidence, scientific explanations, and logical arguments.
When responding, maintain a respectful tone while firmly defending your position.""",
            "position_y_desc": """You are representing the Theist position in a debate on God's existence.
Your core values include: faith, spiritual experience, and religious tradition.
Focus on cosmological arguments, personal experience, and moral foundations.
When responding, maintain a respectful tone while firmly defending your position."""
        },
        3: {
            "topic": "Should healthcare be universal?",
            "position_x": "Liberal",
            "position_y": "Conservative",
            "position_x_desc": """You are representing the Liberal position on universal healthcare.
Your core values include: equality, social safety nets, and public welfare.
Focus on healthcare as a right, cost efficiency of universal systems, and societal benefits.
When responding, maintain a respectful tone while firmly defending your position.""",
            "position_y_desc": """You are representing the Conservative position on healthcare.
Your core values include: individual responsibility, market solutions, and limited government.
Focus on free market competition, innovation, quality of care, and personal choice.
When responding, maintain a respectful tone while firmly defending your position."""
        }
    }
    
    # Select debate topic
    if topic_choice is None or topic_choice not in topics:
        print("Available debate topics:")
        for key, value in topics.items():
            print(f"{key}. {value['topic']} ({value['position_x']} vs. {value['position_y']})")
        
        topic_choice = int(input("Select a debate topic (1-3): "))
    
    selected_topic = topics[topic_choice]
    
    # Create Position X agent
    position_x_agent = Agent(
        name=f"{selected_topic['position_x']} Advocate",
        role_description=selected_topic['position_x_desc'],
        model="llama3",
        position="X",
        topic=selected_topic['topic']
    )
    
    # Create Position Y agents
    position_y_agents = []
    for i in range(1, 5):
        position_y_agents.append(
            Agent(
                name=f"{selected_topic['position_y']} Expert {i}",
                role_description=selected_topic['position_y_desc'],
                model="llama3",
                position="Y",
                topic=selected_topic['topic']
            )
        )
    
    return (
        selected_topic['topic'],
        selected_topic['position_x'],
        selected_topic['position_y'],
        position_x_agent,
        position_y_agents
    )

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='AI Debate Knockout Challenge')
    parser.add_argument('--topic', type=int, help='Select debate topic (1-3)')
    parser.add_argument('--rounds', type=int, help='Number of debate rounds')
    parser.add_argument('--verbose', action='store_true', help='Print full agent responses to console')
    parser.add_argument('--config', type=str, help='Path to custom configuration file')
    parser.add_argument('--use-config', action='store_true', help='Use configuration from input.json')
    args = parser.parse_args()
    
    # Determine whether to use config file or example debates
    if args.use_config or args.config:
        try:
            # Load configuration
            config = load_config(args.config)
            
            # Create agents from configuration
            topic, position_x_agent, position_y_agents = create_agents_from_config(config)
            
            # Get debate settings from configuration
            debate_settings = config.get("debate_settings", {})
            rounds = args.rounds or debate_settings.get("rounds", 6)
            verbose = args.verbose or debate_settings.get("verbose", True)
            starting_position = debate_settings.get("starting_position", "X")
            rotation_limit = debate_settings.get("rotation_limit", 3)
            
            print(f"Setting up debate on '{topic}' using configuration file")
            print(f"Position X: {position_x_agent.name}")
            print(f"Position Y: {position_y_agents[0].name} and others")
        except Exception as e:
            print(f"Error loading configuration: {e}")
            print("Falling back to example debate setup...")
            # Fall back to example debate
            topic, position_x, position_y, position_x_agent, position_y_agents = create_example_debate(args.topic)
            rounds = args.rounds or 6
            verbose = args.verbose
            starting_position = "X"
            rotation_limit = 3
            
            print(f"Setting up debate on '{topic}'")
            print(f"Position X: {position_x}")
            print(f"Position Y: {position_y}")
    else:
        # Create debate setup from examples
        topic, position_x, position_y, position_x_agent, position_y_agents = create_example_debate(args.topic)
        rounds = args.rounds or 6
        verbose = args.verbose
        starting_position = "X"
        rotation_limit = 3
        
        print(f"Setting up debate on '{topic}'")
        print(f"Position X: {position_x}")
        print(f"Position Y: {position_y}")
    
    # Create and start the debate manager
    debate_manager = DebateManager(
        position_x=position_x_agent,
        position_y_agents=position_y_agents,
        topic=topic,
        rounds=rounds,
        starting_position=starting_position,
        verbose=verbose
    )
    
    # Set rotation limit if provided in config
    if 'rotation_limit' in locals():
        debate_manager.rotation_limit = rotation_limit
    
    # Run the debate
    results = debate_manager.start_debate()
    
    # Print summary
    print("\n=== Debate Summary ===")
    print(f"Topic: {results['topic']}")
    print(f"Position X: {results['position_x']}")
    print(f"Position Y debaters: {', '.join(results['position_y_debaters'])}")
    print(f"Total rounds: {results['rounds']}")
    print(f"Total rotations: {results['rotations']}")

if __name__ == "__main__":
    main()
