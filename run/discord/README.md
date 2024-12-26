# Example App - Discord Bot with Web Research

This example illustrates how you can create an applicaiton on top of creo-1 using custom agents and tools. The application consists of 2 agents and 3 tools:

- Main Agent
- Web Agent
- - Google Search tool
- - URL Request tool
- - Note taking tool

# Setup

## NOTE: Run all steps from project root folder

### Variables
You will need to make sure you have the following vaues defined in your `.env` file:
```
DISCORD_CHANNEL_ID=<your-channel-id>
DISCORD_TOKEN=<your-discord-token>
```

### Environment
Activate your `.venv`:
```
source .venv/bin/activate
```

### Requirements
Install requirements:
```
chmod +X run/discord/setup.sh
sh run/discord/setup.sh
```

# Execution

Run the application:
```
make run-local
# or
python3 run/discord/discord_app.py
```