import os
import json
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel, HttpUrl
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="OneForAll Scanner API", version="1.0.0")

class ScanRequest(BaseModel):
    url: str
    http_requests: bool = False

class ScanResponse(BaseModel):
    results: List[Dict[Any, Any]]
    target: str
    total_count: int


@app.post("/scan", response_model=ScanResponse)
async def scan_domain(url: str = Form(...), http_requests: bool = Form(False)):
    """
    Scan a domain using OneForAll and return the results as JSON
    """
    target_domain = url.replace("http://", "").replace("https://", "").split("/")[0]
    logger.info(f"Starting scan for domain: {target_domain}")
    
    # Change to OneForAll directory
    oneforall_dir = "/app/OneForAll"
    if not os.path.exists(oneforall_dir):
        logger.error(f"OneForAll directory not found: {oneforall_dir}")
        raise HTTPException(status_code=500, detail="OneForAll not found. Please ensure it's properly installed.")
    
    # Check if oneforall.py exists
    oneforall_script = os.path.join(oneforall_dir, "oneforall.py")
    if not os.path.exists(oneforall_script):
        logger.error(f"OneForAll script not found: {oneforall_script}")
        # List directory contents for debugging
        try:
            contents = os.listdir(oneforall_dir)
            logger.info(f"OneForAll directory contents: {contents}")
        except Exception as e:
            logger.error(f"Could not list OneForAll directory: {e}")
        raise HTTPException(status_code=500, detail=f"OneForAll script not found at {oneforall_script}")
    
    try:
        # Run OneForAll scan
        cmd = [
            "python3.10", 
            "oneforall.py", 
            "--target", target_domain, 
            "--fmt", "json"
        ]
        
        # Add HTTP requests parameter
        if http_requests:
            cmd.extend(["--req", "True"])
        else:
            cmd.extend(["--req", "False"])
            
        cmd.append("run")
        
        logger.info(f"Executing command: {' '.join(cmd)} in directory: {oneforall_dir}")
        
        # Execute the command in OneForAll directory
        result = subprocess.run(
            cmd,
            cwd=oneforall_dir,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        logger.info(f"Command exit code: {result.returncode}")
        logger.info(f"Command stdout: {result.stdout}")
        logger.info(f"Command stderr: {result.stderr}")
        
        if result.returncode != 0:
            error_msg = f"OneForAll scan failed with exit code {result.returncode}. Stderr: {result.stderr}. Stdout: {result.stdout}"
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
        
        # Look for the generated JSON file in the results directory
        json_file = os.path.join(oneforall_dir, "results", f"{target_domain}.json")
        logger.info(f"Looking for output file: {json_file}")
        
        if not os.path.exists(json_file):
            # List files in results directory to see what was created
            results_dir = os.path.join(oneforall_dir, "results")
            try:
                if os.path.exists(results_dir):
                    files = [f for f in os.listdir(results_dir) if f.endswith('.json')]
                    logger.info(f"JSON files found in OneForAll results directory: {files}")
                else:
                    logger.error(f"Results directory does not exist: {results_dir}")
                    files = []
            except Exception as e:
                logger.error(f"Could not list files in OneForAll results directory: {e}")
                files = []
            
            raise HTTPException(
                status_code=500, 
                detail=f"Expected output file {target_domain}.json not found in results directory. Available JSON files: {files}"
            )
        
        # Read the JSON results
        logger.info(f"Reading results from: {json_file}")
        with open(json_file, 'r', encoding='utf-8') as f:
            scan_results = json.load(f)
        
        logger.info(f"Scan completed successfully for {target_domain}")
        
        return ScanResponse(
            results=scan_results,
            target=target_domain,
            total_count=len(scan_results)
        )
        
    except subprocess.TimeoutExpired:
        logger.error(f"Scan timeout for domain: {target_domain}")
        raise HTTPException(status_code=408, detail="Scan timeout after 5 minutes")
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to parse JSON results: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during scan: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")

@app.get("/", include_in_schema=False)
async def root():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9403)
