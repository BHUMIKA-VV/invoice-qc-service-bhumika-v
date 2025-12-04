FROM python:3.11-slim

# set working directory
WORKDIR /app

# install system dependencies (for PDFs, etc. if needed later)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# copy requirements
COPY requirements.txt .

# install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy backend files
COPY invoice_qc/ ./invoice_qc/
COPY api.py ./api.py

# (Optional) copy frontend folder (not required for backend-only service)
# COPY src/ ./src/

# expose port Render expects
EXPOSE 8000

# start FastAPI app
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
