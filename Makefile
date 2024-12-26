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
	@echo "Starting MongoDB..."
	docker run --name mongodb -d mongodb/mongodb-community-server:6.0-ubi8

start-rabbitmq:
	@echo "Starting RabbitMQ..."
	docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:4.0-management

code:
	source .venv/bin/activate && code .

run-local:
	sh .venv/bin/activate && python3 run/discord/discord_app.py

run: run-local