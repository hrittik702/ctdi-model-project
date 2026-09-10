# 🚀 Running the CTDI Python Backend

> [!INFO] Service Overview
> - **Framework**: FastAPI + Uvicorn
> - **Entrypoint**: `api.py`
> - **Default Port**: `8000`
> - **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### 1. Activate Environment & Start Server

> [!TIP] Linux / macOS
> ```bash
> # Navigate to project directory
> cd /home/mocha/Desktop/ctdi-model-project
> 
> # Activate virtual environment (if needed)
> source .venv/bin/activate
> 
> # Run FastAPI server with auto-reload
> uvicorn api:app --host 127.0.0.1 --port 8000 --reload
> ```

> [!TIP] Windows (PowerShell)
> ```powershell
> cd ctdi-model-project
> .venv\Scripts\Activate.ps1
> uvicorn api:app --host 127.0.0.1 --port 8000 --reload
> ```

---

### 2. Live API Docs inside Obsidian

You can embed the interactive Swagger documentation directly inside this Obsidian note:

<iframe 
  src="http://127.0.0.1:8000/docs" 
  width="100%" 
  height="700px" 
  style="border-radius: 8px; border: 1px solid var(--background-modifier-border);">
</iframe>