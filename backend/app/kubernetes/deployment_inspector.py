from typing import Dict, List, Any
from loguru import logger
from app.kubernetes.executor import KubectlExecutor

class DeploymentInspector:
    def __init__(self, executor: KubectlExecutor):
        self.executor = executor

    def inspect(self, cluster: str, namespace: str) -> Dict[str, Any]:
        """
        Inspects deployments and collects metrics about desired vs. available replicas, and rollout failures.
        """
        logger.info(f"Inspecting deployments in namespace: {namespace} on cluster: {cluster}")
        
        args = ["get", "deployments"]
        if namespace == "all-namespaces":
            args.append("-A")
            
        result = self.executor.execute(cluster, args, namespace)
        
        if not result["success"]:
            logger.error(f"Failed to fetch deployments: {result['stderr']}")
            return {
                "success": False,
                "unhealthy_deployments": [],
                "error": result["stderr"],
                "raw_output": ""
            }

        stdout = result["stdout"]
        lines = stdout.strip().split("\n")
        
        if len(lines) <= 1:
            return {
                "success": True,
                "unhealthy_deployments": [],
                "error": None,
                "raw_output": stdout
            }

        header = lines[0].lower().split()
        is_all_ns = "namespace" in header
        
        unhealthy_deployments = []
        
        for line in lines[1:]:
            parts = line.split()
            if not parts:
                continue
                
            try:
                if is_all_ns:
                    ns = parts[0]
                    name = parts[1]
                    ready = parts[2]
                    uptodate = parts[3]
                    available = parts[4]
                    age = parts[5]
                else:
                    ns = namespace
                    name = parts[0]
                    ready = parts[1]
                    uptodate = parts[2]
                    available = parts[3]
                    age = parts[4]
                
                # Check replica health
                # ready format is "X/Y" where X = available, Y = desired
                ready_parts = ready.split("/")
                if len(ready_parts) == 2:
                    current_ready = int(ready_parts[0])
                    desired_ready = int(ready_parts[1])
                    
                    if current_ready < desired_ready or available == "0":
                        # Fetch extra details using describe deployment
                        desc_args = ["describe", "deployment", name]
                        desc_result = self.executor.execute(cluster, desc_args, ns)
                        details = desc_result["stdout"] if desc_result["success"] else desc_result["stderr"]
                        
                        unhealthy_deployments.append({
                            "name": name,
                            "namespace": ns,
                            "ready": ready,
                            "up_to_date": uptodate,
                            "available": available,
                            "age": age,
                            "details": details
                        })
            except Exception as e:
                logger.warning(f"Failed to parse deployment line: '{line}' - Error: {e}")

        return {
            "success": True,
            "unhealthy_deployments": unhealthy_deployments,
            "error": None,
            "raw_output": stdout
        }
