# Procfile for Railway deployment
# The backend is the main service, running on port 8000
web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
# The frontend can be a separate service or built statically, but for simplicity, we'll focus on the backend for now.
# If the user wants to deploy the frontend as well, we'll need a separate service or a multi-stage build.
# For now, we'll assume the user wants the backend API deployed.
