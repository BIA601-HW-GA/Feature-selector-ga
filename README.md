# Feature-selector-ga

Professional README — Feature selection web app using Genetic Algorithms

Overview

Feature-selector-ga is a full-stack research and demonstration application that runs genetic-algorithm-based feature selection on tabular datasets, compares the selected features with several established methods, and visualizes results in a web dashboard. It was developed for the BIA601 (Intelligent Algorithms) course and is suitable as a reproducible experiment and a lightweight demo.

Key capabilities

- Upload a CSV dataset to run analysis (the frontend accepts `multipart/form-data`).
- Run an optimized Genetic Algorithm (threaded evaluation by default) to select informative features.
- Compare GA-selected features to: SelectKBest, LassoCV, RFE, VarianceThreshold, Mutual Information, RandomForest-based selection.
- Generate and serve plots (GA progress, comparison metrics, Jaccard overlap, timing, selected counts).
- Frontend built with static HTML + Tailwind CSS; backend uses FastAPI.

Repository structure

- `backend/`
  - `main.py` — FastAPI app entrypoint; mounts frontend and outputs static dirs
  - `config.py` — project paths, logging and basic configuration
  - `api/` — FastAPI routers
    - `feature_selection.py` — endpoint that runs GA, comparisons and saves plots
    - `data_management.py` — upload/list/delete datasets
    - `health.py` — simple health endpoint

- `frontend/`
  - `upload.html` — upload form and GA parameter UI
  - `results.html` — results page (reads last result from localStorage)
  - `analysis.html` — detailed analysis page
  - `assets/` — `script.js` and `style.css`

- `utils/`
  - `data.py` — dataset preparation helpers
  - `comparison.py` — functions to run comparison methods
  - `ga_optimized.py` — optimized GA implementation (threaded eval by default)
  - `ga_original.py` — reference/original GA implementation
  - `plotting.py` — functions that create and save matplotlib plots

- `outputs/` — generated plots and result artifacts (created at runtime)
- `uploads/` — uploaded CSVs (created at runtime)
- `requirements.txt` — Python dependencies
- `Dockerfile` — image spec for containerized runs

Quick start — local (development)

1) Create and activate a virtual environment (Windows PowerShell):

```powershell
python -m venv .venv
# Feature-selector-ga

Professional README — Feature selection web app using Genetic Algorithms

Live demo

The application is deployed and available at: https://genetic-algorithm-production-3ee1.up.railway.app/

Overview

Feature-selector-ga is a full-stack research and demonstration application that runs genetic-algorithm-based feature selection on tabular datasets, compares the selected features with several established methods, and visualizes results in a web dashboard. It was developed for the BIA601 (Intelligent Algorithms) course and is suitable as a reproducible experiment and a lightweight demo.

Key capabilities

- Upload a CSV dataset to run analysis (the frontend accepts `multipart/form-data`).
- Run an optimized Genetic Algorithm (threaded evaluation by default) to select informative features.
- Compare GA-selected features to: SelectKBest, LassoCV, RFE, VarianceThreshold, Mutual Information, RandomForest-based selection.
- Generate and serve plots (GA progress, comparison metrics, Jaccard overlap, timing, selected counts).
- Frontend built with static HTML + Tailwind CSS; backend uses FastAPI.

Repository structure

- `backend/`
  - `main.py` — FastAPI app entrypoint; mounts frontend and outputs static dirs
  - `config.py` — project paths, logging and basic configuration
  - `api/` — FastAPI routers
    - `feature_selection.py` — endpoint that runs GA, comparisons and saves plots
    - `data_management.py` — upload/list/delete datasets
    - `health.py` — simple health endpoint

- `frontend/`
  - `upload.html` — upload form and GA parameter UI
  - `results.html` — results page (reads last result from localStorage)
  - `analysis.html` — detailed analysis page
  - `assets/` — `script.js` and `style.css`

- `utils/`
  - `data.py` — dataset preparation helpers
  - `comparison.py` — functions to run comparison methods
  - `ga_optimized.py` — optimized GA implementation (threaded eval by default)
  - `ga_original.py` — reference/original GA implementation
  - `plotting.py` — functions that create and save matplotlib plots

- `outputs/` — generated plots and result artifacts (created at runtime)
- `uploads/` — uploaded CSVs (created at runtime)
- `requirements.txt` — Python dependencies
- `Dockerfile` — image spec for containerized runs

Quick start — local (development)

1) Create and activate a virtual environment (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2) Start the server locally:

```powershell
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

3) Open the app in your browser:

- Upload page: `http://127.0.0.1:8000/upload.html`

