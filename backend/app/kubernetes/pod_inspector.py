from typing import Dict, List, Any
from loguru import logger
from app.kubernetes.executor import KubectlExecutor

class PodInspector:
    def __init__(self, executor: KubectlExecutor):
        self.executor = executor

    def inspect(self, cluster: str, namespace: str) -> Dict[str, Any]:
        """
        Retrieves all pods in a namespace and identifies unhealthy ones.
        """
        logger.info(f"Inspecting pods in namespace: {namespace} on cluster: {cluster}")
        
        args = ["get", "pods"]
        if namespace == "all-namespaces":
            args.append("-A")
        
        result = self.executor.execute(cluster, args, namespace)
        
        if not result["success"]:
            logger.error(f"Failed to inspect pods: {result['stderr']}")
            return {
                "healthy": False,
                "problematic_pods": [],
                "error": result["stderr"],
                "raw_output": ""
            }

        stdout = result["stdout"]
        problematic_pods = []
        lines = stdout.strip().split("\n")
        
        if len(lines) <= 1:
            return {
                "healthy": True,
                "problematic_pods": [],
                "error": None,
                "raw_output": stdout
            }

        # Parse lines
        header = lines[0].lower().split()
        is_all_ns = "namespace" in header
        
        for line in lines[1:]:
            parts = line.split()
            if not parts:
                continue
                
            try:
                # Layout with namespace column or not
                if is_all_ns:
                    ns = parts[0]
                    name = parts[1]
                    ready = parts[2]
                    status = parts[3]
                    restarts = parts[4]
                    age = parts[5]
                else:
                    ns = namespace
                    name = parts[0]
                    ready = parts[1]
                    status = parts[2]
                    restarts = parts[3]
                    age = parts[4]
                
                # Check status and readiness
                # Typical problematic statuses
                unhealthy_statuses = [
                    "crashloopbackoff", "imagepullbackoff", "errimagepull", 
                    "error", "oomkilled", "pending", "containercreating",
                    "failed", "runcontainererror"
                ]
                
                # Split ready (e.g. 0/1, 1/2)
                ready_split = ready.split("/")
                not_ready = False
                if len(ready_split) == 2:
                    not_ready = ready_split[0] != ready_split[1]

                is_unhealthy = status.lower() in unhealthy_statuses or not_ready
                
                if is_unhealthy:
                    problematic_pods.append({
                        "name": name,
                        "namespace": ns,
                        "ready": ready,
                        "status": status,
                        "restarts": restarts,
                        "age": age
                    })
            except Exception as e:
                logger.warning(f"Failed to parse pod line: '{line}' - Error: {e}")

        healthy = len(problematic_pods) == 0
        return {
            "healthy": healthy,
            "problematic_pods": problematic_pods,
            "error": None,
            "raw_output": stdout
        }
