from agent import Agent
from debate_manager import DebateManager
import argparse

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
    parser.add_argument('--rounds', type=int, default=6, help='Number of debate rounds')
    parser.add_argument('--verbose', action='store_true', help='Print full agent responses to console')
    args = parser.parse_args()
    
    # Create debate setup
    topic, position_x, position_y, position_x_agent, position_y_agents = create_example_debate(args.topic)
    
    print(f"Setting up debate on '{topic}'")
    print(f"Position X: {position_x}")
    print(f"Position Y: {position_y}")
    
    # Create and start the debate manager
    debate_manager = DebateManager(
        position_x=position_x_agent,
        position_y_agents=position_y_agents,
        topic=topic,
        rounds=args.rounds,
        verbose=args.verbose
    )
    
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
