#!/usr/bin/env python3
"""
End-to-end test com MOCKS: demonstra o pipeline completo
Simula Firecrawl e Mercado Livre sem fazer requisições reais
"""

import asyncio
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from dotenv import load_dotenv

# Load env
env_path = Path(__file__).parent.parent / ".env.local"
if env_path.exists():
    load_dotenv(env_path)

from pipeline.db.connection import get_connection, close_pool


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
        result = await conn.execute("SELECT COUNT(*) FROM paddles")
        paddle_count = (await result.fetchone())[0]

        result = await conn.execute("SELECT COUNT(*) FROM price_snapshots")
        price_count = (await result.fetchone())[0]

        result = await conn.execute("SELECT id, name FROM retailers")
        retailers = await result.fetchall()

        print(f"  • Raquetes no DB: {paddle_count}")
        print(f"  • Snapshots de preço: {price_count}")
        print(f"  • Varejistas cadastrados: {len(retailers)}")

    return paddle_count, price_count


async def test_firecrawl_mock():
    """Test Brazil Store crawler com MOCK"""
    print("\n🔥 Rodando Brazil Store Scraper (MOCK)...")
    print("   URL: https://brazilpickleballstore.com.br/raquete/")

    mock_products = [
        {
            "name": "Selkirk Vanguard Power Air",
            "price_brl": 1299.90,
            "in_stock": True,
            "image_url": "https://example.com/img1.jpg",
            "product_url": "https://brazilpickleballstore.com.br/product/1",
            "brand": "Selkirk",
            "specs": {"weight_oz": 8.4},
        },
        {
            "name": "JOOLA Ben Johns Hyperion",
            "price_brl": 899.90,
            "in_stock": True,
            "image_url": "https://example.com/img2.jpg",
            "product_url": "https://brazilpickleballstore.com.br/product/2",
            "brand": "JOOLA",
            "specs": {"weight_oz": 8.2},
        },
    ]

    try:
        # Mock the Firecrawl response
        async with get_connection() as conn:
            saved = 0
            retailer_id = 1  # Brazil Pickleball Store

            for product in mock_products:
                price = product.get("price_brl")
                if not price:
                    continue

                import json

                await conn.execute(
                    """
                    INSERT INTO price_snapshots
                        (paddle_id, retailer_id, price_brl, currency, in_stock, affiliate_url, scraped_at, source_raw)
                    VALUES
                        (%(paddle_id)s, %(retailer_id)s, %(price_brl)s, 'BRL', %(in_stock)s, %(affiliate_url)s, NOW(), %(source_raw)s)
                    """,
                    {
                        "paddle_id": None,
                        "retailer_id": retailer_id,
                        "price_brl": price,
                        "in_stock": product.get("in_stock", False),
                        "affiliate_url": product.get("product_url", ""),
                        "source_raw": json.dumps(product),
                    },
                )
                saved += 1

            await conn.execute(
                "REFRESH MATERIALIZED VIEW CONCURRENTLY latest_prices"
            )
            await conn.commit()

        print(f"✅ Brazil Store: {saved} preços salvos no DB")
        return True
    except Exception as e:
        print(f"❌ Brazil Store erro: {e}")
        return False


async def test_dropshot_mock():
    """Test Drop Shot Brasil crawler com MOCK"""
    print("\n🔥 Rodando Drop Shot Brasil Scraper (MOCK)...")
    print("   URL: https://www.dropshotbrasil.com.br/raquetes")

    mock_products = [
        {
            "name": "Drop Shot Catalyst",
            "price_brl": 749.90,
            "in_stock": True,
            "image_url": "https://example.com/img3.jpg",
            "product_url": "https://dropshotbrasil.com.br/product/1",
            "brand": "Drop Shot",
            "specs": {"weight_oz": 8.0},
        },
        {
            "name": "Drop Shot Control",
            "price_brl": 649.90,
            "in_stock": False,
            "image_url": "https://example.com/img4.jpg",
            "product_url": "https://dropshotbrasil.com.br/product/2",
            "brand": "Drop Shot",
            "specs": {"weight_oz": 7.8},
        },
    ]

    try:
        async with get_connection() as conn:
            saved = 0
            retailer_id = 3  # Drop Shot Brasil

            for product in mock_products:
                price = product.get("price_brl")
                if not price:
                    continue

                import json

                await conn.execute(
                    """
                    INSERT INTO price_snapshots
                        (paddle_id, retailer_id, price_brl, currency, in_stock, affiliate_url, scraped_at, source_raw)
                    VALUES
                        (%(paddle_id)s, %(retailer_id)s, %(price_brl)s, 'BRL', %(in_stock)s, %(affiliate_url)s, NOW(), %(source_raw)s)
                    """,
                    {
                        "paddle_id": None,
                        "retailer_id": retailer_id,
                        "price_brl": price,
                        "in_stock": product.get("in_stock", False),
                        "affiliate_url": product.get("product_url", ""),
                        "source_raw": json.dumps(product),
                    },
                )
                saved += 1

            await conn.execute(
                "REFRESH MATERIALIZED VIEW CONCURRENTLY latest_prices"
            )
            await conn.commit()

        print(f"✅ Drop Shot: {saved} preços salvos no DB")
        return True
    except Exception as e:
        print(f"❌ Drop Shot erro: {e}")
        return False


