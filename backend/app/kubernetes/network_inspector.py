from typing import Dict, List, Any
from loguru import logger
from app.kubernetes.executor import KubectlExecutor

class NetworkInspector:
    def __init__(self, executor: KubectlExecutor):
        self.executor = executor

    def inspect(self, cluster: str, namespace: str) -> Dict[str, Any]:
        """
        Inspects networking components like Services and Endpoints.
        Checks for missing endpoints, DNS concerns, or label selector mismatches.
        """
        logger.info(f"Inspecting network (services/endpoints) in namespace: {namespace} on cluster: {cluster}")
        
        svc_args = ["get", "svc"]
        ep_args = ["get", "endpoints"]
        
        if namespace == "all-namespaces":
            svc_args.append("-A")
            ep_args.append("-A")
            
        svc_res = self.executor.execute(cluster, svc_args, namespace)
        ep_res = self.executor.execute(cluster, ep_args, namespace)
        
        if not svc_res["success"]:
            logger.error(f"Failed to fetch services: {svc_res['stderr']}")
            return {
                "success": False,
                "error": svc_res["stderr"],
                "services": "",
                "endpoints": "",
                "issues": []
            }

        services_out = svc_res["stdout"]
        endpoints_out = ep_res["stdout"] if ep_res["success"] else ""
        
        # Analyze mismatching selector/endpoints issues
        issues = []
        ep_lines = endpoints_out.strip().split("\n")
        
        if len(ep_lines) > 1:
            header = ep_lines[0].lower().split()
            is_all_ns = "namespace" in header
            
            for line in ep_lines[1:]:
                parts = line.split()
                if not parts:
                    continue
                try:
                    if is_all_ns:
                        ns = parts[0]
                        name = parts[1]
                        endpoints = parts[2]
                    else:
                        ns = namespace
                        name = parts[0]
                        endpoints = parts[1]
                        
                    # If endpoints are <none> or empty list, it means selector mismatch or pod failure!
                    if endpoints.lower() in ("<none>", "", "<pending>"):
                        issues.append({
                            "service_name": name,
                            "namespace": ns,
                            "issue": "Missing endpoints (endpoints column is <none>). This usually points to a pod label selector mismatch or pod health issue.",
                            "endpoints": endpoints
                        })
                except Exception as e:
                    logger.warning(f"Failed to parse endpoints line: '{line}' - Error: {e}")

        return {
            "success": True,
            "error": None,
            "services": services_out,
            "endpoints": endpoints_out,
            "issues": issues
        }
