#!/usr/bin/env python3
"""
Script de Verificação Pós-Limpeza do Catálogo PickleIQ
Valida integridade dos dados após operação de limpeza.

Uso:
    python scripts/catalog_cleanup/5_verify_cleanup.py
    python scripts/catalog_cleanup/5_verify_cleanup.py --compare-with pre_cleanup_report.json
"""

import asyncio
import json
import logging
import sys
from dataclasses import dataclass
from datetime import datetime
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


@dataclass
class VerificationResult:
    check: str
    status: str  # PASS, FAIL, WARNING
    message: str
    details: Optional[dict] = None


class PostCleanupVerifier:
    """Verificador de integridade pós-limpeza."""
    
    def __init__(self, pre_cleanup_report: Optional[str] = None):
        self.pre_cleanup_report = pre_cleanup_report
        self.results: List[VerificationResult] = []
        self.pre_metrics = None
        
        if pre_cleanup_report:
            try:
                with open(pre_cleanup_report) as f:
                    self.pre_metrics = json.load(f)
            except Exception as e:
                logger.warning(f"Não foi possível carregar relatório pré-limpeza: {e}")
    
    async def run_verification(self) -> List[VerificationResult]:
        """Executa todas as verificações pós-limpeza."""
        logger.info("🔍 Iniciando verificação pós-limpeza...")
        
        await self._verify_no_orphan_records()
        await self._verify_materialized_view()
        await self._verify_foreign_keys()
        await self._verify_api_endpoints()
        await self._verify_rag_functionality()
        await self._verify_retailer_integrations()
        await self._check_data_integrity()
        
        if self.pre_metrics:
            await self._compare_metrics()
        
        return self.results
    
    async def _verify_no_orphan_records(self):
        """Verifica se não existem registros órfãos após limpeza."""
        logger.info("  📋 Verificando registros órfãos...")
        
        async with get_connection() as conn:
            checks = [
                ("Embeddings órfãos", """
                    SELECT COUNT(*) FROM paddle_embeddings pe
                    LEFT JOIN paddles p ON p.id = pe.paddle_id
                    WHERE p.id IS NULL
                """),
                ("Specs órfãos", """
                    SELECT COUNT(*) FROM paddle_specs ps
                    LEFT JOIN paddles p ON p.id = ps.paddle_id
                    WHERE p.id IS NULL
                """),
                ("Snapshots órfãos", """
                    SELECT COUNT(*) FROM price_snapshots ps
                    LEFT JOIN paddles p ON p.id = ps.paddle_id
                    WHERE p.id IS NULL
                """),
                ("Review queue órfãos", """
                    SELECT COUNT(*) FROM review_queue rq
                    LEFT JOIN paddles p ON p.id = rq.paddle_id
                    WHERE p.id IS NULL AND rq.paddle_id IS NOT NULL
                """),
            ]
            
            issues = []
            for name, query in checks:
                row = await (await conn.execute(query)).fetchone()
                count = row[0] if row else 0
                if count > 0:
                    issues.append(f"{name}: {count}")
            
            if issues:
                self.results.append(VerificationResult(
                    check="Registros Órfãos",
                    status="FAIL",
                    message=f"Registros órfãos encontrados: {', '.join(issues)}",
                    details={"issues": issues}
                ))
            else:
                self.results.append(VerificationResult(
                    check="Registros Órfãos",
                    status="PASS",
                    message="Nenhum registro órfão encontrado"
                ))
    
    async def _verify_materialized_view(self):
        """Verifica se materialized view está atualizado."""
        logger.info("  🔄 Verificando materialized view...")
        
        async with get_connection() as conn:
            # Verificar se latest_prices tem dados
            query = "SELECT COUNT(*) FROM latest_prices"
            row = await (await conn.execute(query)).fetchone()
            count = row[0] if row else 0
            
            if count == 0:
                self.results.append(VerificationResult(
                    check="Materialized View",
                    status="FAIL",
                    message="latest_prices está vazio - necessita REFRESH"
                ))
            else:
                self.results.append(VerificationResult(
                    check="Materialized View",
                    status="PASS",
                    message=f"latest_prices atualizado com {count} registros"
                ))
    
    async def _verify_foreign_keys(self):
        """Verifica integridade das foreign keys."""
        logger.info("  🔗 Verificando foreign keys...")
        
        async with get_connection() as conn:
            # Verificar se todos os retailers existem
            query = """
                SELECT DISTINCT retailer_id FROM price_snapshots
                WHERE retailer_id NOT IN (SELECT id FROM retailers)
            """
            rows = await (await conn.execute(query)).fetchall()
            
            if rows:
                self.results.append(VerificationResult(
                    check="Foreign Keys",
                    status="FAIL",
                    message=f"Retailer_ids inválidos encontrados: {[r[0] for r in rows]}"
                ))
            else:
                self.results.append(VerificationResult(
                    check="Foreign Keys",
                    status="PASS",
                    message="Todas as foreign keys estão íntegras"
                ))
    
    async def _verify_api_endpoints(self):
        """Verifica se endpoints da API ainda funcionam."""
        logger.info("  🔌 Verificando endpoints da API...")
        
        try:
            # Testar se conseguimos conectar e fazer queries básicas
            async with get_connection() as conn:
                # Simular queries que a API faz
                queries = [
                    ("List paddles", "SELECT id, name FROM paddles LIMIT 5"),
                    ("Get prices", "SELECT * FROM latest_prices LIMIT 5"),
                    ("Search similar", "SELECT id FROM paddle_embeddings LIMIT 5"),
                ]
                
                failed = []
                for name, query in queries:
                    try:
                        await conn.execute(query)
                    except Exception as e:
                        failed.append(f"{name}: {e}")
                
                if failed:
                    self.results.append(VerificationResult(
                        check="API Endpoints",
                        status="FAIL",
                        message=f"Queries falharam: {', '.join(failed)}"
                    ))
                else:
                    self.results.append(VerificationResult(
                        check="API Endpoints",
                        status="PASS",
                        message="Todas as queries da API executam com sucesso"
                    ))
        except Exception as e:
            self.results.append(VerificationResult(
                check="API Endpoints",
                status="FAIL",
                message=f"Erro ao conectar: {e}"
            ))
    
    async def _verify_rag_functionality(self):
        """Verifica se RAG ainda funciona (embeddings + busca)."""
        logger.info("  🤖 Verificando funcionalidade RAG...")
        
        async with get_connection() as conn:
            # Verificar se temos embeddings suficientes
            query = """
                SELECT 
                    COUNT(*) as total_paddles,
                    COUNT(pe.id) as with_embeddings
                FROM paddles p
                LEFT JOIN paddle_embeddings pe ON pe.paddle_id = p.id
            """
            row = await (await conn.execute(query)).fetchone()
            total, with_emb = row if row else (0, 0)
            
            coverage = (with_emb / total * 100) if total > 0 else 0
            
            if coverage < 90:
                self.results.append(VerificationResult(
                    check="RAG Functionality",
                    status="WARNING",
                    message=f"Cobertura de embeddings baixa: {coverage:.1f}% ({with_emb}/{total})"
                ))
            else:
                self.results.append(VerificationResult(
                    check="RAG Functionality",
                    status="PASS",
                    message=f"RAG funcional: {coverage:.1f}% com embeddings"
                ))
    
    async def _verify_retailer_integrations(self):
        """Verifica se integrações com varejistas ainda funcionam."""
        logger.info("  🏪 Verificando integrações com varejistas...")
        
        async with get_connection() as conn:
            # Verificar se todos os varejistas ativos têm dados recentes
            query = """
                SELECT 
                    r.name,
                    r.is_active,
                    MAX(ps.scraped_at) as last_scrape,
                    COUNT(ps.id) as snapshot_count
                FROM retailers r
                LEFT JOIN price_snapshots ps ON ps.retailer_id = r.id
                GROUP BY r.id, r.name, r.is_active
                ORDER BY r.id
            """
            rows = await (await conn.execute(query)).fetchall()
            
            issues = []
            warnings = []
            
            for name, is_active, last_scrape, count in rows:
                if not is_active:
                    continue
                    
                if count == 0:
                    issues.append(f"{name}: sem snapshots")
                elif last_scrape and last_scrape < datetime.now().replace(day=datetime.now().day-7):
                    warnings.append(f"{name}: dados desatualizados ({last_scrape.date()})")
            
            status = "FAIL" if issues else ("WARNING" if warnings else "PASS")
            messages = issues + warnings
            
            self.results.append(VerificationResult(
                check="Retailer Integrations",
                status=status,
                message=f"{len(messages)} problemas encontrados: {', '.join(messages)}" if messages else "Todas as integrações funcionando",
                details={"issues": issues, "warnings": warnings}
            ))
    
    async def _check_data_integrity(self):
        """Verifica integridade geral dos dados."""
        logger.info("  🔍 Verificando integridade dos dados...")
        
        async with get_connection() as conn:
            checks = []
            
            # Verificar preços negativos ou zero
            query = "SELECT COUNT(*) FROM latest_prices WHERE price_brl <= 0"
            row = await (await conn.execute(query)).fetchone()
            if row and row[0] > 0:
                checks.append(f"Preços inválidos: {row[0]}")
            
            # Verificar paddles sem nome
            query = "SELECT COUNT(*) FROM paddles WHERE name IS NULL OR name = ''"
            row = await (await conn.execute(query)).fetchone()
            if row and row[0] > 0:
                checks.append(f"Paddles sem nome: {row[0]}")
            
            # Verificar duplicatas de nome
            query = """
                SELECT COUNT(*) FROM (
                    SELECT name FROM paddles GROUP BY name HAVING COUNT(*) > 1
                ) dup
            """
            row = await (await conn.execute(query)).fetchone()
            if row and row[0] > 0:
                checks.append(f"Nomes duplicados: {row[0]}")
            
            if checks:
                self.results.append(VerificationResult(
                    check="Data Integrity",
                    status="WARNING",
                    message=f"Problemas de integridade: {', '.join(checks)}",
                    details={"issues": checks}
                ))
            else:
                self.results.append(VerificationResult(
                    check="Data Integrity",
                    status="PASS",
                    message="Integridade dos dados verificada"
                ))
    
    async def _compare_metrics(self):
        """Compara métricas pré e pós-limpeza."""
        logger.info("  📊 Comparando métricas pré/pós limpeza...")
        
        async with get_connection() as conn:
            current = {}
            queries = {
                "total_paddles": "SELECT COUNT(*) FROM paddles",
                "total_snapshots": "SELECT COUNT(*) FROM price_snapshots",
                "total_embeddings": "SELECT COUNT(*) FROM paddle_embeddings",
                "total_specs": "SELECT COUNT(*) FROM paddle_specs",
            }
            
            for key, query in queries.items():
                row = await (await conn.execute(query)).fetchone()
                current[key] = row[0] if row else 0
            
            pre = self.pre_metrics.get("record_counts", self.pre_metrics)
            
            changes = []
            for key in ["total_paddles", "total_snapshots", "total_embeddings", "total_specs"]:
                before = pre.get(key, 0)
                after = current.get(key, 0)
                diff = after - before
                if diff != 0:
                    changes.append(f"{key}: {before} → {after} ({diff:+d})")
            
            if changes:
                self.results.append(VerificationResult(
                    check="Métricas Comparison",
                    status="PASS",
                    message="Mudanças detectadas:",
                    details={"changes": changes}
                ))
    
    def print_report(self):
        """Imprime relatório de verificação."""
        print("\n" + "=" * 70)
        print("📋 RELATÓRIO DE VERIFICAÇÃO PÓS-LIMPEZA")
        print("=" * 70)
        print(f"Gerado em: {datetime.now().isoformat()}")
        print()
        
        passed = sum(1 for r in self.results if r.status == "PASS")
        warnings = sum(1 for r in self.results if r.status == "WARNING")
        failed = sum(1 for r in self.results if r.status == "FAIL")
        
        print(f"Resultados: {passed} ✅ | {warnings} ⚠️  | {failed} ❌")
        print()
        
        for result in self.results:
            icon = "✅" if result.status == "PASS" else "⚠️" if result.status == "WARNING" else "❌"
            print(f"{icon} {result.check}: {result.status}")
            print(f"   {result.message}")
            if result.details and result.status != "PASS":
                for key, value in result.details.items():
                    print(f"   - {key}: {value}")
            print()
        
        print("=" * 70)
        
        if failed > 0:
            print("❌ FALHA: Problemas críticos encontrados!")
            print("   Ações necessárias antes de considerar a limpeza completa:")
            for result in self.results:
                if result.status == "FAIL":
                    print(f"   - {result.check}: {result.message}")
            return False
        elif warnings > 0:
            print("⚠️  ATENÇÃO: Problemas menores detectados")
            print("   Recomendado revisar os warnings antes de prosseguir")
            return True
        else:
            print("✅ SUCESSO: Toda a verificação passou!")
            print("   O catálogo está limpo e íntegro.")
            return True


async def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Verificação pós-limpeza do catálogo PickleIQ"
    )
    parser.add_argument(
        "--compare-with",
        help="Arquivo JSON do relatório pré-limpeza para comparação"
    )
    parser.add_argument(
        "--json-output",
        help="Salvar resultado em formato JSON"
    )
    
    args = parser.parse_args()
    
    verifier = PostCleanupVerifier(pre_cleanup_report=args.compare_with)
    await verifier.run_verification()
    
    success = verifier.print_report()
    
    if args.json_output:
        output = {
            "timestamp": datetime.now().isoformat(),
            "results": [
                {
                    "check": r.check,
                    "status": r.status,
                    "message": r.message,
                    "details": r.details
                }
                for r in verifier.results
            ]
        }
        with open(args.json_output, 'w') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"\n📄 Relatório JSON salvo em: {args.json_output}")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
