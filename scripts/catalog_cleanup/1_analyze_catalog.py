#!/usr/bin/env python3
"""
Script de Análise Pré-Limpeza do Catálogo PickleIQ
Gera relatórios detalhados sobre o estado atual do catálogo antes da limpeza.

Uso:
    python scripts/catalog_cleanup/1_analyze_catalog.py
    python scripts/catalog_cleanup/1_analyze_catalog.py --output-format json
"""

import asyncio
import json
import logging
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlparse

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Adicionar pipeline ao path
sys.path.insert(0, "/home/diego/Documentos/picklepicker")
sys.path.insert(0, "/home/diego/Documentos/picklepicker/pipeline")

from pipeline.db.connection import get_connection


@dataclass
class CatalogMetrics:
    """Métricas do catálogo."""
    timestamp: str
    total_paddles: int
    total_price_snapshots: int
    total_latest_prices: int
    total_embeddings: int
    total_specs: int
    total_review_queue: int
    total_retailers: int
    
    # Anomalias
    paddles_without_prices: int
    paddles_without_embeddings: int
    paddles_without_images: int
    paddles_with_placeholder_images: int
    duplicate_names: int
    
    # Preços
    avg_price_brl: Optional[float]
    min_price_brl: Optional[float]
    max_price_brl: Optional[float]
    
    # Frescor dos dados
    last_scrape_older_than_7d: int
    last_scrape_older_than_30d: int
    
    # Review queue
    pending_duplicates: int
    pending_spec_unmatched: int
    pending_price_anomaly: int


