.PHONY: setup-env setup-install setup code run-local run

setup-env:
	@echo "Creating virtual environment..."
	python3 -m venv .venv
	@echo "Virtual environment created."

setup-install:
	@echo "Installing dependencies..."
	source .venv/bin/activate && pip install -r requirements.txt
	@echo "Dependencies installed."

setup: setup-env setup-install

start-mongo:
	@echo "Checking if MongoDB container exists..."
	@container_id=$(shell docker ps -aq -f name=mongodb); \
	echo "Container ID: $$container_id"; \
	if [ ! -z "$$container_id" ]; then \
		if [ $(shell docker ps -q -f name=mongodb) ]; then \
			echo "MongoDB container is already running."; \
		else \
			echo "MongoDB container exists but is stopped, starting..."; \
			docker start mongodb; \
		fi \
	else \
		echo "MongoDB container does not exist, creating new one..."; \
		docker run --name mongodb -d mongodb/mongodb-community-server:6.0-ubi8; \
	fi



start-rabbitmq:
	@echo "Starting RabbitMQ..."
	docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:4.0-management

start-all: start-mongo start-rabbitmq

code:
	source .venv/bin/activate && code .

run-local-discord:
	sh .venv/bin/activate && python3 run/discord/discord_app.py

run: run-local