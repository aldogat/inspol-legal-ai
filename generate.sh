#!/bin/bash
set -e

echo "🏗️  Generando INSPOL LEGAL AI - Plataforma Jurídica Inteligente"

# Crear estructura de directorios
mkdir -p {apps,frontend,backend,packages,docker,docs,scripts}
mkdir -p backend/{app/{api/{v1},core,models,schemas,services},tests,alembic}
mkdir -p frontend/{app/{"(dashboard)"/{cases,documents,chat,clients,analytics,admin},components/{ui,dashboard,documents,chat,layout},lib,hooks,providers,styles},public}
mkdir -p docker/{backend,frontend,postgres}
mkdir -p packages/{shared,ui,config}
mkdir -p docs/{api,architecture,deployment}

# .env
cat > .env << 'EOF'
DATABASE_URL=postgresql://inspol:inspol_pass@postgres:5432/inspol_db
REDIS_URL=redis://redis:6379/0
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=inspol-documents
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4-turbo
WEAVIATE_URL=http://weaviate:8080
JWT_SECRET=inspol-jwt-secret-change-in-production
JWT_ALGORITHM=HS256
APP_ENV=development
API_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
EOF

# docker-compose.yml (usando docker compose v2)
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: inspol
      POSTGRES_PASSWORD: inspol_pass
      POSTGRES_DB: inspol_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes:
      - minio_data:/data
    ports:
      - "9000:9000"
      - "9001:9001"
  weaviate:
    image: semitechnologies/weaviate:1.25.1
    environment:
      AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'true'
      PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
      DEFAULT_VECTORIZER_MODULE: 'none'
    volumes:
      - weaviate_data:/var/lib/weaviate
    ports:
      - "8080:8080"
  backend:
    build:
      context: ./backend
      dockerfile: ../docker/backend/Dockerfile
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - postgres
      - redis
      - minio
      - weaviate
  celery:
    build:
      context: ./backend
      dockerfile: ../docker/backend/Dockerfile
    command: celery -A app.core.celery_app worker --loglevel=info
    volumes:
      - ./backend:/app
    env_file: .env
    depends_on:
      - backend
  frontend:
    build:
      context: ./frontend
      dockerfile: ../docker/frontend/Dockerfile
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend
volumes:
  postgres_data:
  minio_data:
  weaviate_data:
EOF

# Dockerfiles
mkdir -p docker/backend docker/frontend
cat > docker/backend/Dockerfile << 'EOF'
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

cat > docker/frontend/Dockerfile << 'EOF'
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]
EOF

# Backend requirements
cat > backend/requirements.txt << 'EOF'
fastapi>=0.115.0
uvicorn[standard]
sqlalchemy[asyncio]>=2.0
asyncpg
python-jose[cryptography]
passlib[bcrypt]
python-multipart
boto3
openai
weaviate-client
celery[redis]
pydantic-settings
Pillow
pypdf
python-docx
langchain
langchain-openai
httpx
redis
EOF

# Backend app main
touch backend/app/__init__.py
mkdir -p backend/app/core backend/app/models backend/app/services backend/app/api/v1

cat > backend/app/main.py << 'PYEOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, ai, chat

app = FastAPI(title="INSPOL LEGAL AI", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["ai"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
PYEOF

cat > backend/app/core/config.py << 'PYEOF'
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV: str = "development"
    DATABASE_URL: str
    REDIS_URL: str
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET: str
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4-turbo"
    WEAVIATE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    class Config:
        env_file = ".env"
settings = Settings()
PYEOF

cat > backend/app/core/security.py << 'PYEOF'
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def create_access_token(data: dict, expires: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires or timedelta(hours=24))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
def decode_token(token: str):
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None
PYEOF

cat > backend/app/api/v1/auth.py << 'PYEOF'
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from app.core.security import create_access_token
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

@router.post("/login")
async def login(username: str, password: str):
    # demo: cualquier login funciona
    token = create_access_token({"sub": "demo", "email": username})
    return {"access_token": token, "token_type": "bearer"}
PYEOF

cat > backend/app/api/v1/ai.py << 'PYEOF'
from fastapi import APIRouter, Depends, File, UploadFile
from openai import AsyncOpenAI
from app.core.config import settings
router = APIRouter()
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

@router.post("/analyze-contract")
async def analyze_contract(text: str):
    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[{"role": "system", "content": "Analiza este contrato y devuelve un JSON con risk_score, traffic_light, riesgos y sugerencias."},
                  {"role": "user", "content": text}],
        response_format={"type": "json_object"}
    )
    import json
    return json.loads(response.choices[0].message.content)
PYEOF

cat > backend/app/api/v1/chat.py << 'PYEOF'
from fastapi import APIRouter
router = APIRouter()

@router.post("/message")
async def chat(message: str):
    return {"response": f"Respuesta demo para: {message}"}
PYEOF

# Frontend básico
cat > frontend/package.json << 'EOF'
{
  "name": "inspol-frontend",
  "version": "1.0.0",
  "scripts": { "dev": "next dev", "build": "next build", "start": "next start" },
  "dependencies": {
    "next": "15.0.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "next-themes": "^0.3.0",
    "lucide-react": "^0.441.0",
    "framer-motion": "^11.0.0"
  },
  "devDependencies": {
    "typescript": "^5",
    "@types/react": "^18",
    "tailwindcss": "^3.4.10",
    "autoprefixer": "^10.4.20",
    "postcss": "^8.4.41"
  }
}
EOF

cat > frontend/tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{"name": "next"}],
    "paths": {"@/*": ["./*"]}
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}
EOF

