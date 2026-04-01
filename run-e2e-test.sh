#!/bin/bash
set -e

echo "==========================================="
echo "🚀 Setup E2E Test: Scrapers → DB Local"
echo "==========================================="

# Step 1: Check Docker
echo -e "\n1️⃣ Verificando Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado"
    exit 1
fi
echo "✅ Docker disponível"

# Step 2: Start DB
echo -e "\n2️⃣ Iniciando PostgreSQL (docker compose)..."
docker compose up -d
sleep 5

# Wait for DB to be ready
echo "   Aguardando DB ficar pronto..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if docker compose exec postgres pg_isready -U pickleiq > /dev/null 2>&1; then
        echo "✅ PostgreSQL está pronto"
        break
    fi
    attempt=$((attempt + 1))
    sleep 1
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Timeout esperando DB"
    docker compose logs
    exit 1
fi

# Step 3: Setup Python venv
echo -e "\n3️⃣ Setup Python environment..."
cd pipeline
if [ ! -d ".venv" ]; then
    echo "   Criando venv..."
    python3 -m venv .venv
fi
source .venv/bin/activate
echo "✅ venv ativado"

# Step 4: Install dependencies
echo -e "\n4️⃣ Instalando dependências..."
pip install -q -e ".[dev]"
echo "✅ Dependências instaladas"

# Step 5: Verify .env.local
echo -e "\n5️⃣ Verificando .env.local..."
if [ ! -f "../.env.local" ]; then
    echo "❌ .env.local não encontrado"
    echo "   Crie o arquivo com sua FIRECRAWL_API_KEY:"
    echo "   cp .env.example .env.local"
    exit 1
fi
echo "✅ .env.local existe"

# Step 6: Run E2E test
echo -e "\n6️⃣ Rodando teste E2E...\n"
python test_e2e_scraper.py

echo -e "\n==========================================="
echo "✅ Teste concluído!"
echo "==========================================="
echo -e "\n💡 Dicas:"
echo "  • Ver logs do DB: docker compose logs -f postgres"
echo "  • Parar DB: docker compose down"
echo "  • Ver dados: psql -h localhost -U pickleiq -d pickleiq"
echo "  • Limpar DB: docker compose down -v"
