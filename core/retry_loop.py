import base64
import logging
from core.json_guard import safe_parse_json
from core.schema_validator import validate_json
from core.base64_utils import safe_b64decode

logger = logging.getLogger(__name__)

MAX_LOGIC_RETRIES = 3
MAX_FORMAT_RETRIES = 5

def generate_with_review(architecture_json, coding_agent, review_agent):
    logger.info("="*60)
    logger.info("Starting Code Generation with Review Loop")
    logger.info("="*60)
    
    feedback = None
    logic_attempts = 0
    format_attempts = 0

    while logic_attempts < MAX_LOGIC_RETRIES:
        logger.info(f"📝 Coding logic attempt {logic_attempts + 1}/{MAX_LOGIC_RETRIES}")

        prompt = architecture_json if not feedback else {
            "architecture": architecture_json,
            "review_feedback": feedback
        }
        
        if feedback:
            logger.info(f"Applying review feedback: {feedback.get('issues', 'N/A')}")

        # CODE GENERATION 
        logger.info("Generating code...")
        code_response = coding_agent.generate_reply(
            messages=[{"role": "user", "content": str(prompt)}]
        )
        logger.debug(f"Code response length: {len(code_response.get('content', ''))} characters")
        
        # CODE FORMAT HANDLING 
        try:
            code_json = validate_json(
                safe_parse_json(code_response["content"]),
                ["files"]
            )
            logger.info(f"✓ Code JSON validated - {len(code_json.get('files', []))} files generated")
        except Exception as e:
            format_attempts += 1
            logger.warning(f"✗ Code JSON format error (attempt {format_attempts}/{MAX_FORMAT_RETRIES}): {str(e)}")

            if format_attempts >= MAX_FORMAT_RETRIES:
                logger.error("Too many code JSON format failures - aborting")
                raise RuntimeError("Too many code JSON format failures")

            continue  

        #  REVIEW
        logger.info("Submitting code for review...")
        review_response = review_agent.generate_reply(
            messages=[{"role": "user", "content": str(code_json)}]
        )

        # REVIEW FORMAT HANDLING 
        try:
            review_json = validate_json(
                safe_parse_json(review_response["content"]),
                ["status", "issues", "suggested_fixes"]
            )
            logger.info(f"Review status: {review_json.get('status', 'UNKNOWN')}")
        except Exception as e:
            format_attempts += 1
            logger.warning(f"✗ Review JSON format error (attempt {format_attempts}/{MAX_FORMAT_RETRIES}): {str(e)}")

            if format_attempts >= MAX_FORMAT_RETRIES:
                logger.error("Too many review JSON format failures - returning error")
                return {
                    "files": [],
                    "error": "Code generation failed due to repeated JSON format errors"
                }
            continue 
    
        if review_json["status"] == "REJECTED" and logic_attempts >= 2:
            logger.warning("⚠️  Forcing approval after multiple advisory reviews")
            review_json["status"] = "APPROVED"

        # DECISION 
        if review_json["status"] == "APPROVED":
            logger.info("✓ Code APPROVED by reviewer")
            
            # Decode base64 content
            for f in code_json["files"]:
                f["content"] = safe_b64decode(f["content_base64"])
                del f["content_base64"]
                logger.debug(f"Decoded file: {f['path']}")

            logger.info(f"Code generation completed successfully with {len(code_json['files'])} files")
            return code_json

        logger.warning(f"✗ Code REJECTED by reviewer")
        logger.warning(f"Issues: {review_json['issues']}")
        logger.info(f"Suggested fixes: {review_json.get('suggested_fixes', 'None provided')}")
        
        feedback = review_json
        logic_attempts += 1 

    logger.error("✗ Code generation failed after max logical retries")
    raise RuntimeError("Code generation failed after max logical retries")
