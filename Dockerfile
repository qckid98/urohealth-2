# 1. Gunakan Python versi stabil (Linux Debian)
FROM python:3.10-slim

# 2. Install Library Sistem yang WAJIB untuk WeasyPrint (Pango, Cairo, GObject)
# Kita install manual agar tidak ada yang kurang
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-cffi \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-dejavu \
    fonts-liberation \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 3. Setup Folder Kerja
WORKDIR /app

# 4. Copy file requirements dan install library Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy seluruh kode aplikasi ke dalam container
COPY . .

# 6. Jalankan aplikasi menggunakan Gunicorn
# Railway otomatis memberikan PORT, kita bind ke 0.0.0.0
CMD gunicorn app:app --bind 0.0.0.0:$PORT