# Debate Agent Execution Guide

This document provides instructions for running the AI Debate Knockout Challenge system.

## Prerequisites

1. Ensure Python 3.10+ is installed on your system
2. Install [Ollama](https://ollama.ai/) and verify it's running
3. Install required Python packages:
   ```
   pip install langchain langchain-ollama
   ```

## Basic Execution

### Using Built-in Example Debates

To run a debate using the built-in examples:

```bash
python main.py
```

You will be prompted to choose from available debate topics.

### Specifying a Debate Topic

To directly select a specific debate topic without prompts:

```bash
python main.py --topic 2  # 1=Abortion, 2=God, 3=Healthcare
```

### Additional Command Line Options

- Set the number of debate rounds:
  ```bash
  python main.py --rounds 8  # Default is 6
  ```

- Enable verbose output (full agent responses in console):
  ```bash
  python main.py --verbose
  ```

## Using Configuration Files

### Default Configuration

To run using the default input.json configuration file:

```bash
python main.py --use-config
```

### Custom Configuration File

To use a custom configuration file:

```bash
python main.py --config /path/to/custom_config.json
```

### Configuration Options

The input.json file allows you to customize:
- Debate topic
- Position X agent (name, role description, model)
- Position Y agents (at least 4 required)
- Debate settings (rounds, starting position, verbosity, rotation limit)

## Configuration File Structure

```json
{
  "topic": "Does God exist?",
  "position_x": {
    "name": "Atheist Advocate",
    "role_description": "Description of position X role...",
    "model": "llama3:latest"
  },
  "position_y": [
    {
      "name": "Theist Expert 1",
      "role_description": "Description of position Y role...",
      "model": "llama3:latest"
    },
    {
      "name": "Theist Expert 2",
      "role_description": "Description of position Y role...",
      "model": "llama3:latest"
    },
    // At least 4 position Y agents are required
  ],
  "debate_settings": {
    "rounds": 6,
    "starting_position": "X",
    "verbose": true,
    "rotation_limit": 3
  }
}
```

## Creating Your Own Debates

1. Create a copy of the default input.json file
2. Modify the topic, agent names, and role descriptions
3. Run the debate using your configuration file:
   ```bash
   python main.py --config your_custom_config.json
   ```

## Debate Output

The system saves debate transcripts to the `output` directory as JSON files with naming format:
