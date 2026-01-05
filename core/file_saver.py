"""
File Saver Utility
Saves generated files to the proper directory structure: generated/{project_name}/{type}/
"""
import logging
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger(__name__)


def save_generated_files(project_name: str, files: List[Dict], file_type: str) -> Dict[str, int]:
    """
    Save generated files to the appropriate directory structure.
    
    Args:
        project_name: Name of the project (used as folder name)
        files: List of file dictionaries with 'path' and 'content' keys
        file_type: Type of files - 'src', 'tests', 'docs', or 'deploy'
    
    Returns:
        Dictionary with save statistics (saved_count, failed_count)
    """
    # Create the base directory for this project
    base_dir = Path(__file__).parent.parent / "generated" / project_name
    
    # Map file types to their target directories
    type_dirs = {
        'src': base_dir / 'src',
        'tests': base_dir / 'tests',
        'docs': base_dir / 'docs',
        'deploy': base_dir / 'deploy'
    }
    
    if file_type not in type_dirs:
        logger.error(f"Invalid file_type: {file_type}. Must be one of {list(type_dirs.keys())}")
        return {"saved_count": 0, "failed_count": len(files)}
    
    target_dir = type_dirs[file_type]
    target_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Saving {len(files)} {file_type} files to {target_dir}")
    
    saved_count = 0
    failed_count = 0
    
    for file_info in files:
        try:
            file_path = file_info.get('path', '')
            content = file_info.get('content', '')
            
            if not file_path:
                logger.warning(f"Skipping file with empty path in {file_type}")
                failed_count += 1
                continue
            
            # Create full file path
            full_path = target_dir / file_path
            
            # Create parent directories if needed
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"✓ Saved: {full_path}")
            saved_count += 1
            
        except Exception as e:
            logger.error(f"✗ Failed to save file {file_info.get('path', 'unknown')}: {str(e)}")
            failed_count += 1
    
    logger.info(f"Save complete: {saved_count} succeeded, {failed_count} failed")
    
    return {
        "saved_count": saved_count,
        "failed_count": failed_count,
        "target_directory": str(target_dir)
    }


def get_project_directory(project_name: str) -> str:
    """
    Get the full path to a project's generated directory.
    
    Args:
        project_name: Name of the project
    
    Returns:
        Full path as string
    """
    base_dir = Path(__file__).parent.parent / "generated" / project_name
    return str(base_dir)
