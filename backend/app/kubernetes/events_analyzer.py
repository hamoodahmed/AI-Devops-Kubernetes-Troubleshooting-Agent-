from typing import Dict, List, Any
from loguru import logger
from app.kubernetes.executor import KubectlExecutor

class EventsAnalyzer:
    def __init__(self, executor: KubectlExecutor):
        self.executor = executor

    def analyze(self, cluster: str, namespace: str) -> Dict[str, Any]:
        """
        Gathers events from the namespace, filters for warnings/failures, and summarizes findings.
        """
        logger.info(f"Analyzing events in namespace: {namespace} on cluster: {cluster}")
        
        args = ["get", "events", "--sort-by=.metadata.creationTimestamp"]
        if namespace == "all-namespaces":
            args.append("-A")
            
        result = self.executor.execute(cluster, args, namespace)
        
        if not result["success"]:
            logger.error(f"Failed to fetch events: {result['stderr']}")
            return {
                "success": False,
                "warnings": [],
                "error": result["stderr"],
                "raw_output": ""
            }

        stdout = result["stdout"]
        warnings = []
        lines = stdout.strip().split("\n")
        
        if len(lines) <= 1:
            return {
                "success": True,
                "warnings": [],
                "error": None,
                "raw_output": stdout
            }

        # Header parsing to find columns
        header = lines[0].lower()
        
        # Keywords to identify problematic warning/error events
        warning_types = ["warning", "failed", "backoff", "error", "unhealthy", "failedscheduling", "errimagepull"]
        
        for line in lines[1:]:
            if not line.strip():
                continue
                
            is_warning = any(kw in line.lower() for kw in warning_types)
            if is_warning:
                # Capture events details
                # A standard event line looks like:
                # LAST SEEN   TYPE      REASON      OBJECT      MESSAGE
                # Or with Namespace in front:
                # NAMESPACE   LAST SEEN   TYPE   REASON   OBJECT   MESSAGE
                warnings.append(line.strip())

        # Limit to the last 20 warning events to keep content concise and token counts friendly
        warnings = warnings[-20:]

        return {
            "success": True,
            "warnings": warnings,
            "error": None,
            "raw_output": stdout if len(lines) < 50 else "\n".join(lines[-50:])
        }
