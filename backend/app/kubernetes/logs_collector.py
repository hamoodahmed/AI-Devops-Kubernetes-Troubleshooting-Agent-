import re
from typing import Dict, List, Any
from loguru import logger
from app.kubernetes.executor import KubectlExecutor

class LogsCollector:
    def __init__(self, executor: KubectlExecutor):
        self.executor = executor

    def collect(self, cluster: str, problematic_pods: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Collects and filters logs for a list of problematic pods.
        """
        logger.info(f"Collecting logs for {len(problematic_pods)} problematic pods on cluster: {cluster}")
        
        logs_payload = {}
        
        for pod in problematic_pods:
            pod_name = pod["name"]
            namespace = pod["namespace"]
            
            # Fetch tail of logs (last 100 lines) to avoid token blowout
            args = ["logs", pod_name, "--tail=100"]
            result = self.executor.execute(cluster, args, namespace)
            
            if not result["success"]:
                logs_payload[pod_name] = {
                    "pod_name": pod_name,
                    "namespace": namespace,
                    "success": False,
                    "error": result["stderr"],
                    "filtered_logs": []
                }
                continue

            raw_logs = result["stdout"]
            lines = raw_logs.strip().split("\n")
            
            # Filter logs for errors, exceptions, stacktraces
            filtered = []
            keywords = [
                "error", "exception", "failed", "fatal", "connection", 
                "refused", "missing", "not found", "oom", "killed", 
                "exit", "crash", "traceback", "keyerror", "nullpointer"
            ]
            
            # We also want to capture Context Lines around exceptions (e.g. standard Traceback blocks)
            # A simple rule: if a line is a traceback block or contains a keyword, include it.
            # If a line starts with traceback indentation (spaces), include it if previous line was included.
            in_traceback = False
            for line in lines:
                is_err_line = any(kw in line.lower() for kw in keywords)
                
                # Check for traceback block starter
                if "traceback" in line.lower():
                    in_traceback = True
                    filtered.append(line)
                    continue
                
                if in_traceback:
                    # If it starts with space (python indentation) or is a python traceback file reference
                    if line.startswith(" ") or "File \"" in line:
                        filtered.append(line)
                    else:
                        in_traceback = False
                        if is_err_line:
                            filtered.append(line)
                else:
                    if is_err_line:
                        filtered.append(line)

            # If filtered list is empty, default to returning the last 15 lines of raw logs
            if not filtered:
                filtered = lines[-15:] if len(lines) > 15 else lines

            logs_payload[pod_name] = {
                "pod_name": pod_name,
                "namespace": namespace,
                "success": True,
                "filtered_logs": filtered,
                "total_lines_read": len(lines)
            }
            
        return logs_payload
