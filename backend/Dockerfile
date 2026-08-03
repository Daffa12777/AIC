FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ /app/
COPY ml-engine/ /ml-engine/
ENV PYTHONPATH=/ml-engine:/app
ENV DATABASE_URL=postgresql://alumisight:alumisight@db:5432/alumisight
ENV UPLOAD_DIR=/app/storage
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