cat > frontend/next.config.js << 'EOF'
/** @type {import('next').NextConfig} */
module.exports = { env: { NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000' } }
EOF

cat > frontend/tailwind.config.ts << 'EOF'
import type { Config } from "tailwindcss"
const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: { extend: {} },
  plugins: [],
}
export default config
EOF

cat > frontend/postcss.config.js << 'EOF'
module.exports = { plugins: { tailwindcss: {}, autoprefixer: {} } }
EOF

cat > frontend/app/globals.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;
body { font-family: system-ui, sans-serif; }
EOF

cat > frontend/app/layout.tsx << 'EOF'
import "./globals.css"
import { ThemeProvider } from "@/providers/theme-provider"
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" suppressHydrationWarning>
      <body><ThemeProvider attribute="class" defaultTheme="system" enableSystem>{children}</ThemeProvider></body>
    </html>
  )
}
EOF

mkdir -p frontend/providers
cat > frontend/providers/theme-provider.tsx << 'EOF'
"use client"
import { ThemeProvider as NextThemesProvider } from "next-themes"
import { type ThemeProviderProps } from "next-themes/dist/types"
export function ThemeProvider({ children, ...props }: ThemeProviderProps) { return <NextThemesProvider {...props}>{children}</NextThemesProvider> }
EOF

mkdir -p "frontend/app/(dashboard)"
cat > 'frontend/app/(dashboard)/layout.tsx' << 'EOF'
"use client"
import Link from "next/link"
import { Home, MessageCircle, Scale, Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { theme, setTheme } = useTheme()
  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      <aside className="w-64 bg-white dark:bg-gray-800 border-r p-4 flex flex-col gap-4">
        <Link href="/" className="flex items-center gap-2 text-primary"><Scale size={28} /><span className="font-bold text-xl">INSPOL</span></Link>
        <nav className="flex flex-col gap-2">
          <Link href="/" className="flex items-center gap-2 p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700"><Home size={18} /> Dashboard</Link>
          <Link href="/chat" className="flex items-center gap-2 p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700"><MessageCircle size={18} /> Chat IA</Link>
        </nav>
        <button onClick={() => setTheme(theme==="dark"?"light":"dark")} className="mt-auto p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700">
          {theme==="dark" ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </aside>
      <main className="flex-1 p-6 overflow-auto">{children}</main>
    </div>
  )
}
EOF

cat > 'frontend/app/(dashboard)/page.tsx' << 'EOF'
export default function Dashboard() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Buenos días, Carlos</h1>
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow"><p className="text-gray-500">Casos activos</p><p className="text-3xl font-bold">24</p></div>
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow"><p className="text-gray-500">Documentos</p><p className="text-3xl font-bold">12</p></div>
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow"><p className="text-gray-500">Vencimientos</p><p className="text-3xl font-bold">3</p></div>
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow"><p className="text-gray-500">Horas ahorradas</p><p className="text-3xl font-bold">89</p></div>
      </div>
    </div>
  )
}
EOF

cat > 'frontend/app/(dashboard)/chat/page.tsx' << 'EOF'
"use client"
import { useState } from "react"

export default function ChatPage() {
  const [messages, setMessages] = useState([{role:"assistant",content:"Hola, soy tu copiloto jurídico. ¿En qué puedo ayudarte?"}])
  const [input, setInput] = useState("")
  const handleSend = async () => {
    if (!input.trim()) return
    setMessages([...messages, {role:"user",content:input}])
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/chat/message`, {
        method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({message:input})
      })
      const data = await res.json()
      setMessages(prev => [...prev, {role:"assistant",content:data.response}])
    } catch(e) {
      setMessages(prev => [...prev, {role:"assistant",content:"Error de conexión"}])
    }
    setInput("")
  }
  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] bg-white dark:bg-gray-800 rounded-xl shadow overflow-hidden">
      <div className="flex-1 p-4 overflow-auto space-y-4">
        {messages.map((m,i)=>(
          <div key={i} className={`p-3 rounded-lg max-w-[70%] ${m.role==="user"?"bg-primary text-white ml-auto":"bg-gray-100 dark:bg-gray-700"}`}>{m.content}</div>
        ))}
      </div>
      <form onSubmit={e=>{e.preventDefault();handleSend()}} className="p-4 border-t flex gap-2">
        <input value={input} onChange={e=>setInput(e.target.value)} placeholder="Pregunta sobre tus contratos..." className="flex-1 p-2 border rounded-lg dark:bg-gray-700"/>
        <button type="submit" className="px-4 py-2 bg-primary text-white rounded-lg">Enviar</button>
      </form>
    </div>
  )
}
EOF

echo ""
echo "✅ INSPOL LEGAL AI generado exitosamente"
echo "Edita .env con tu OPENAI_API_KEY y ejecuta: docker compose up --build"