class CatalogAnalyzer:
    """Analisador do estado do catálogo."""
    
    def __init__(self):
        self.metrics = {}
    
    async def run_full_analysis(self) -> CatalogMetrics:
        """Executa análise completa do catálogo."""
        logger.info("🔍 Iniciando análise completa do catálogo...")
        
        async with get_connection() as conn:
            # Contagens básicas
            basic_counts = await self._get_basic_counts(conn)
            
            # Anomalias
            anomalies = await self._get_anomalies(conn)
            
            # Estatísticas de preços
            price_stats = await self._get_price_stats(conn)
            
            # Frescor dos dados
            freshness = await self._get_freshness_stats(conn)
            
            # Review queue
            review_stats = await self._get_review_queue_stats(conn)
            
            metrics = CatalogMetrics(
                timestamp=datetime.now().isoformat(),
                **basic_counts,
                **anomalies,
                **price_stats,
                **freshness,
                **review_stats,
            )
            
            return metrics
    
    async def _get_basic_counts(self, conn) -> dict:
        """Contagens básicas das tabelas."""
        logger.info("  📊 Coletando contagens básicas...")
        
        queries = {
            "total_paddles": "SELECT COUNT(*) FROM paddles",
            "total_price_snapshots": "SELECT COUNT(*) FROM price_snapshots",
            "total_latest_prices": "SELECT COUNT(*) FROM latest_prices",
            "total_embeddings": "SELECT COUNT(*) FROM paddle_embeddings",
            "total_specs": "SELECT COUNT(*) FROM paddle_specs",
            "total_review_queue": "SELECT COUNT(*) FROM review_queue",
            "total_retailers": "SELECT COUNT(*) FROM retailers",
        }
        
        results = {}
        for key, query in queries.items():
            row = await (await conn.execute(query)).fetchone()
            results[key] = row[0] if row else 0
        
        return results
    
    async def _get_anomalies(self, conn) -> dict:
        """Identifica anomalias no catálogo."""
        logger.info("  🔍 Verificando anomalias...")
        
        # Paddles sem preços
        no_prices_query = """
            SELECT COUNT(*) FROM paddles p
            WHERE NOT EXISTS (
                SELECT 1 FROM price_snapshots ps WHERE ps.paddle_id = p.id
            )
        """
        row = await (await conn.execute(no_prices_query)).fetchone()
        paddles_without_prices = row[0] if row else 0
        
        # Paddles sem embeddings
        no_embeddings_query = """
            SELECT COUNT(*) FROM paddles p
            WHERE NOT EXISTS (
                SELECT 1 FROM paddle_embeddings pe WHERE pe.paddle_id = p.id
            )
        """
        row = await (await conn.execute(no_embeddings_query)).fetchone()
        paddles_without_embeddings = row[0] if row else 0
        
        # Paddles sem imagens
        no_images_query = """
            SELECT COUNT(*) FROM paddles
            WHERE image_url IS NULL OR image_url = ''
        """
        row = await (await conn.execute(no_images_query)).fetchone()
        paddles_without_images = row[0] if row else 0
        
        # Paddles com placeholder images
        placeholder_query = """
            SELECT COUNT(*) FROM paddles
            WHERE image_url ILIKE '%placeholder%'
               OR image_url ILIKE '%default%'
               OR image_url ILIKE '%no-image%'
               OR image_url ILIKE '%sem-imagem%'
        """
        row = await (await conn.execute(placeholder_query)).fetchone()
        paddles_with_placeholder_images = row[0] if row else 0
        
        # Duplicatas por nome
        duplicates_query = """
            SELECT COUNT(*) FROM (
                SELECT name FROM paddles
                GROUP BY name
                HAVING COUNT(*) > 1
            ) dup
        """
        row = await (await conn.execute(duplicates_query)).fetchone()
        duplicate_names = row[0] if row else 0
        
        return {
            "paddles_without_prices": paddles_without_prices,
            "paddles_without_embeddings": paddles_without_embeddings,
            "paddles_without_images": paddles_without_images,
            "paddles_with_placeholder_images": paddles_with_placeholder_images,
            "duplicate_names": duplicate_names,
        }
    
    async def _get_price_stats(self, conn) -> dict:
        """Estatísticas de preços."""
        logger.info("  💰 Calculando estatísticas de preços...")
        
        query = """
            SELECT 
                AVG(price_brl) as avg_price,
                MIN(price_brl) as min_price,
                MAX(price_brl) as max_price
            FROM latest_prices
            WHERE price_brl > 0
        """
        row = await (await conn.execute(query)).fetchone()
        
        return {
            "avg_price_brl": round(row[0], 2) if row and row[0] else None,
            "min_price_brl": row[1] if row else None,
            "max_price_brl": row[2] if row else None,
        }
    
    async def _get_freshness_stats(self, conn) -> dict:
        """Estatísticas de frescor dos dados."""
        logger.info("  ⏰ Verificando frescor dos dados...")
        
        # Último scrape por paddle
        older_7d_query = """
            SELECT COUNT(*) FROM (
                SELECT paddle_id, MAX(scraped_at) as last_scraped
                FROM price_snapshots
                GROUP BY paddle_id
                HAVING MAX(scraped_at) < NOW() - INTERVAL '7 days'
            ) old
        """
        row = await (await conn.execute(older_7d_query)).fetchone()
        last_scrape_older_than_7d = row[0] if row else 0
        
        older_30d_query = """
            SELECT COUNT(*) FROM (
                SELECT paddle_id, MAX(scraped_at) as last_scraped
                FROM price_snapshots
                GROUP BY paddle_id
                HAVING MAX(scraped_at) < NOW() - INTERVAL '30 days'
            ) old
        """
        row = await (await conn.execute(older_30d_query)).fetchone()
        last_scrape_older_than_30d = row[0] if row else 0
        
        return {
            "last_scrape_older_than_7d": last_scrape_older_than_7d,
            "last_scrape_older_than_30d": last_scrape_older_than_30d,
        }
    
    async def _get_review_queue_stats(self, conn) -> dict:
        """Estatísticas da review queue."""
        logger.info("  📋 Verificando review queue...")
        
        query = """
            SELECT 
                COUNT(*) FILTER (WHERE type = 'duplicate' AND status = 'pending') as pending_duplicates,
                COUNT(*) FILTER (WHERE type = 'spec_unmatched' AND status = 'pending') as pending_spec_unmatched,
                COUNT(*) FILTER (WHERE type = 'price_anomaly' AND status = 'pending') as pending_price_anomaly
            FROM review_queue
        """
        row = await (await conn.execute(query)).fetchone()
        
        return {
            "pending_duplicates": row[0] if row else 0,
            "pending_spec_unmatched": row[1] if row else 0,
            "pending_price_anomaly": row[2] if row else 0,
        }
    
    def print_report(self, metrics: CatalogMetrics):
        """Imprime relatório formatado."""
        print("\n" + "=" * 70)
        print("📊 RELATÓRIO DE ANÁLISE DO CATÁLOGO PICKLEIQ")
        print("=" * 70)
        print(f"Gerado em: {metrics.timestamp}")
        print()
        
        print("📦 CONTAGENS PRINCIPAIS")
        print("-" * 40)
        print(f"  Total de raquetes:           {metrics.total_paddles:>8}")
        print(f"  Total de snapshots:          {metrics.total_price_snapshots:>8}")
        print(f"  Total de preços atuais:      {metrics.total_latest_prices:>8}")
        print(f"  Total de embeddings:         {metrics.total_embeddings:>8}")
        print(f"  Total de especificações:     {metrics.total_specs:>8}")
        print(f"  Varejistas configurados:     {metrics.total_retailers:>8}")
        print()
        
        print("⚠️  ANOMALIAS DETECTADAS")
        print("-" * 40)
        print(f"  Raquetes sem preços:              {metrics.paddles_without_prices:>6}")
        print(f"  Raquetes sem embeddings:          {metrics.paddles_without_embeddings:>6}")
        print(f"  Raquetes sem imagens:             {metrics.paddles_without_images:>6}")
        print(f"  Raquetes com placeholder:         {metrics.paddles_with_placeholder_images:>6}")
        print(f"  Nomes duplicados:                 {metrics.duplicate_names:>6}")
        print()
        
        print("💰 ESTATÍSTICAS DE PREÇOS")
        print("-" * 40)
        if metrics.avg_price_brl:
            print(f"  Preço médio:    R$ {metrics.avg_price_brl:>10,.2f}")
            print(f"  Preço mínimo:   R$ {metrics.min_price_brl:>10,.2f}")
            print(f"  Preço máximo:   R$ {metrics.max_price_brl:>10,.2f}")
        else:
            print("  Nenhum preço válido encontrado")
        print()
        
        print("⏰ FRESCOR DOS DADOS")
        print("-" * 40)
        print(f"  Sem atualização > 7 dias:   {metrics.last_scrape_older_than_7d:>6}")
        print(f"  Sem atualização > 30 dias:  {metrics.last_scrape_older_than_30d:>6}")
        print()
        
        print("📋 REVIEW QUEUE PENDENTE")
        print("-" * 40)
        print(f"  Duplicatas:        {metrics.pending_duplicates:>6}")
        print(f"  Specs não match:   {metrics.pending_spec_unmatched:>6}")
        print(f"  Anomalias preço:   {metrics.pending_price_anomaly:>6}")
        print()
        
        print("=" * 70)
        print()


