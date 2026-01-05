import logging
from core.json_guard import safe_parse_json
from core.schema_validator import validate_json

logger = logging.getLogger(__name__)


def run_agent_json(
    agent,
    messages,
    required_keys,
    max_retries=5,
    agent_name="agent"
):
    """
    Universal, retry-safe agent runner.
    NEVER throws JSONRepairError or JSONDecodeError.
    """
    logger.info(f"{'='*60}")
    logger.info(f"Starting {agent_name}")
    logger.info(f"{'='*60}")
    logger.debug(f"Required keys: {required_keys}")
    logger.debug(f"Input message length: {len(str(messages))} characters")

    last_error = None

    for attempt in range(1, max_retries + 1):
        logger.info(f"{agent_name} - Attempt {attempt}/{max_retries}")
        
        try:
            response = agent.generate_reply(messages=messages)
            logger.debug(f"Agent response length: {len(response.get('content', ''))} characters")
            
            parsed = validate_json(
                safe_parse_json(response["content"]),
                required_keys
            )
            
            logger.info(f"✓ {agent_name} completed successfully")
            logger.debug(f"Output keys: {list(parsed.keys())}")
            
            return parsed

        except Exception as e:
            last_error = e
            logger.warning(f"✗ {agent_name} JSON error on attempt {attempt}: {str(e)}")
            
            if attempt < max_retries:
                logger.info(f"Retrying {agent_name}...")
            else:
                logger.error(f"✗ {agent_name} failed after {max_retries} attempts")
    
    error_result = {
        "error": f"{agent_name} failed to produce valid JSON after {max_retries} retries",
        "_exception": str(last_error),
    }
    
    logger.error(f"Final error: {error_result['error']}")
    
    return error_result
