from util_qdrant import QdrantUtil

from logging import getLogger, INFO
logger = getLogger(__name__)
logger.setLevel(INFO)

async def tool_query_program_logs(begin_date: str, end_date: str, prompt: str, application: str=None, ip: str=None, change_id: str=None):
    """
    This tool will query program log entries based on the provided application details and date periods.
    The following must always be provided to limit the scope of the logs:
        begin_date,
        end_date,
        prompt 
    The following are additional filters that can be added to reduce the scope of the logs:
        application: name of application, 
        ip: ip address of server,
        change_id: related change_id
    """
    logger.info(">> tool_query_program_logs")
    
    
    vector_store_util = QdrantUtil()
    intent = {}
    if application:
        intent['application'] = application
    if ip:
        intent['ip'] = ip
    if change_id:
        intent['change_id'] = change_id

    results = vector_store_util.query_data(
        collection_name='opschat_data',
        prompt=prompt,
        intent=intent,
        begin_date=begin_date,
        end_date=end_date
    )

    return f"<tool-output>[tool_query_program_logs]:{results}\n</tool-output>"
    