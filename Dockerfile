FROM python:3.11-slim

WORKDIR /app

# Install uv for fast dependency resolution
RUN pip install --no-cache-dir uv

# Install deps with uv (10-100x faster than pip)
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

# Copy only source code
COPY src/ ./src/
COPY openenv.yaml .
COPY inference.py .

EXPOSE 7860

CMD ["uvicorn", "src.environment.server:app", "--host", "0.0.0.0", "--port", "7860"]
