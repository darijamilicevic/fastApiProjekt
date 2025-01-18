FROM python:3.10-slim

# 1) Postavi radni direktorij
WORKDIR /app

# 2) Kopiraj requirements i instaliraj
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) Kopiraj ostatak koda
COPY app/ /app

# 4) Expose port 5000 (FastAPI)
EXPOSE 5000

# 5) Definiraj startnu točku (pokretanje uvicorna)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]