# Use smaller Python base
FROM python:3.9-slim

WORKDIR /app

# Copy only requirements first (better caching)
COPY backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy only backend code (NOT whole repo)
COPY backend ./backend

# Set Python path
ENV PYTHONPATH=/app

EXPOSE 7860

CMD ["uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "8000"]