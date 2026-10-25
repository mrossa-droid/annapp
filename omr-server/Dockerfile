# AnnApp sheet-music reader (homr). Needs about 1.5 GB RAM.
FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*
WORKDIR /srv
RUN pip install --no-cache-dir "homr[cpu]==0.7.0" "fastapi>=0.110" "uvicorn>=0.29" "python-multipart>=0.0.9"
# download the recognition models into the image
RUN python -m homr.main --init
COPY app.py /srv/app.py
ENV PORT=10000
EXPOSE 10000
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT}"]
