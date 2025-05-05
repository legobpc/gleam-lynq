FROM node:20

WORKDIR /app

# Копіюємо тільки package*.json для кешування шарів при npm install
COPY package*.json ./

# Встановлюємо залежності
RUN npm install

# Копіюємо весь код
COPY . .

# Відкриваємо порт для Vite
EXPOSE 5173

# Стандартна команда для запуску Vite dev server
CMD ["npm", "run", "dev", "--", "--host"]