# OPSCHAT Smart IT Agent 
This is a concept test of a Smart IT agent that can use tools to analyze the environment.

## Tech Stack:
Streamlit front-end
FastAPI backend
RabbitMQ message queue

### RabbitMQ
To start the *RabbitMQ backend* initially, run:
```bash
make start-rabbitmq
```

### Queue Mangaer
Then to start the *Queue Manager*
Run the following command from project root
```bash
make run-queue
```

### FastAPI backend
Run the following command from project root
```bash
make run-api
```
or
```bash
python3 -m run/opschat/app-api.py
```

### Streamlit frontend
To start the front-end, run the following command from project root
```bash
make run-front
```
or
```bash
python3 -m streamlit run run/opschat/opschat-2.py
```

