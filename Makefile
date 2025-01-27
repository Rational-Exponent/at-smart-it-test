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
		docker run --name mongodb -d -p 27017:27017 mongodb/mongodb-community-server:6.0-ubi8; \
	fi


start-rabbitmq:
	@echo "Starting RabbitMQ..."
	@container_id=$(shell docker ps -aq -f name=rabbitmq); \
	echo "Container ID: $$container_id"; \
	if [ ! -z "$$container_id" ]; then \
		if [ $(shell docker ps -q -f name=rabbitmq) ]; then \
			echo "RabbitMQ container is already running."; \
		else \
			echo "RabbitMQ container exists but is stopped, starting..."; \
			docker start rabbitmq; \
		fi \
	else \
		echo "RabbitMQ container does not exist, creating new one..."; \
		docker run -it --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:4.0-management; \
	fi
	
start-all-services: start-mongo start-rabbitmq

code:
	source .venv/bin/activate && code .

run-local-discord:
	sh .venv/bin/activate && python3 run/discord/discord_app.py

run-front:
	python3 -m streamlit run run/opschat/opschat-2.py

run-api:
	python3 run/opschat/app-api.py

run-queue:
	python3 run/opschat/app-queue.py


start-opschat: run-api run-queue run-front