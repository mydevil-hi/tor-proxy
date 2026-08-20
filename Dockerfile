FROM python:3.10-slim

# تثبيت Tor و obfs4proxy
RUN apt-get update && apt-get install -y \
    tor \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/*

# إعداد ملف تشغيل Tor
RUN echo "SocksPort 0.0.0.0:9050" >> /etc/tor/torrc && \
    echo "ExitRelays 0" >> /etc/tor/torrc

WORKDIR /app

# تثبيت مكتبات بايثون
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# تصريح تشغيل السكربت
RUN chmod +x start.sh

EXPOSE 8080

CMD ["./start.sh"]
