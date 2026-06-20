# AI Kubernetes Troubleshooting Agent 🚀

An on-demand, full-stack **AI-powered Kubernetes Troubleshooting & Diagnostics** agent. It acts as an automated junior DevOps engineer to extract evidence from your clusters (pods, logs, events, deployments, networking) and passes the data to a Senior SRE reasoning agent (via Gemini on OpenRouter) to identify root causes and recommend actionable fixes.

---

## 🛠️ Architecture

```text
               +-------------------------------------------------------+
               |                  Next.js Frontend                     |
               |       (Auth, Live SSE Stream, History Logs)           |
               +-------------------------------------------------------+
                                           │
                        API Calls & SSE    │
                        Progress Streams   ▼
               +-------------------------------------------------------+
               |                 FastAPI Orchestrator                  |
               |              (Backend API router & SSE)               |
               +-------------------------------------------------------+
                                           │
                                           ├──────────────────────────┐
                                           ▼                          ▼
               +----------------------------------------+   +-------------------+
               |      Kubernetes Investigation Layer     |   |  AI SRE Agent     |
               | (Subprocess executor & structured runs)|   |  (Prompt Builder  |
               +----------------------------------------+   |  & LLM Client)    |
                                           │                +-------------------+
             Executes                      │                          │
             Kubectl commands              ▼                          ▼
                              +─────────────────────────+   +───────────────────+
                              |   Kubernetes Cluster    |   |    OpenRouter     |
                              |   (Real / Simulated)    |   |    (LLM API)      |
                              +─────────────────────────+   +───────────────────+
```

---

## 📁 Project Structure

```text
ai-kubernetes-agent/
├── backend/
│   ├── app/
│   │   ├── api/             # API Router definitions
│   │   ├── core/            # Configuration & logger initialization
│   │   ├── kubernetes/      # Subprocess command executor & resource inspectors
│   │   ├── ai/              # Prompt compiling & OpenRouter client
│   │   ├── services/        # Investigation orchestration service
│   │   ├── models/          # Pydantic schema validation
│   │   └── main.py          # FastAPI application entrypoint
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile           # Backend container
│
├── frontend/
│   ├── src/
│   │   ├── app/             # App Router pages (Page, Dashboard)
│   │   ├── components/      # UI components (Header, selectors, diagnosis card)
│   │   ├── services/        # InsForge wrapper & API communication
│   │   ├── hooks/           # useInvestigation SSE hook
│   │   └── types/           # Unified TypeScript definitions
│   ├── package.json         # Node.js dependencies
│   └── Dockerfile           # Frontend container
│
├── docker-compose.yml       # Orchestrates both services locally
└── README.md                # Documentation
```

---

## 🚀 Getting Started

### Option A: Using Docker Compose (Recommended)

1. Create a `.env` file in the root directory:
   ```env
   OPENROUTER_API_KEY=your_openrouter_api_key
   OPENROUTER_MODEL=google/gemini-2.5-flash
   SIMULATION_MODE=true
   ```
2. Build and start the containers:
   ```bash
   docker compose up --build
   ```
3. Access:
   * **Frontend Dashboard**: `http://localhost:3000`
   * **Backend Health Check**: `http://localhost:8000/health`

---

### Option B: Running Locally

#### 1. Start the Backend
1. Navigate to the `backend` folder:
   ```bash
   cd backend
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the development server:
   ```bash
   python app/main.py
   ```

#### 2. Start the Frontend
1. Open a new terminal and navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```
2. Install Node packages:
   ```bash
   npm install
   ```
3. Run the Next.js development server:
   ```bash
   npm run dev
   ```

---

## 🧪 Simulation Scenarios

The system includes a **Simulation Mode** (enabled automatically if `kubectl` is missing or when a `simulation-` context is selected). It allows testing the full pipeline offline:

1. **`CrashLoopBackOff`**: Application container crashes due to a missing `DATABASE_URL` environment variable.
2. **`ImagePullBackOff`**: Kubernetes fails to pull the container image because of an invalid image tag.
3. **`OOMKilled`**: Container exceeds its memory limit (low limit 64Mi vs. high load).
4. **`SelectorMismatch`**: No endpoints are matched for a Service due to mismatching selector labels.

---

## 🚀 Deployment Guide

### Part 1: GitHub Repository Setup

1. **Initialize Git** in the project root:
   ```bash
   git init
   ```
2. **Stage and commit** the code:
   ```bash
   git add .
   git commit -m "feat: initial commit AI Kubernetes agent foundation"
   ```
3. **Push to GitHub**:
   * Create a new repository on GitHub.
   * Connect your local repo and push:
     ```bash
     git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
     git branch -M main
     git push -u origin main
     ```

---

### Part 2: Deploying to Vercel (Frontend)

Next.js is deployed directly to **Vercel** for hosting.

1. **Host the Backend**:
   * Deploy the Python FastAPI backend to a platform like **Railway**, **Render**, or **Fly.io** (or deploy via Docker to your cloud server).
   * Note the deployed public backend URL (e.g. `https://your-backend.railway.app`).
2. **Vercel Import**:
   * Go to [Vercel](https://vercel.com) and click **Add New Project**.
   * Import your GitHub repository.
3. **Project Settings**:
   * Set **Root Directory** to `frontend`.
   * Add the following **Environment Variables**:
     * `NEXT_PUBLIC_API_BASE_URL` = `https://your-backend.railway.app`
     * `NEXT_PUBLIC_INSFORGE_URL` = `(Your InsForge Client Endpoint)`
     * `NEXT_PUBLIC_INSFORGE_ANON_KEY` = `(Your InsForge Anon Token)`
4. Click **Deploy**. Vercel will build the frontend and serve it globally!
