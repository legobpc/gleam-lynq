FROM python:3.11

# ---------------------------------------------------------------------------------
# Встановлюємо всі необхідні системні залежності для роботи Google Chrome
# (headless режим):
#
# - wget, curl, gnupg: для завантаження та обробки ключів і файлів
# - fonts-liberation та інші бібліотеки: ключові залежності для стабільної роботи
#   headless Chrome у середовищах без GUI (наприклад, у Docker-контейнері)
#
# Ми більше НЕ використовуємо apt для встановлення google-chrome-stable, бо він
# завжди ставить найновішу версію ➔ це ламає сумісність із драйвером.
#
# Натомість одразу завантажуємо конкретну версію Chrome (CfT) далі.
# ---------------------------------------------------------------------------------
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    unzip \
    xvfb \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxkbcommon0 \
    libxshmfence1 \
    libgbm1 \
    libpangocairo-1.0-0 \
    libx11-xcb-dev \
    xdg-utils

# ---------------------------------------------------------------------------------
# Встановлюємо Google Chrome (CfT) конкретної версії 124.0.6367.119:
#
# - Завантажуємо архів Chrome for Testing
# - Розпаковуємо його у /opt/chrome
# - Створюємо симлінк у /usr/bin/google-chrome для сумісності з Selenium
#
# Це забезпечує повний контроль над версією Chrome і уникає оновлень з apt.
# ---------------------------------------------------------------------------------
RUN wget -O /tmp/chrome-linux64.zip https://storage.googleapis.com/chrome-for-testing-public/124.0.6367.119/linux64/chrome-linux64.zip \
    && unzip /tmp/chrome-linux64.zip \
    && mv chrome-linux64 /opt/chrome \
    && ln -s /opt/chrome/chrome /usr/bin/google-chrome \
    && rm -rf /tmp/chrome-linux64.zip

# ---------------------------------------------------------------------------------
# Встановлюємо ChromeDriver, який відповідає версії Chrome (124.0.6367.119)
#
# ❗️ Це гарантує ідеальну сумісність браузера і драйвера, щоб уникнути помилок
# типу "SessionNotCreatedException".
# ---------------------------------------------------------------------------------
RUN wget -O /tmp/chromedriver-linux64.zip https://storage.googleapis.com/chrome-for-testing-public/124.0.6367.119/linux64/chromedriver-linux64.zip \
    && unzip /tmp/chromedriver-linux64.zip \
    && mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf chromedriver-linux64 /tmp/chromedriver-linux64.zip

# ---------------------------------------------------------------------------------
# Встановлюємо робочий каталог у контейнері (/code)
# Копіюємо код програми та файл requirements.txt (список Python-залежностей)
# ---------------------------------------------------------------------------------
WORKDIR /code

# Копіюємо тільки requirements.txt щоб використати кеш
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Потім код
COPY . /code

# ---------------------------------------------------------------------------------
# Стартова команда для запуску FastAPI сервера через Uvicorn
# ---------------------------------------------------------------------------------
CMD xvfb-run --server-args="-screen 0 1920x1080x24" uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
