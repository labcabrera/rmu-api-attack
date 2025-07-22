#!/bin/bash

# Script de inicio para el desarrollo de la API RMU Attack

echo "🚀 Iniciando RMU API Attack..."
echo "==============================================="

# Activar entorno virtual
if [ -d ".venv" ]; then
    echo "📦 Activando entorno virtual..."
    source .venv/bin/activate
else
    echo "❌ No se encontró el entorno virtual. Ejecuta 'python -m venv .venv' primero."
    exit 1
fi

# Verificar instalación de dependencias
echo "🔍 Verificando dependencias..."
pip list | grep fastapi > /dev/null
if [ $? -ne 0 ]; then
    echo "📥 Instalando dependencias..."
    pip install -r requirements.txt
fi

echo "✅ Dependencias verificadas"
echo ""
echo "🌐 Iniciando servidor FastAPI..."
echo "📚 Documentación disponible en: http://localhost:8000/docs"
echo "🔄 Swagger UI en: http://localhost:8000/docs"
echo "📖 ReDoc en: http://localhost:8000/redoc"
echo ""
echo "Para detener el servidor presiona Ctrl+C"
echo "==============================================="

# Iniciar el servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
