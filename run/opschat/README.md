# OPSCHAT Smart IT Agent 
This is a concept test of a Smart IT agent that can use tools to analyze the environment.

## Streamlit / creo-1
Test configuration: Streamlit front end that talks to a FastAPI with a creo-1 agent.

### Streamlit frontend
To start the front-end, run the following command from project root
```bash
python3 -m streamlit run run/opschat/opschat-2.py
```

### FastAPI backend
To start the back-end, run the following command from project root
```bash
python3 -m run/opschat/app-api.py
```
