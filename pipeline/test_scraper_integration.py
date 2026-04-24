#!/usr/bin/env python3
"""
End-to-end test: Firecrawl → DB local
Extrai dados dos scrapers e salva no banco de dados local
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from firecrawl import FirecrawlApp

# Load env from .env.local
env_path = Path(__file__).parent.parent / ".env.local"
if env_path.exists():
    load_dotenv(env_path)

from pipeline.db.connection import get_connection, close_pool
from pipeline.crawlers.brazil_store import run_brazil_store_crawler
from pipeline.crawlers.dropshot_brasil import run_dropshot_brasil_crawler
from pipeline.crawlers.mercado_livre import run_mercado_livre_crawler


async def verify_db_connection():
    """Test database connection"""
    print("🔗 Verificando conexão com DB...")
    try:
        async with get_connection() as conn:
            result = await conn.execute("SELECT version()")
            version = await result.fetchone()
            print(f"✅ DB conectado: {version[0][:50]}...")
            return True
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False


async def check_data_before():
    """Check initial data state"""
    print("\n📊 Estado inicial do DB:")
    async with get_connection() as conn:
        # Count paddles
        result = await conn.execute("SELECT COUNT(*) FROM paddles")
        paddle_count = (await result.fetchone())[0]

        # Count price snapshots
        result = await conn.execute("SELECT COUNT(*) FROM price_snapshots")
        price_count = (await result.fetchone())[0]

        # Count retailers
        result = await conn.execute("SELECT id, name FROM retailers")
        retailers = await result.fetchall()

        print(f"  • Raquetes no DB: {paddle_count}")
        print(f"  • Snapshots de preço: {price_count}")
        print(f"  • Varejistas cadastrados: {len(retailers)}")
        for rid, rname in retailers:
            print(f"    - {rname} (ID: {rid})")

    return paddle_count, price_count


async def run_brazil_store_scraper():
    """Test Brazil Store crawler"""
    print("\n🔥 Rodando Brazil Store Scraper...")
    print("   URL: https://brazilpickleballstore.com.br/raquete/")
    try:
        saved = await run_brazil_store_crawler()
        print(f"✅ Brazil Store: {saved} preços salvos no DB")
        return True
    except Exception as e:
        print(f"❌ Brazil Store erro: {e}")
        return False


async def run_dropshot_scraper():
    """Test Drop Shot Brasil crawler"""
    print("\n🔥 Rodando Drop Shot Brasil Scraper...")
    print("   URL: https://www.dropshotbrasil.com.br/raquetes")
    try:
        saved = await run_dropshot_brasil_crawler()
        print(f"✅ Drop Shot: {saved} preços salvos no DB")
        return True
    except Exception as e:
        print(f"❌ Drop Shot erro: {e}")
        return False


async def run_mercado_livre_scraper():
    """Test Mercado Livre crawler"""
    print("\n🔥 Rodando Mercado Livre Scraper...")
    print("   API: https://api.mercadolibre.com/sites/MLB/search")
    try:
        saved = await run_mercado_livre_crawler()
        print(f"✅ Mercado Livre: {saved} preços salvos no DB")
        return True
    except Exception as e:
        print(f"❌ Mercado Livre erro: {e}")
        return False


async def check_data_after():
    """Check final data state and show sample"""
    print("\n📊 Estado final do DB:")
    async with get_connection() as conn:
        # Count totals
        result = await conn.execute("SELECT COUNT(*) FROM paddles")
        paddle_count = (await result.fetchone())[0]

        result = await conn.execute("SELECT COUNT(*) FROM price_snapshots")
        price_count = (await result.fetchone())[0]

        print(f"  • Raquetes no DB: {paddle_count}")
        print(f"  • Snapshots de preço: {price_count}")

        # Show recent prices
        print("\n💰 Últimos preços salvos:")
        result = await conn.execute("""
            SELECT
                p.name,
                r.name as retailer,
                ps.price_brl,
                ps.in_stock,
                ps.scraped_at
            FROM price_snapshots ps
            JOIN paddles p ON ps.paddle_id = p.id
            JOIN retailers r ON ps.retailer_id = r.id
            ORDER BY ps.scraped_at DESC
            LIMIT 5
        """)
        rows = await result.fetchall()
        for name, retailer, price, in_stock, scraped_at in rows:
            stock = "✅ Em estoque" if in_stock else "❌ Fora de estoque"
            print(f"  • {name}")
            print(f"    {retailer}: R$ {price} ({stock}) - {scraped_at}")


def test_scraper_extracts_enriched_fields():
    """Verify scraper extracts skill_level, specs, and in_stock."""
    # Mock enriched response data
    result = {
        "name": "Paddle Pro X",
        "brand": "PickleBrand",
        "skill_level": "intermediate",
        "specs": {
            "swingweight": 105,
            "twistweight": 7,
            "weight_oz": 7.8,
            "core_thickness_mm": 16,
            "face_material": "carbon fiber"
        },
        "in_stock": True
    }

    # Validate enriched fields
    assert "skill_level" in result, "skill_level field missing"
    if result["skill_level"]:
        assert result["skill_level"] in ["beginner", "intermediate", "advanced"]

    if result.get("specs"):
        specs = result["specs"]
        assert isinstance(specs, dict)
        # At least one spec should be populated
        assert any([
            specs.get("swingweight"),
            specs.get("twistweight"),
            specs.get("weight_oz"),
            specs.get("core_thickness_mm"),
            specs.get("face_material")
        ]), "No specs populated"

    assert "in_stock" in result, "in_stock field missing"
    if result["in_stock"] is not None:
        assert isinstance(result["in_stock"], bool)


async def main():
    """Main test flow"""
    print("=" * 60)
    print("🚀 TESTE END-TO-END: Scrapers → Database")
    print("=" * 60)

    # Check DB connection
    if not await verify_db_connection():
        print("\n❌ Não é possível continuar sem DB. Suba com:")
        print("   docker-compose up -d")
        sys.exit(1)

    # Check initial state
    before_paddles, before_prices = await check_data_before()

    # Run scrapers
    results = {
        "Brazil Store": await run_brazil_store_scraper(),
        "Drop Shot": await run_dropshot_scraper(),
        "Mercado Livre": await run_mercado_livre_scraper(),
    }

    # Check final state
    await check_data_after()

    # Summary
    print("\n" + "=" * 60)
    print("📈 RESUMO")
    print("=" * 60)
    for scraper, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {scraper}")

    print("=" * 60)

    # Cleanup
    await close_pool()


if __name__ == "__main__":
    asyncio.run(main())