Running in Docker

Build and run (requires enough host memory for building some dependencies):

```powershell
docker build -t ga-feature-selection .
docker run -p 8000:8000 ga-feature-selection
```

Visit `http://localhost:8000`.

If you see `Error loading ASGI app. Could not import module "backend.main"`:

- Ensure `backend/main.py` and `backend/config.py` are present in the repository before building the image.
- Ensure your `Dockerfile` does not reference a non-existent `setup.py`. The supplied `Dockerfile` copies only `requirements.txt` and the repo files.

API reference (key endpoint)

- POST `/api/run`
  - Content type: `multipart/form-data`
  - Parameters (form fields):
    - `file` (file) — CSV file (required)
    - `target_column` (string, optional)
    - `problem_type` (string, default `regression`)
    - `pop_size`, `generations`, `mutation_rate`, `crossover_rate`, `cv`, `model_type`, `ga_version`, `mode`, `methods`
  - Response (JSON): contains `dataset`, `results` (per-method metrics), `plots` (URLs), and `metadata`.

Example `curl` (upload local CSV):

```bash
curl -F "file=@iris.csv" http://localhost:8000/api/run
```

How plotting and static serving work

- The backend saves generated PNGs to `outputs/<dataset>/`.
- `backend.main` mounts `/outputs` as a StaticFiles mount **before** the frontend mount so requests to `/outputs/...` return those files instead of being handled by the frontend static mount.

Implementation notes and important details

- Parallel evaluation: `utils/ga_optimized.py` uses `ThreadPoolExecutor` to avoid pickling errors with nested evaluator functions. If true process-level parallelism is required, refactor the evaluator into a module-level function and pass necessary data explicitly so it can be pickled.
- Temporary files: uploaded CSVs are stored in `uploads/` and removed after processing (check `feature_selection.py`).
- Logging: `backend/config.py` uses `/app/logs/app.log` when running in Docker; for local runs it falls back to `logs/app.log` under the project root.

Troubleshooting (common errors)

- 404s for `/outputs/...` images:
  - Confirm images are present under `outputs/<dataset>/` with exact filenames returned in the API `plots` list.
  - Confirm server is running the same working directory as the repository (Docker builds may copy files into image; check paths).

- `AttributeError: 'str' object has no attribute 'read'` on `/api/run`:
  - Frontend must send `multipart/form-data` with a file input; `upload.html` contains `enctype=\"multipart/form-data\"` and the JS sends a `FormData`.

- `Can't get local object 'run_ga.<locals>.evaluate_individual'`:
  - Occurs when ProcessPoolExecutor tries to pickle a nested function. Use threads (current default) or refactor evaluator to top-level.

- Docker build fails while installing packages (out-of-memory):
  - Increase Docker Desktop memory (>= 4GB) or modify the Dockerfile to avoid heavy system packages.

Deployment on Railway

This project is deployed on Railway. below is a short guide to reproduce the deployment there.

1) Create a Railway project and connect your GitHub repository.

2) In Railway, add environment variables (in Settings → Variables):
   - `PORT` — Railway provides this automatically at runtime (use it in your start command).
   - `MPLCONFIGDIR` — set to `/tmp/matplotlib` to ensure matplotlib can create a writable config directory.

3) Set Railway build & start commands:
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

4) Ensure the repository contains directories that will be created at runtime: `uploads/` and `outputs/`. Railway's ephemeral filesystem will allow temporary storage for generated images, but for durable artifacts you should configure external storage (S3) or use Railway plugins.

5) Adjust Dockerfile / runtime if using Docker on Railway:
   - If you deploy via Docker, ensure the image exposes `8000` and the container runs the same `uvicorn` start command using `$PORT`.

Notes about production on Railway

- Railway assigns a random public domain for the deployment; the demo link is shown at the top of this README.
- The Railway filesystem is ephemeral — files written to `outputs/` will not persist across restarts. For persistent storage, integrate S3 or another external storage provider and update `feature_selection.py` to upload generated plots there.
- Monitor memory & CPU: GA runs can be computationally heavy. Limit `pop_size` and `generations` in production or offload GA runs to background workers.

Development recommendations

- Pin dependency versions in `requirements.txt` for reproducible builds.
- Add `tests/` with a small smoke test that runs the GA on a tiny synthetic dataset (fast). Example test would assert the GA returns a genome, score, and history length > 0.
- If you need multiprocessing performance, refactor `evaluate_individual` into a top-level function and pass a minimal payload to the worker.
- Consider adding explicit environment configuration (e.g., `.env` + python-dotenv) for toggling `parallel` strategy and other runtime settings.







