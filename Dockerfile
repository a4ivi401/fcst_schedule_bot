FROM python:3.10-slim

# Встановлюємо OpenVPN
RUN apt-get update && \
    apt-get install -y openvpn curl && \
    rm -rf /var/lib/apt/lists/*

# Копіюємо всі файли проекту
COPY . /app
WORKDIR /app

# Встановлюємо Python-залежності
RUN pip install -r requirements.txt

# Копіюємо .ovpn файл у контейнер
COPY vpn-config.ovpn /etc/openvpn/config.ovpn

# Створюємо скрипт для запуску VPN + бота
RUN echo '#!/bin/bash\n\
openvpn --config /etc/openvpn/config.ovpn --daemon && \
sleep 5 && \
python main.py' > /app/start.sh && \
chmod +x /app/start.sh

# Запускаємо бота
CMD ["/app/start.sh"]