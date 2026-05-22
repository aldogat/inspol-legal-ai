FROM node:20-alpine

WORKDIR /app

# Copiar package.json
COPY package*.json ./
RUN npm ci

# Copiar el código
COPY . .

# Construir la aplicación
RUN npm run build

# Exponer puerto
EXPOSE 3000

# Comando de inicio
CMD ["npm", "start"]
