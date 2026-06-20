import os
import shutil
import subprocess
import yaml
from typing import Dict, List, Any, Optional
from loguru import logger
from app.core.config import settings

class KubectlExecutor:
    def __init__(self):
        self.kubectl_path = shutil.which("kubectl")
        self.has_kubectl = self.kubectl_path is not None
        
        if not self.has_kubectl:
            logger.warning("kubectl command line utility was not found on the system path. Simulation mode will be enabled by default.")

    def get_available_contexts(self) -> List[Dict[str, Any]]:
        """
        Retrieves all contexts from the local kubeconfig file.
        If kubeconfig or kubectl is missing, returns simulated clusters.
        """
        contexts = []
        
        # Try to parse the kubeconfig file directly using PyYAML
        kubeconfig_path = os.path.expanduser(settings.KUBECONFIG_PATH)
        if os.path.exists(kubeconfig_path):
            try:
                with open(kubeconfig_path, "r") as f:
                    config_data = yaml.safe_load(f)
                if config_data and "contexts" in config_data:
                    current_context = config_data.get("current-context", "")
                    for ctx in config_data["contexts"]:
                        name = ctx.get("name", "")
                        contexts.append({
                            "name": name,
                            "is_active": name == current_context,
                            "is_simulated": False,
                            "server": self._get_cluster_server(config_data, ctx.get("context", {}).get("cluster", ""))
                        })
            except Exception as e:
                logger.error(f"Error parsing kubeconfig at {kubeconfig_path}: {e}")

        # If kubectl is available, we can also query it
        if not contexts and self.has_kubectl:
            try:
                # Use kubectl config get-contexts
                cmd = ["kubectl", "config", "get-contexts", "-o", "name"]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                if res.returncode == 0:
                    lines = res.stdout.strip().split("\n")
                    # Get active context
                    active_res = subprocess.run(["kubectl", "config", "current-context"], capture_output=True, text=True, timeout=5)
                    active_ctx = active_res.stdout.strip() if active_res.returncode == 0 else ""
                    
                    for name in lines:
                        if name:
                            contexts.append({
                                "name": name,
                                "is_active": name == active_ctx,
                                "is_simulated": False,
                                "server": "Local Cluster"
                            })
            except Exception as e:
                logger.error(f"Error running kubectl get-contexts: {e}")

        # Always offer simulation contexts for development and testing
        contexts.append({
            "name": "simulation-minikube-dev",
            "is_active": len(contexts) == 0,
            "is_simulated": True,
            "server": "https://127.0.0.1:8443 (Simulated Developer Cluster)"
        })
        contexts.append({
            "name": "simulation-eks-production",
            "is_active": False,
            "is_simulated": True,
            "server": "https://aws-eks.prod.k8s.local (Simulated Production Cluster)"
        })
        
        return contexts

    def _get_cluster_server(self, config_data: Dict[str, Any], cluster_name: str) -> Optional[str]:
        if "clusters" in config_data:
            for cls in config_data["clusters"]:
                if cls.get("name") == cluster_name:
                    return cls.get("cluster", {}).get("server")
        return None

    def execute(self, cluster_context: str, args: List[str], namespace: str = "default") -> Dict[str, Any]:
        """
        Executes a kubectl command on a specific cluster context.
        If it's a simulated context, or kubectl is not found, returns simulated responses.
        """
        is_simulated = cluster_context.startswith("simulation-") or not self.has_kubectl
        
        if is_simulated:
            logger.info(f"[SIMULATION] Executing: kubectl --context {cluster_context} -n {namespace} {' '.join(args)}")
            return self._get_simulated_execution(cluster_context, args, namespace)

        # Real command execution
        cmd = ["kubectl", "--context", cluster_context, "-n", namespace] + args
        logger.info(f"Executing: {' '.join(cmd)}")
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return {
                "success": res.returncode == 0,
                "stdout": res.stdout,
                "stderr": res.stderr,
                "returncode": res.returncode
            }
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout executing command: {' '.join(cmd)}")
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timed out after 10 seconds.",
                "returncode": -1
            }
        except Exception as e:
            logger.error(f"Error executing command {' '.join(cmd)}: {e}")
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }

    def _get_simulated_execution(self, cluster_context: str, args: List[str], namespace: str) -> Dict[str, Any]:
        # Helper to generate simulated output
        # Check what command is being executed
        cmd_str = " ".join(args)
        
        # We can extract the forced scenario from the environment or active context name
        # If the environment has a specific scenario (e.g., set during the API request), we can use it.
        # But wait! To let the orchestrator determine which scenario output to generate,
        # we can store/retrieve it from a thread-local/session context or pass a metadata/scenario parameter.
        # Let's inspect the environment variable `ACTIVE_SIMULATION_SCENARIO` which we will set in the request context!
        scenario = os.getenv("ACTIVE_SIMULATION_SCENARIO", "CrashLoopBackOff")

        if "get pods" in cmd_str:
            return self._sim_get_pods(scenario)
        elif "logs" in cmd_str:
            # logs <pod_name>
            pod_name = args[-1] if len(args) > 1 else ""
            return self._sim_logs(scenario, pod_name)
        elif "get events" in cmd_str:
            return self._sim_get_events(scenario)
        elif "describe deployment" in cmd_str:
            dep_name = args[-1] if len(args) > 1 else ""
            return self._sim_describe_deployment(scenario, dep_name)
        elif "get deployment" in cmd_str:
            return self._sim_get_deployments(scenario)
        elif "get svc" in cmd_str or "get service" in cmd_str:
            return self._sim_get_services(scenario)
        elif "get endpoints" in cmd_str:
            return self._sim_get_endpoints(scenario)
        
        # Fallback default
        return {
            "success": True,
            "stdout": f"Simulated execution of: kubectl {' '.join(args)} successful.",
            "stderr": "",
            "returncode": 0
        }

    def _sim_get_pods(self, scenario: str) -> Dict[str, Any]:
        if scenario == "CrashLoopBackOff":
            stdout = (
                "NAME                               READY   STATUS              RESTARTS   AGE\n"
                "payment-service-58d7c49b6b-df2jk   0/1     CrashLoopBackOff    6 (2m ago) 15m\n"
                "frontend-7fc459bdf8-9lmop          1/1     Running             0          4h\n"
                "order-db-0                         1/1     Running             0          10d\n"
            )
        elif scenario == "ImagePullBackOff":
            stdout = (
                "NAME                               READY   STATUS              RESTARTS   AGE\n"
                "auth-service-7bbcd459d8-kp810      0/1     ImagePullBackOff    0          4m\n"
                "frontend-7fc459bdf8-9lmop          1/1     Running             0          4h\n"
                "payment-service-58d7c49b6b-df2jk   1/1     Running             1          15m\n"
            )
        elif scenario == "OOMKilled":
            stdout = (
                "NAME                               READY   STATUS              RESTARTS   AGE\n"
                "report-generator-d86bfcd8-89qws    0/1     OOMKilled           4 (1m ago) 8m\n"
                "frontend-7fc459bdf8-9lmop          1/1     Running             0          4h\n"
                "order-db-0                         1/1     Running             0          10d\n"
            )
        elif scenario == "SelectorMismatch":
            stdout = (
                "NAME                               READY   STATUS              RESTARTS   AGE\n"
                "notification-processor-b7d8d-xpl8  1/1     Running             0          6m\n"
                "frontend-7fc459bdf8-9lmop          1/1     Running             0          4h\n"
            )
        else: # Healthy
            stdout = (
                "NAME                               READY   STATUS              RESTARTS   AGE\n"
                "frontend-7fc459bdf8-9lmop          1/1     Running             0          4h\n"
                "payment-service-58d7c49b6b-df2jk   1/1     Running             0          4h\n"
                "order-db-0                         1/1     Running             0          10d\n"
            )
        return {"success": True, "stdout": stdout, "stderr": "", "returncode": 0}

    def _sim_logs(self, scenario: str, pod_name: str) -> Dict[str, Any]:
        if scenario == "CrashLoopBackOff":
            stdout = (
                "2026-06-20 10:45:01 [INFO] Starting Payment Service Version 2.4.1\n"
                "2026-06-20 10:45:02 [INFO] Loading configuration modules...\n"
                "2026-06-20 10:45:02 [ERROR] Startup failed! Database URL is not set.\n"
                "Traceback (most recent call last):\n"
                "  File \"/app/main.py\", line 42, in <module>\n"
                "    db_url = os.environ['DATABASE_URL']\n"
                "  File \"/usr/local/lib/python3.12/os.py\", line 679, in __getitem__\n"
                "    raise KeyError(key) from None\n"
                "KeyError: 'DATABASE_URL'\n"
            )
        elif scenario == "ImagePullBackOff":
            stdout = ""
            stderr = "Error from server (BadRequest): container \"auth-service\" in pod \"auth-service-7bbcd459d8-kp810\" is waiting to start: ImagePullBackOff"
            return {"success": False, "stdout": stdout, "stderr": stderr, "returncode": 1}
        elif scenario == "OOMKilled":
            stdout = (
                "2026-06-20 10:51:10 [INFO] Generating monthly financial CSV reports...\n"
                "2026-06-20 10:51:12 [INFO] Processing batch of 100,000 transaction records...\n"
                "2026-06-20 10:51:15 [DEBUG] Reading transaction IDs into memory...\n"
                "2026-06-20 10:51:18 [DEBUG] Allocating structures for data aggregation...\n"
                "Killed\n"
            )
        elif scenario == "SelectorMismatch":
            stdout = (
                "2026-06-20 10:49:00 [INFO] Notification processor started and listening to queue 'notifications'...\n"
                "2026-06-20 10:49:05 [INFO] Heartbeat OK. Waiting for connections...\n"
            )
        else:
            stdout = "2026-06-20 10:00:00 [INFO] Server running on port 8080.\n"
        return {"success": True, "stdout": stdout, "stderr": "", "returncode": 0}

    def _sim_get_events(self, scenario: str) -> Dict[str, Any]:
        if scenario == "CrashLoopBackOff":
            stdout = (
                "LAST SEEN   TYPE      REASON      OBJECT                                 MESSAGE\n"
                "2m ago      Warning   BackOff     pod/payment-service-58d7c49b6b-df2jk   Back-off restarting failed container\n"
                "15m ago     Normal    Scheduled   pod/payment-service-58d7c49b6b-df2jk   Successfully assigned payment-service to node-1\n"
            )
        elif scenario == "ImagePullBackOff":
            stdout = (
                "LAST SEEN   TYPE      REASON      OBJECT                                 MESSAGE\n"
                "1m ago      Warning   Failed      pod/auth-service-7bbcd459d8-kp810      Failed to pull image \"internal-registry.io/auth-service:v2.0.1-prod\": rpc error: code = NotFound desc = failed to pull and unpack image\n"
                "1m ago      Warning   Inspect     pod/auth-service-7bbcd459d8-kp810      Error: ErrImagePull\n"
                "4m ago      Normal    Scheduled   pod/auth-service-7bbcd459d8-kp810      Successfully assigned auth-service to node-2\n"
            )
        elif scenario == "OOMKilled":
            stdout = (
                "LAST SEEN   TYPE      REASON      OBJECT                                 MESSAGE\n"
                "30s ago     Warning   BackOff     pod/report-generator-d86bfcd8-89qws    Back-off restarting failed container\n"
                "1m ago      Warning   OOMKilled   pod/report-generator-d86bfcd8-89qws    System OOM killer triggered - Container report-generator process killed\n"
            )
        elif scenario == "SelectorMismatch":
            stdout = (
                "LAST SEEN   TYPE      REASON             OBJECT                                            MESSAGE\n"
                "2m ago      Warning   FailedScheduling   pod/notification-processor-b7d8d-xpl8             no nodes available matching selector\n"
            )
        else:
            stdout = "No events found in default namespace."
        return {"success": True, "stdout": stdout, "stderr": "", "returncode": 0}

    def _sim_describe_deployment(self, scenario: str, dep_name: str) -> Dict[str, Any]:
        if scenario == "CrashLoopBackOff":
            stdout = (
                f"Name:                   payment-service\n"
                f"Namespace:              default\n"
                f"Replicas:               1 desired | 1 updated | 1 total | 0 available | 1 unavailable\n"
                f"Conditions:\n"
                f"  Type           Status  Reason\n"
                f"  ----           ------  ------\n"
                f"  Available      False   MinimumReplicasUnavailable\n"
                f"  Progressing    True    ReplicaSetUpdated\n"
            )
        elif scenario == "ImagePullBackOff":
            stdout = (
                f"Name:                   auth-service\n"
                f"Namespace:              default\n"
                f"Replicas:               1 desired | 1 updated | 1 total | 0 available | 1 unavailable\n"
                f"Conditions:\n"
                f"  Type           Status  Reason\n"
                f"  ----           ------  ------\n"
                f"  Available      False   MinimumReplicasUnavailable\n"
                f"  Progressing    False   ProgressDeadlineExceeded\n"
            )
        elif scenario == "OOMKilled":
            stdout = (
                f"Name:                   report-generator\n"
                f"Namespace:              default\n"
                f"Replicas:               1 desired | 1 updated | 1 total | 0 available | 1 unavailable\n"
                f"Conditions:\n"
                f"  Type           Status  Reason\n"
                f"  ----           ------  ------\n"
                f"  Available      False   MinimumReplicasUnavailable\n"
            )
        elif scenario == "SelectorMismatch":
            stdout = (
                f"Name:                   notification-service\n"
                f"Namespace:              default\n"
                f"Replicas:               2 desired | 2 updated | 2 total | 2 available | 0 unavailable\n"
                f"Selector:               app=notification-app\n" # deployment selector
                f"Template:\n"
                f"  Labels:               app=notification-service\n" # actual pod label (mismatching)
            )
        else:
            stdout = f"Deployment {dep_name} status: healthy."
        return {"success": True, "stdout": stdout, "stderr": "", "returncode": 0}

    def _sim_get_deployments(self, scenario: str) -> Dict[str, Any]:
        if scenario == "CrashLoopBackOff":
            stdout = (
                "NAME              READY   UP-TO-DATE   AVAILABLE   AGE\n"
                "payment-service   0/1     1            0           15m\n"
                "frontend          1/1     1            1           4h\n"
            )
        elif scenario == "ImagePullBackOff":
            stdout = (
                "NAME              READY   UP-TO-DATE   AVAILABLE   AGE\n"
                "auth-service      0/1     1            0           4m\n"
                "frontend          1/1     1            1           4h\n"
            )
        elif scenario == "OOMKilled":
            stdout = (
                "NAME               READY   UP-TO-DATE   AVAILABLE   AGE\n"
                "report-generator   0/1     1            0           8m\n"
                "frontend           1/1     1            1           4h\n"
            )
        elif scenario == "SelectorMismatch":
            stdout = (
                "NAME                   READY   UP-TO-DATE   AVAILABLE   AGE\n"
                "notification-service   2/2     2            2           6m\n"
                "frontend               1/1     1            1           4h\n"
            )
        else:
            stdout = (
                "NAME              READY   UP-TO-DATE   AVAILABLE   AGE\n"
                "frontend          1/1     1            1           4h\n"
                "payment-service   1/1     1            1           4h\n"
            )
        return {"success": True, "stdout": stdout, "stderr": "", "returncode": 0}

    def _sim_get_services(self, scenario: str) -> Dict[str, Any]:
        if scenario == "SelectorMismatch":
            stdout = (
                "NAME                   TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE\n"
                "notification-service   ClusterIP   10.96.140.231   <none>        8080/TCP   6m\n"
                "frontend               ClusterIP   10.96.220.10    <none>        80/TCP     4h\n"
            )
        else:
            stdout = (
                "NAME              TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE\n"
                "frontend          ClusterIP   10.96.220.10    <none>        80/TCP     4h\n"
                "payment-service   ClusterIP   10.96.155.84    <none>        8080/TCP   4h\n"
            )
        return {"success": True, "stdout": stdout, "stderr": "", "returncode": 0}

    def _sim_get_endpoints(self, scenario: str) -> Dict[str, Any]:
        if scenario == "SelectorMismatch":
            # No endpoints because of selector label mismatch!
            stdout = (
                "NAME                   ENDPOINTS   AGE\n"
                "notification-service   <none>      6m\n"
                "frontend               10.244.0.5  4h\n"
            )
        else:
            stdout = (
                "NAME              ENDPOINTS         AGE\n"
                "frontend          10.244.0.5:80     4h\n"
                "payment-service   10.244.0.12:8080  4h\n"
            )
        return {"success": True, "stdout": stdout, "stderr": "", "returncode": 0}
