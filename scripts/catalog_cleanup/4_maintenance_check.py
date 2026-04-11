#!/usr/bin/env python3
"""
Script de Verificação Contínua do Catálogo PickleIQ
Checagens diárias para manter o catálogo saudável.

Uso:
    python scripts/catalog_cleanup/4_maintenance_check.py
    python scripts/catalog_cleanup/4_maintenance_check.py --alert-telegram
"""

import asyncio
import json
import logging
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

sys.path.insert(0, "/home/diego/Documentos/picklepicker")
sys.path.insert(0, "/home/diego/Documentos/picklepicker/pipeline")

from pipeline.db.connection import get_connection
from pipeline.alerts.telegram import send_telegram_alert


@dataclass
class HealthCheck:
    """Resultado de uma checagem de saúde."""
    check_name: str
    status: str  # "OK", "WARNING", "CRITICAL"
    value: any
    threshold: any
    message: str
    recommendation: str


class CatalogHealthMonitor:
    """Monitor de saúde do catálogo."""
    
    THRESHOLDS = {
        "min_paddles": 100,
        "max_stale_percent": 20,  # % de paddles com dados desatualizados
        "max_no_image_percent": 30,
        "max_no_price_percent": 10,
        "max_duplicate_percent": 5,
    }
    
    def __init__(self, send_alerts: bool = False):
        self.send_alerts = send_alerts
        self.checks: List[HealthCheck] = []
        self.metrics = {}
    
    async def run_health_check(self) -> List[HealthCheck]:
        """Executa todas as checagens de saúde."""
        logger.info("🏥 Iniciando verificação de saúde do catálogo...")
        
        await self._check_paddle_count()
        await self._check_data_freshness()
        await self._check_image_coverage()
        await self._check_price_coverage()
        await self._check_duplicate_ratio()
        await self._check_review_queue()
        await self._check_embedding_coverage()
        await self._check_crawler_health()
        
        # Enviar alertas se necessário
        if self.send_alerts:
            await self._send_critical_alerts()
        
        return self.checks
    
    async def _check_paddle_count(self):
        """Verifica se há raquetes suficientes no catálogo."""
        async with get_connection() as conn:
            row = await (await conn.execute("SELECT COUNT(*) FROM paddles")).fetchone()
            count = row[0] if row else 0
            
            status = "OK" if count >= self.THRESHOLDS["min_paddles"] else "CRITICAL"
            
            self.checks.append(HealthCheck(
                check_name="Total de Paddles",
                status=status,
                value=count,
                threshold=self.THRESHOLDS["min_paddles"],
                message=f"{count} paddles no catálogo",
                recommendation="Executar crawlers imediatamente" if status == "CRITICAL" else "Nenhuma"
            ))
            self.metrics["total_paddles"] = count
    
    async def _check_data_freshness(self):
        """Verifica percentual de paddles com dados frescos."""
        async with get_connection() as conn:
            # Paddles atualizados nos últimos 7 dias
            query = """
                SELECT COUNT(DISTINCT paddle_id)
                FROM price_snapshots
                WHERE scraped_at > NOW() - INTERVAL '7 days'
            """
            row = await (await conn.execute(query)).fetchone()
            fresh_count = row[0] if row else 0
            
            total = self.metrics.get("total_paddles", 1)
            stale_percent = ((total - fresh_count) / total) * 100 if total > 0 else 0
            
            if stale_percent <= self.THRESHOLDS["max_stale_percent"]:
                status = "OK"
            elif stale_percent <= 50:
                status = "WARNING"
            else:
                status = "CRITICAL"
            
            self.checks.append(HealthCheck(
                check_name="Frescor dos Dados",
                status=status,
                value=f"{100-stale_percent:.1f}%",
                threshold=f"<{self.THRESHOLDS['max_stale_percent']}% stale",
                message=f"{fresh_count}/{total} paddles atualizados na última semana",
                recommendation="Verificar se crawlers estão rodando corretamente"
            ))
            self.metrics["fresh_percent"] = 100 - stale_percent
    
    async def _check_image_coverage(self):
        """Verifica cobertura de imagens."""
        async with get_connection() as conn:
            # Paddles com imagens válidas
            query = """
                SELECT COUNT(*) FROM paddles
                WHERE image_url IS NOT NULL
                  AND image_url != ''
                  AND image_url NOT ILIKE '%placeholder%'
                  AND image_url NOT ILIKE '%default%'
            """
            row = await (await conn.execute(query)).fetchone()
            with_image = row[0] if row else 0
            
            total = self.metrics.get("total_paddles", 1)
            no_image_percent = ((total - with_image) / total) * 100 if total > 0 else 0
            
            if no_image_percent <= self.THRESHOLDS["max_no_image_percent"]:
                status = "OK"
            elif no_image_percent <= 50:
                status = "WARNING"
            else:
                status = "CRITICAL"
            
            self.checks.append(HealthCheck(
                check_name="Cobertura de Imagens",
                status=status,
                value=f"{(with_image/total)*100:.1f}%",
                threshold=f">{100-self.THRESHOLDS['max_no_image_percent']}%",
                message=f"{with_image}/{total} paddles com imagens válidas",
                recommendation="Executar extração de imagens (Phase 2 dos crawlers)"
            ))
    
    async def _check_price_coverage(self):
        """Verifica se paddles têm preços."""
        async with get_connection() as conn:
            query = """
                SELECT COUNT(DISTINCT p.id)
                FROM paddles p
                INNER JOIN price_snapshots ps ON ps.paddle_id = p.id
            """
            row = await (await conn.execute(query)).fetchone()
            with_price = row[0] if row else 0
            
            total = self.metrics.get("total_paddles", 1)
            no_price_percent = ((total - with_price) / total) * 100 if total > 0 else 0
            
            if no_price_percent <= self.THRESHOLDS["max_no_price_percent"]:
                status = "OK"
            elif no_price_percent <= 25:
                status = "WARNING"
            else:
                status = "CRITICAL"
            
            self.checks.append(HealthCheck(
                check_name="Cobertura de Preços",
                status=status,
                value=f"{(with_price/total)*100:.1f}%",
                threshold=f">{100-self.THRESHOLDS['max_no_price_percent']}%",
                message=f"{with_price}/{total} paddles com preços",
                recommendation="Verificar conexão com varejistas"
            ))
    
    async def _check_duplicate_ratio(self):
        """Verifica percentual de possíveis duplicatas."""
        async with get_connection() as conn:
            # Nomes que aparecem mais de uma vez
            query = """
                SELECT COUNT(*) FROM (
                    SELECT name FROM paddles
                    GROUP BY name
                    HAVING COUNT(*) > 1
                ) dup
            """
            row = await (await conn.execute(query)).fetchone()
            dup_names = row[0] if row else 0
            
            total = self.metrics.get("total_paddles", 1)
            dup_percent = (dup_names / total) * 100 if total > 0 else 0
            
            if dup_percent <= self.THRESHOLDS["max_duplicate_percent"]:
                status = "OK"
            else:
                status = "WARNING"
            
            self.checks.append(HealthCheck(
                check_name="Taxa de Duplicatas",
                status=status,
                value=f"{dup_percent:.1f}%",
                threshold=f"<{self.THRESHOLDS['max_duplicate_percent']}%",
                message=f"{dup_names} nomes duplicados detectados",
                recommendation="Revisar review_queue e consolidar duplicatas"
            ))
    
    async def _check_review_queue(self):
        """Verifica tamanho da review queue."""
        async with get_connection() as conn:
            query = "SELECT COUNT(*), type FROM review_queue WHERE status = 'pending' GROUP BY type"
            rows = await (await conn.execute(query)).fetchall()
            
            total_pending = sum(r[0] for r in rows)
            
            by_type = {r[1]: r[0] for r in rows}
            
            if total_pending < 50:
                status = "OK"
            elif total_pending < 200:
                status = "WARNING"
            else:
                status = "CRITICAL"
            
            self.checks.append(HealthCheck(
                check_name="Review Queue",
                status=status,
                value=total_pending,
                threshold="<50 pendentes",
                message=f"{total_pending} itens pendentes: {by_type}",
                recommendation="Processar itens da review queue"
            ))
    
    async def _check_embedding_coverage(self):
        """Verifica cobertura de embeddings."""
        async with get_connection() as conn:
            query = "SELECT COUNT(*) FROM paddle_embeddings"
            row = await (await conn.execute(query)).fetchone()
            embedding_count = row[0] if row else 0
            
            total = self.metrics.get("total_paddles", 1)
            coverage = (embedding_count / total) * 100 if total > 0 else 0
            
            if coverage >= 95:
                status = "OK"
            elif coverage >= 80:
                status = "WARNING"
            else:
                status = "CRITICAL"
            
            self.checks.append(HealthCheck(
                check_name="Cobertura de Embeddings",
                status=status,
                value=f"{coverage:.1f}%",
                threshold=">=95%",
                message=f"{embedding_count}/{total} paddles com embeddings",
                recommendation="Executar pipeline/embeddings/batch_embedder.py"
            ))
    
    async def _check_crawler_health(self):
        """Verifica saúde dos crawlers (última execução bem-sucedida)."""
        async with get_connection() as conn:
            # Verificar se há snapshots recentes de cada retailer
            query = """
                SELECT r.name, MAX(ps.scraped_at) as last_scrape
                FROM retailers r
                LEFT JOIN price_snapshots ps ON ps.retailer_id = r.id
                WHERE r.is_active = TRUE
                GROUP BY r.id, r.name
            """
            rows = await (await conn.execute(query)).fetchall()
            
            issues = []
            for retailer_name, last_scrape in rows:
                if last_scrape is None:
                    issues.append(f"{retailer_name}: Nunca executado")
                elif last_scrape < datetime.now() - timedelta(days=2):
                    days_ago = (datetime.now() - last_scrape).days
                    issues.append(f"{retailer_name}: {days_ago} dias sem execução")
            
            if not issues:
                status = "OK"
                message = "Todos os crawlers ativos nos últimos 2 dias"
            else:
                status = "WARNING"
                message = f"Problemas: {', '.join(issues)}"
            
            self.checks.append(HealthCheck(
                check_name="Saúde dos Crawlers",
                status=status,
                value=len(issues),
                threshold="0 problemas",
                message=message,
                recommendation="Verificar GitHub Actions workflows"
            ))
    
    async def _send_critical_alerts(self):
        """Envia alertas para checks críticos."""
        critical_checks = [c for c in self.checks if c.status == "CRITICAL"]
        
        if not critical_checks:
            return
        
        message = "🚨 *ALERTA CRÍTICO - PickleIQ Catalog Health*\n\n"
        for check in critical_checks:
            message += f"❌ *{check.check_name}*\n"
            message += f"   {check.message}\n"
            message += f"   → {check.recommendation}\n\n"
        
        try:
            await send_telegram_alert(message)
            logger.info("✅ Alertas críticos enviados via Telegram")
        except Exception as e:
            logger.error(f"❌ Falha ao enviar alerta: {e}")
    
    def print_report(self):
        """Imprime relatório de saúde."""
        print("\n" + "=" * 70)
        print("🏥 RELATÓRIO DE SAÚDE DO CATÁLOGO PICKLEIQ")
        print("=" * 70)
        print(f"Gerado em: {datetime.now().isoformat()}")
        print()
        
        # Contar por status
        ok_count = sum(1 for c in self.checks if c.status == "OK")
        warning_count = sum(1 for c in self.checks if c.status == "WARNING")
        critical_count = sum(1 for c in self.checks if c.status == "CRITICAL")
        
        print(f"Status Geral: {ok_count} ✅ | {warning_count} ⚠️  | {critical_count} 🚨")
        print()
        
        for check in self.checks:
            icon = "✅" if check.status == "OK" else "⚠️" if check.status == "WARNING" else "🚨"
            print(f"{icon} {check.check_name}: {check.status}")
            print(f"   Valor: {check.value} (threshold: {check.threshold})")
            print(f"   {check.message}")
            if check.status != "OK":
                print(f"   → {check.recommendation}")
            print()
        
        print("=" * 70)
        
        # Status final
        if critical_count > 0:
            print("❌ STATUS: CRÍTICO - Ações imediatas necessárias!")
            sys.exit(1)
        elif warning_count > 0:
            print("⚠️  STATUS: ATENÇÃO - Verificar recomendações")
            sys.exit(0)
        else:
            print("✅ STATUS: SAUDÁVEL - Catálogo em ótimo estado!")
            sys.exit(0)


async def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Verificação de saúde do catálogo PickleIQ"
    )
    parser.add_argument(
        "--alert-telegram",
        action="store_true",
        help="Enviar alertas via Telegram para problemas críticos"
    )
    parser.add_argument(
        "--json-output",
        help="Salvar resultado em formato JSON"
    )
    
    args = parser.parse_args()
    
    monitor = CatalogHealthMonitor(send_alerts=args.alert_telegram)
    await monitor.run_health_check()
    
    if args.json_output:
        output = {
            "timestamp": datetime.now().isoformat(),
            "checks": [asdict(c) for c in monitor.checks]
        }
        with open(args.json_output, 'w') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Relatório JSON salvo em: {args.json_output}")
    
    monitor.print_report()


if __name__ == "__main__":
    asyncio.run(main())
