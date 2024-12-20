import subprocess
import logging
import venv
import os
from typing import Optional, Dict
from pathlib import Path

class SignalExecutor:
    def __init__(self, script_path: str, project_path: str):
        self.script_path = Path(script_path)
        self.project_path = Path(project_path)
        self.logger = logging.getLogger(__name__)
        
        if not self.script_path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")
        if not self.project_path.exists():
            raise FileNotFoundError(f"Project directory not found: {project_path}")
        
        # Verify poetry.lock exists in project path
        if not (self.project_path / "poetry.lock").exists():
            raise FileNotFoundError(f"poetry.lock not found in {project_path}")

    def execute_script(self) -> Optional[str]:
        """Execute external Python script using poetry and return its output."""
        try:
            # Check if poetry is installed
            subprocess.run(
                ["poetry", "--version"],
                capture_output=True,
                check=True
            )
            
            # Execute script using poetry
            result = subprocess.run(
                ["poetry", "run", "python", str(self.script_path)],
                capture_output=True,
                text=True,
                check=True,
                cwd=str(self.project_path)
            )
            
            if result.stderr:
                self.logger.warning(f"Script produced warnings: {result.stderr}")
                
            return result.stdout
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Script execution failed: {e.stderr}")
            raise RuntimeError(f"Failed to execute script: {e.stderr}")
        except FileNotFoundError:
            self.logger.error("Poetry not found. Please ensure poetry is installed.")
            raise

    def parse_output(self, output: str) -> Optional[Dict]:
        """Parse the script output into structured data."""
        if not output or not output.strip():
            self.logger.warning("Empty output received")
            return None
            
        try:
            signal_data = {}
            for line in output.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    signal_data[key.strip()] = value.strip()
                    
            if not signal_data:
                self.logger.warning("No valid key-value pairs found in output")
                
            return signal_data
            
        except Exception as e:
            self.logger.error(f"Error parsing output: {str(e)}")
            return None