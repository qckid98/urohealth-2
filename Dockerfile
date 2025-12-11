# 1. GUNAKAN VERSI BOOKWORM (STABIL)
# Jangan pakai 'slim' saja, karena bisa nyasar ke versi Trixie/Unstable
FROM python:3.10-slim-bookworm

# 2. Install Library Sistem (WeasyPrint Dependencies)
# Di Debian Bookworm, nama-nama paket ini DIJAMIN ada
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
RUN mkdir -p instance

# 4. Copy requirements dan install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy kode aplikasi
COPY . .

# 6. Jalankan Gunicorn
CMD gunicorn app:app --bind 0.0.0.0:5000