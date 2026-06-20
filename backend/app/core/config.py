import os
from pathlib import Path
from dotenv import load_dotenv

# Load env variables from backend directory or parent directories
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
load_dotenv()  # fallback to current working directory .env

class Settings:
    PROJECT_NAME: str = "AI Kubernetes Troubleshooting Agent"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    # OpenRouter Config
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash") # fallback model
    OPENROUTER_URL: str = "https://openrouter.ai/api/v1/chat/completions"

    # Kubernetes Config
    KUBECONFIG_PATH: str = os.getenv("KUBECONFIG_PATH", os.path.expanduser("~/.kube/config"))
    
    # Simulation mode fallback if real kubectl isn't available
    SIMULATION_MODE: bool = os.getenv("SIMULATION_MODE", "true").lower() in ("true", "1", "yes")

    # InsForge Auth/Database fallback URL/Keys
    INSFORGE_URL: str = os.getenv("INSFORGE_URL", "")
    INSFORGE_ANON_KEY: str = os.getenv("INSFORGE_ANON_KEY", "")

    # CORS Allowed Origins
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://ai-devops-kubernetes-agent.vercel.app",  # Example Vercel host
    ]

settings = Settings()
