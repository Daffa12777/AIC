FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Tentukan direktori kerja di dalam container
WORKDIR /app

# Copy file requirements terlebih dahulu untuk caching
COPY requirements.txt .

# Install semua library Python
RUN pip install --no-cache-dir -r requirements.txt

# =================================================================
# BAGIAN HUGGING FACE (Download otomatis saat build)
# =================================================================
# Buat folder models
RUN mkdir -p /app/models

# Download model dari Hugging Face 
RUN wget -O /app/models/unsloth.Q4_K_M.gguf "https://huggingface.co/erlangram/qwen2.5_finetune_alumisight/resolve/main/unsloth.Q4_K_M.gguf?download=true"
# =================================================================

# Copy seluruh file proyek ke dalam container
COPY . .

# Beri tahu Docker bahwa aplikasi ini berjalan di port 8000
EXPOSE 8000

# Perintah untuk menyalakan server FastAPI saat container dijalankan
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]