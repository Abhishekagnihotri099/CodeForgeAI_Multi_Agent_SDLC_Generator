import logging
from core.agent_runner import run_agent_json
from core.retry_loop import generate_with_review
from core.base64_utils import safe_b64decode
from core.file_saver import save_generated_files

from agents.requirement_agent import requirement_agent
from agents.design_agent import design_agent
from agents.coding_agent import coding_agent
from agents.review_agent import review_agent
from agents.test_agent import test_agent
from agents.documentation_agent import documentation_agent
from agents.deployment_agent import deployment_agent

logger = logging.getLogger(__name__)


def run_pipeline(user_requirement: str, project_name: str = "generated_project"):
    """
    Run the complete multi-agent SDLC pipeline.
    
    Args:
        user_requirement: User's project description
        project_name: Name of the project (used for folder structure and logging)
    
    Returns:
        Dictionary containing all generated artifacts
    """
    logger.info("="*80)
    logger.info("🚀 STARTING MULTI-AGENT SDLC PIPELINE")
    logger.info("="*80)
    logger.info(f"Project Name: {project_name}")
    logger.info(f"User Requirement: {user_requirement}")
    logger.info("="*80)
    
    try:

        # 1️⃣ Requirements
        logger.info("STAGE 1: Requirements Analysis")
        req = run_agent_json(
            requirement_agent,
            [{"role": "user", "content": user_requirement}],
            ["functional_requirements", "non_functional_requirements", "constraints", "edge_cases"],
            agent_name="Requirement Agent"
        )
        if "error" in req:
            logger.error(f"Requirements stage failed: {req['error']}")
            return req
        logger.info(f"✓ Requirements generated: {len(req.get('functional_requirements', []))} functional, {len(req.get('non_functional_requirements', []))} non-functional")

        # 2️⃣ Design
        logger.info("STAGE 2: Architecture Design")
        arch = run_agent_json(
            design_agent,
            [{"role": "user", "content": str(req)}],
            ["components", "data_models", "apis", "security", "infrastructure", "scalability_considerations"],
            agent_name="Design Agent"
        )
        if "error" in arch:
            logger.error(f"Design stage failed: {arch['error']}")
            return arch
        logger.info(f"✓ Architecture designed with {len(arch.get('components', []))} components")

        # 3️⃣ Code + Review
        logger.info("STAGE 3: Code Generation with Review")
        code = generate_with_review(arch, coding_agent, review_agent)
        if "error" in code:
            logger.error(f"Code generation stage failed: {code['error']}")
            return code
        logger.info(f"✓ Code generated: {len(code.get('files', []))} files")
        
        # Save code files
        logger.info("Saving code files...")
        code_save_stats = save_generated_files(project_name, code.get('files', []), 'src')
        logger.info(f"Code files saved: {code_save_stats['saved_count']} succeeded, {code_save_stats['failed_count']} failed")

        # 4️⃣ Tests
        logger.info("STAGE 4: Test Generation")
        tests = run_agent_json(
            test_agent,
            [{"role": "user", "content": str(code)}],
            ["tests"],
            agent_name="Test Agent"
        )
        if "error" in tests:
            logger.error(f"Test generation stage failed: {tests['error']}")
            return tests

        for t in tests.get("tests", []):
            t["content"] = safe_b64decode(t["content_base64"])
            del t["content_base64"]
        
        logger.info(f"✓ Tests generated: {len(tests.get('tests', []))} test files")
        
        # Save test files
        logger.info("Saving test files...")
        test_save_stats = save_generated_files(project_name, tests.get('tests', []), 'tests')
        logger.info(f"Test files saved: {test_save_stats['saved_count']} succeeded, {test_save_stats['failed_count']} failed")

        # 5️⃣ Docs
        logger.info("STAGE 5: Documentation Generation")
        docs = run_agent_json(
            documentation_agent,
            [{"role": "user", "content": str({"requirements": req, "architecture": arch})}],
            ["docs"],
            agent_name="Documentation Agent"
        )
        if "error" in docs:
            logger.error(f"Documentation stage failed: {docs['error']}")
            return docs

        for d in docs.get("docs", []):
            d["content"] = safe_b64decode(d["content_base64"])
            del d["content_base64"]
        
        logger.info(f"✓ Documentation generated: {len(docs.get('docs', []))} doc files")
        
        # Save documentation files
        logger.info("Saving documentation files...")
        docs_save_stats = save_generated_files(project_name, docs.get('docs', []), 'docs')
        logger.info(f"Documentation files saved: {docs_save_stats['saved_count']} succeeded, {docs_save_stats['failed_count']} failed")

        # 6️⃣ Deployment
        logger.info("STAGE 6: Deployment Configuration")
        deploy = run_agent_json(
            deployment_agent,
            [{"role": "user", "content": str(arch)}],
            ["deploy"],
            agent_name="Deployment Agent"
        )
        if "error" in deploy:
            logger.error(f"Deployment stage failed: {deploy['error']}")
            return deploy

        for f in deploy.get("deploy", []):
            f["content"] = safe_b64decode(f["content_base64"])
            del f["content_base64"]
        
        logger.info(f"✓ Deployment configs generated: {len(deploy.get('deploy', []))} files")
        
        # Save deployment files
        logger.info("Saving deployment files...")
        deploy_save_stats = save_generated_files(project_name, deploy.get('deploy', []), 'deploy')
        logger.info(f"Deployment files saved: {deploy_save_stats['saved_count']} succeeded, {deploy_save_stats['failed_count']} failed")

        result = {
            "requirements": req,
            "architecture": arch,
            "code": code,
            "tests": tests,
            "docs": docs,
            "deploy": deploy,
            "save_stats": {
                "code": code_save_stats,
                "tests": test_save_stats,
                "docs": docs_save_stats,
                "deploy": deploy_save_stats
            }
        }
        
        logger.info("="*80)
        logger.info("✅ PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("="*80)
        logger.info(f"Total files generated: {code_save_stats['saved_count'] + test_save_stats['saved_count'] + docs_save_stats['saved_count'] + deploy_save_stats['saved_count']}")
        logger.info(f"Project location: {code_save_stats.get('target_directory', 'N/A').replace('src', '')}")
        logger.info("="*80)
        
        return result
        
    except Exception as e:
        logger.error("="*80)
        logger.error("❌ PIPELINE FAILED")
        logger.error("="*80)
        logger.exception(f"Unhandled exception: {str(e)}")
        logger.error("="*80)
        
        return {
            "error": "Pipeline failed due to unrecoverable error",
            "exception": str(e)
        }
