FROM python:3.11-slim

WORKDIR /app

# Install deps first (cached layer if requirements.txt unchanged)
COPY requirements.txt .
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

# Copy only source code
COPY src/ ./src/
COPY openenv.yaml .
COPY inference.py .

EXPOSE 7860

CMD ["uvicorn", "src.environment.server:app", "--host", "0.0.0.0", "--port", "7860"]
