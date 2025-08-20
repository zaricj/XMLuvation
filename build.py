import subprocess
import sys
import os

def build_project():
    """Build the PySide6 project"""
    try:
        # Navigate to src directory
        os.chdir('src')
        
        # Run pyside6-deploy
        result = subprocess.run([
            sys.executable, '-m', 'pyside6_deploy',
            '-c', 'pysidedeploy.spec'
        ], check=True, capture_output=True, text=True)
        
        print("Build successful!")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(e.stderr)
        return False
    
    return True

if __name__ == "__main__":
    build_project()