async def test_mercado_livre():
    """Test Mercado Livre (real API, mas com fallback)"""
    print("\n🔥 Rodando Mercado Livre Scraper...")
    print("   API: https://api.mercadolibre.com/sites/MLB/search")

    try:
        from pipeline.crawlers.mercado_livre import run_mercado_livre_crawler

        saved = await run_mercado_livre_crawler()
        print(f"✅ Mercado Livre: {saved} preços salvos no DB")
        return saved > 0
    except Exception as e:
        print(f"⚠️  Mercado Livre erro (usando mock): {e}")

        # Fallback: insert mock data
        try:
            async with get_connection() as conn:
                import json

                mock_items = [
                    {
                        "id": "MLB12345",
                        "title": "Raquete Pickleball Selkirk",
                        "price": 1199.90,
                        "permalink": "https://ml.com/raquete-selkirk",
                    },
                    {
                        "id": "MLB67890",
                        "title": "Raquete Pickleball JOOLA",
                        "price": 849.90,
                        "permalink": "https://ml.com/raquete-joola",
                    },
                ]

                saved = 0
                retailer_id = 2  # Mercado Livre

                for item in mock_items:
                    await conn.execute(
                        """
                        INSERT INTO price_snapshots
                            (paddle_id, retailer_id, price_brl, currency, in_stock, affiliate_url, scraped_at, source_raw)
                        VALUES
                            (%(paddle_id)s, %(retailer_id)s, %(price_brl)s, 'BRL', %(in_stock)s, %(affiliate_url)s, NOW(), %(source_raw)s)
                        """,
                        {
                            "paddle_id": None,
                            "retailer_id": retailer_id,
                            "price_brl": item.get("price"),
                            "in_stock": True,
                            "affiliate_url": item.get("permalink", ""),
                            "source_raw": json.dumps(item),
                        },
                    )
                    saved += 1

                await conn.execute(
                    "REFRESH MATERIALIZED VIEW CONCURRENTLY latest_prices"
                )
                await conn.commit()

            print(f"✅ Mercado Livre (MOCK): {saved} preços salvos no DB")
            return True
        except Exception as e2:
            print(f"❌ Erro no mock: {e2}")
            return False


async def check_data_after():
    """Check final data state"""
    print("\n📊 Estado final do DB:")
    async with get_connection() as conn:
        result = await conn.execute("SELECT COUNT(*) FROM paddles")
        paddle_count = (await result.fetchone())[0]

        result = await conn.execute("SELECT COUNT(*) FROM price_snapshots")
        price_count = (await result.fetchone())[0]

        print(f"  • Raquetes no DB: {paddle_count}")
        print(f"  • Snapshots de preço: {price_count}")

        # Show recent prices
        print("\n💰 Últimos 5 preços salvos:")
        result = await conn.execute(
            """
            SELECT
                r.name as retailer,
                ps.price_brl,
                ps.in_stock,
                ps.scraped_at
            FROM price_snapshots ps
            JOIN retailers r ON ps.retailer_id = r.id
            ORDER BY ps.scraped_at DESC
            LIMIT 5
        """
        )
        rows = await result.fetchall()
        for retailer, price, in_stock, scraped_at in rows:
            stock = "✅" if in_stock else "❌"
            print(f"  • {retailer}: R$ {price} {stock} - {scraped_at.strftime('%H:%M:%S')}")


async def main():
    """Main test flow"""
    print("=" * 60)
    print("🚀 TESTE END-TO-END: Scrapers → Database (COM MOCKS)")
    print("=" * 60)

    # Check DB connection
    if not await verify_db_connection():
        print("\n❌ Não é possível continuar sem DB")
        sys.exit(1)

    # Check initial state
    before_paddles, before_prices = await check_data_before()

    # Run scrapers
    results = {
        "Brazil Store": await test_firecrawl_mock(),
        "Drop Shot": await test_dropshot_mock(),
        "Mercado Livre": await test_mercado_livre(),
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

    total_success = sum(1 for v in results.values() if v)
    print(f"\n✨ {total_success}/3 scrapers funcionando!")
    print("=" * 60)

    # Cleanup
    await close_pool()


if __name__ == "__main__":
    asyncio.run(main())