async def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Análise pré-limpeza do catálogo PickleIQ"
    )
    parser.add_argument(
        "--output-format",
        choices=["text", "json"],
        default="text",
        help="Formato do relatório (default: text)"
    )
    parser.add_argument(
        "--output-file",
        help="Arquivo para salvar o relatório (opcional)"
    )
    
    args = parser.parse_args()
    
    analyzer = CatalogAnalyzer()
    metrics = await analyzer.run_full_analysis()
    
    if args.output_format == "json":
        output = json.dumps(asdict(metrics), indent=2, ensure_ascii=False)
    else:
        # Format text output
        import io
        buffer = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buffer
        analyzer.print_report(metrics)
        sys.stdout = old_stdout
        output = buffer.getvalue()
    
    # Imprime na tela
    print(output)
    
    # Salva em arquivo se especificado
    if args.output_file:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        logger.info(f"✅ Relatório salvo em: {args.output_file}")
    
    # Também salva relatório padrão para uso pelos outros scripts
    report_file = f"/home/diego/Documentos/picklepicker/scripts/catalog_cleanup/reports/analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    import os
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(asdict(metrics), f, indent=2, ensure_ascii=False)
    logger.info(f"✅ Relatório JSON salvo em: {report_file}")


if __name__ == "__main__":
    asyncio.run(main())
