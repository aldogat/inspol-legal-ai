#!/usr/bin/env python3
"""Reconstruye la base de datos completa y verifica que todo funcione."""
import asyncio
import sys
from datetime import date, datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

from app.database import engine, AsyncSessionLocal
from app.models.base import Base
from app.models.cliente import Cliente
from app.models.expediente import Expediente
from app.models.contrato import Contrato
from app.models.evento import Evento
from app.models.transaccion import Transaccion
from app.models.documento_legal import DocumentoLegal
from app.models.user import User
from app.models.archivo import ArchivoAdjunto
from app.models.archivo_contrato import ArchivoContrato
from app.models.conversacion import Conversacion
from app.models.historial import HistorialExpediente, HistorialContrato
from app.core.security import get_password_hash
from app.core.embeddings import generar_embedding
from sqlalchemy import select

async def rebuild():
    print("🔧 Paso 1: Creando tablas...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tablas creadas")

    print("🔧 Paso 2: Insertando datos de ejemplo...")
    async with AsyncSessionLocal() as db:
        # Verificar si ya hay datos
        result = await db.execute(select(Cliente))
        if result.scalars().first():
            print("⚠️ Ya existen datos. Borrando...")
            for table in [HistorialContrato, HistorialExpediente, ArchivoContrato, ArchivoAdjunto, 
                         DocumentoLegal, Transaccion, Contrato, Evento, Expediente, Cliente, Conversacion]:
                await db.execute(table.__table__.delete())
            await db.execute(User.__table__.delete())
            await db.commit()
            print("✅ Datos antiguos borrados")

        # Crear admin
        db.add(User(email="admin@inspol.com", hashed_password=get_password_hash("admin123"), nombre="Administrador"))
        
        # 5 Clientes
        db.add_all([
            Cliente(nombre="María García López", email="maria.garcia@email.com", telefono="555-123-4567", rfc="GALM800101", direccion="Av. Reforma 123, CDMX"),
            Cliente(nombre="Corporación Industrial del Norte S.A.", email="contacto@cin.com.mx", telefono="555-987-6543", rfc="CIN910201", direccion="Blvd. Díaz Ordaz 456, Monterrey"),
            Cliente(nombre="Juan Carlos Hernández Ruiz", email="juan.hernandez@email.com", telefono="555-555-1212", rfc="HERJ750512", direccion="Calle 5 de Mayo 78, Guadalajara"),
            Cliente(nombre="Bufete Jurídico López & Asociados S.C.", email="info@lopezasociados.com", telefono="555-321-4321", rfc="LOPA850615", direccion="Paseo de la Reforma 222, CDMX"),
            Cliente(nombre="Inmobiliaria Los Pinos S.A.", email="ventas@lospinos.com.mx", telefono="555-444-3333", rfc="ILP020304", direccion="Av. Universidad 1500, CDMX"),
        ])
        await db.flush()

        hoy = date.today()
        # 8 Expedientes
        db.add_all([
            Expediente(numero_expediente="EXP-2025-001", cliente="María García López", juzgado="Juzgado 1° Civil CDMX", estado="Activo", prioridad="Alta", descripcion="Demanda incumplimiento de contrato", fecha_apertura=hoy - timedelta(days=30)),
            Expediente(numero_expediente="EXP-2025-002", cliente="Corporación Industrial del Norte S.A.", juzgado="Juzgado 3° Mercantil MTY", estado="Activo", prioridad="Media", descripcion="Recisión de contrato", fecha_apertura=hoy - timedelta(days=15)),
            Expediente(numero_expediente="EXP-2025-003", cliente="Juan Carlos Hernández Ruiz", juzgado="Juzgado 2° Civil GDL", estado="Cerrado", prioridad="Baja", descripcion="Divorcio incausado", fecha_apertura=hoy - timedelta(days=60)),
            Expediente(numero_expediente="EXP-2025-004", cliente="Bufete Jurídico López & Asociados S.C.", juzgado="Tribunal Federal Administrativo", estado="Activo", prioridad="Alta", descripcion="Juicio contencioso administrativo", fecha_apertura=hoy - timedelta(days=7)),
            Expediente(numero_expediente="EXP-2025-005", cliente="María García López", juzgado="Juzgado 4° Civil CDMX", estado="Activo", prioridad="Media", descripcion="Cobro de pesos", fecha_apertura=hoy - timedelta(days=22)),
            Expediente(numero_expediente="EXP-2025-006", cliente="Inmobiliaria Los Pinos S.A.", juzgado="Juzgado 1° Civil CDMX", estado="Activo", prioridad="Alta", descripcion="Desalojo por falta de pago", fecha_apertura=hoy - timedelta(days=5)),
            Expediente(numero_expediente="EXP-2025-007", cliente="Corporación Industrial del Norte S.A.", juzgado="Juzgado 2° Mercantil MTY", estado="Cerrado", prioridad="Media", descripcion="Ejecución de garantía", fecha_apertura=hoy - timedelta(days=45)),
            Expediente(numero_expediente="EXP-2025-008", cliente="Juan Carlos Hernández Ruiz", juzgado="Juzgado 1° Laboral GDL", estado="Activo", prioridad="Baja", descripcion="Reinstalación laboral", fecha_apertura=hoy - timedelta(days=12)),
        ])
        await db.flush()

        # 4 Contratos
        db.add_all([
            Contrato(numero_contrato="CTO-2025-001", cliente_id=1, fecha_inicio=hoy - timedelta(days=60), fecha_vencimiento=hoy + timedelta(days=10), estado="Activo", descripcion="Servicios legales"),
            Contrato(numero_contrato="CTO-2025-002", cliente_id=2, fecha_inicio=hoy - timedelta(days=90), fecha_vencimiento=hoy + timedelta(days=2), estado="Activo", descripcion="Suministro materiales"),
            Contrato(numero_contrato="CTO-2025-003", cliente_id=4, fecha_inicio=hoy - timedelta(days=30), fecha_vencimiento=hoy + timedelta(days=25), estado="Activo", descripcion="Consultoría jurídica"),
            Contrato(numero_contrato="CTO-2025-004", cliente_id=5, fecha_inicio=hoy - timedelta(days=120), fecha_vencimiento=hoy - timedelta(days=5), estado="Vencido", descripcion="Arrendamiento oficina"),
        ])
        await db.flush()

        # 3 Eventos
        db.add_all([
            Evento(titulo="Audiencia EXP-2025-001", fecha_inicio=datetime.now() + timedelta(days=2, hours=10), fecha_fin=datetime.now() + timedelta(days=2, hours=12), tipo="Audiencia", ubicacion="Juzgado 1° Civil", color="#dc2626"),
            Evento(titulo="Reunión con María García", fecha_inicio=datetime.now() + timedelta(days=1, hours=16), fecha_fin=datetime.now() + timedelta(days=1, hours=17), tipo="Reunión", ubicacion="Oficina principal", color="#3b82f6"),
            Evento(titulo="Vencimiento CTO-2025-002", fecha_inicio=datetime.now() + timedelta(days=2, hours=8), fecha_fin=datetime.now() + timedelta(days=2, hours=8), tipo="Plazo", color="#f59e0b"),
        ])
        await db.flush()

        # 3 Transacciones
        db.add_all([
            Transaccion(tipo="Ingreso", categoria="Honorarios", monto=25000.00, fecha=datetime.now() - timedelta(days=60), descripcion="Honorarios María García"),
            Transaccion(tipo="Gasto", categoria="Alquiler", monto=12000.00, fecha=datetime.now() - timedelta(days=30), descripcion="Renta oficina"),
            Transaccion(tipo="Ingreso", categoria="Honorarios", monto=32000.00, fecha=datetime.now() - timedelta(days=20), descripcion="Honorarios Bufete López"),
        ])

        # Documento RAG
        db.add(DocumentoLegal(
            titulo="Art. 1796 CCF",
            contenido="Los contratos se perfeccionan por el mero consentimiento, excepto aquellos que deben revestir una forma establecida por la ley.",
            embedding=generar_embedding("Los contratos se perfeccionan por el mero consentimiento"),
            fuente="Código Civil Federal", articulo="Art. 1796"
        ))

        await db.commit()
        print("✅ Datos de ejemplo insertados")

    print("\n🔧 Paso 3: Verificando...")
    async with AsyncSessionLocal() as db:
        clientes = await db.scalar(select(Cliente).limit(1))
        expedientes = await db.scalar(select(Expediente).limit(1))
        contratos = await db.scalar(select(Contrato).limit(1))
        eventos = await db.scalar(select(Evento).limit(1))
        transacciones = await db.scalar(select(Transaccion).limit(1))
        users = await db.scalar(select(User).limit(1))
        docs = await db.scalar(select(DocumentoLegal).limit(1))
        
        print(f"  Clientes: {'✅' if clientes else '❌'}")
        print(f"  Expedientes: {'✅' if expedientes else '❌'}")
        print(f"  Contratos: {'✅' if contratos else '❌'}")
        print(f"  Eventos: {'✅' if eventos else '❌'}")
        print(f"  Transacciones: {'✅' if transacciones else '❌'}")
        print(f"  Usuarios: {'✅' if users else '❌'}")
        print(f"  Documentos RAG: {'✅' if docs else '❌'}")

    print("\n✅ RECONSTRUCCIÓN COMPLETA")
    print("🔑 Usuario: admin@inspol.com")
    print("🔑 Contraseña: admin123")
    print("\nAhora inicia el frontend con: cd frontend && rm -rf .next && npm run dev")
    print("Y abre http://localhost:3000/dashboard")

if __name__ == "__main__":
    asyncio.run(rebuild())
