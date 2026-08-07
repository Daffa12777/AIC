FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/models

RUN wget -O /app/models/unsloth.Q4_K_M.gguf "https://huggingface.co/erlangram/qwen2.5_finetune_alumisight/resolve/main/unsloth.Q4_K_M.gguf?download=true"

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]