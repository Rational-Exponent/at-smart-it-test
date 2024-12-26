# Creo-1
### An open-source framework for developing AI Agent Networks

# Enough RAG, time for MOP!
### Message Orchestration Pattern

This repo implements an improvement on the RAG infrastructure, the **Message Orchestration Pattern**, or **MOP**.

This architecture aims to resolve some of the biggest problems for growing and scaling AI Agent systems:
- Efficient agent-to-agent communication
- Ease of adding new independent agents
- Abstractions for integrating with local or cloud based LLM providers
- Abstractions for custom tool calling

We accomplish this operation by implementing a robust message exchange system using a queue service provider. In our examples we will use RabbitMQ, but this is an abstract layer that can be replaced with another provider like Kafka or SQS.

## Scalable Agents
By using a queue, we can create independant and scalable queue consumer agent, wich we can either pool or distribute acrosss compute resources. This allows us to scale each agent role independently. 

# Tech Stack

- Docker
- RabbitMQ
- MongoDB
- OpenAI (swapable service provider)
### (Optional)
- Discord - used in example `run\discord`


# Setup

## Prerequisites

- Docker - (https://docs.docker.com/engine/install/)

## Environment Variables

1. Copy `.env.example` to `.env`
2. Update the `<values>` as indicated in the file

## Installation

Run the following to set up a `venv` and install dependencies:
```bash
make setup
```

### Start Docker

Follow instructions for your OS to start the Docker app

### Start RabbitMQ
```bash
# RabbitMQ 4.0.x
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:4.0-management
```

### Start MongoDB
```bash
export MONGODB_VERSION=6.0-ubi8
docker run --name mongodb -d mongodb/mongodb-community-server:$MONGODB_VERSION
```

# Running examples
## Simple Discord bot
Discord is an excellent tool for testing chat bots because it handles the UI overhead, allowing you to focus on feature design.

The following command will launch a simple discord bot using the example located at `run/local/discord_bot.py`.
```
make run-local
```
You will need to make sure you have the following vaues defined in your `.env` file:
```
DISCORD_CHANNEL_ID=<your-channel-id>
DISCORD_TOKEN=<your-discord-token>
```