#!/usr/bin/env python3
"""
Script de Limpeza do Catálogo PickleIQ
Remove dados órfãos, duplicatas e inconsistências do catálogo.

⚠️  ATENÇÃO: Execute apenas após fazer backup com 2_backup_data.py

Uso:
    python scripts/catalog_cleanup/3_cleanup_catalog.py --dry-run
    python scripts/catalog_cleanup/3_cleanup_catalog.py --execute --yes

Segurança:
    - Sempre execute --dry-run primeiro
    - Em produção, requer confirmação explícita (a menos que --yes)
    - Verifica permissões do usuário antes de operações destrutivas
"""

import asyncio
import json
import logging
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

sys.path.insert(0, "/home/diego/Documentos/picklepicker")
sys.path.insert(0, "/home/diego/Documentos/picklepicker/pipeline")

from pipeline.db.connection import get_connection
from pipeline.dedup.spec_matcher import fuzzy_match_paddles
from pipeline.dedup.review_queue import add_to_review_queue


def is_production_environment() -> bool:
    """Detecta se está rodando em ambiente de produção."""
    # Verificar variável de ambiente
    env = os.getenv("PICKLEIQ_ENV", "").lower()
    if env in ["prod", "production"]:
        return True
    
    # Verificar hostname (heurística comum)
    hostname = os.getenv("HOSTNAME", os.getenv("COMPUTERNAME", "")).lower()
    if any(x in hostname for x in ["prod", "production", "pickleiq"]):
        return True
    
    # Verificar DATABASE_URL
    db_url = os.getenv("DATABASE_URL", "")
    if "amazonaws.com" in db_url or "supabase.co" in db_url:
        return True
    
    return False


async def check_user_permissions(conn) -> bool:
    """Verifica se o usuário tem permissões para operações destrutivas."""
    try:
        # Verificar se usuário pode executar DELETE
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT pg_has_role(current_user, 'pg_write_all_data', 'MEMBER')
                OR EXISTS (
                    SELECT 1 FROM information_schema.table_privileges
                    WHERE grantee = current_user
                    AND privilege_type = 'DELETE'
                    AND table_name = 'paddle_embeddings'
                )
            """)
            row = await cur.fetchone()
            return row[0] if row else False
    except Exception as e:
        logger.warning(f"Não foi possível verificar permissões: {e}")
        # Em caso de erro na verificação, assumir que não tem permissão em produção
        return False


def confirm_destructive_action(is_production: bool, yes_flag: bool) -> bool:
    """Solicita confirmação explícita para ações destrutivas."""
    if yes_flag:
        logger.info("Flag --yes detectada, pulando confirmação interativa")
        return True
    
    if is_production:
        print("\n" + "=" * 70)
        print("⚠️  MODO PRODUÇÃO DETECTADO")
        print("=" * 70)
        print("\nVocê está prestes a executar operações DELETRUTIVAS no banco de produção.")
        print("Isso inclui DELETAR registros e ALTERAR dados.\n")
        
        confirmation = input("Para confirmar, digite 'CONFIRMA-PROD': ")
        return confirmation == "CONFIRMA-PROD"
    else:
        print("\n" + "=" * 70)
        print("⚠️  Modo não-produção detectado")
        print("=" * 70)
        print("\nContinuar com a limpeza? (sim/não): ", end="")
        response = input().lower().strip()
        return response in ["sim", "s", "yes", "y"]


def log_operation(operation: str, details: dict):
    """Registra operação em arquivo de log para auditoria."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "details": details,
        "user": os.getenv("USER", "unknown"),
        "env": os.getenv("PICKLEIQ_ENV", "unknown")
    }
    
    log_file = "/home/diego/Documentos/picklepicker/scripts/catalog_cleanup/logs/cleanup_operations.log"
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


@dataclass
class CleanupResult:
    """Resultado da operação de limpeza."""
    step: str
    records_found: int
    records_affected: int
    details: List[str]


class CatalogCleaner:
    """Executor de limpeza do catálogo."""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.results: List[CleanupResult] = []
        self.mode = "SIMULAÇÃO (dry-run)" if dry_run else "EXECUÇÃO REAL"
    
    async def run_cleanup(self) -> List[CleanupResult]:
        """Executa limpeza completa do catálogo."""
        logger.info(f"🧹 Iniciando limpeza do catálogo - {self.mode}")
        
        if not self.dry_run:
            logger.warning("⚠️  MODO EXECUÇÃO REAL - Alterações serão persistidas!")
        
        # Ordem importante: órfãos -> duplicatas -> stale -> qualidade
        await self._clean_orphan_embeddings()
        await self._clean_orphan_specs()
        await self._clean_stale_snapshots(days=90)
        await self._find_duplicate_paddles()
        await self._flag_stale_paddles(days=30)
        await self._flag_broken_images()
        
        # Rebuild materialized view
        if not self.dry_run:
            await self._refresh_materialized_view()
        
        return self.results
    
    async def _clean_orphan_embeddings(self):
        """Remove embeddings sem paddle correspondente."""
        logger.info("🗑️  Verificando embeddings órfãos...")
        
        async with get_connection() as conn:
            query = """
                SELECT pe.id, pe.paddle_id
                FROM paddle_embeddings pe
                LEFT JOIN paddles p ON p.id = pe.paddle_id
                WHERE p.id IS NULL
            """
            rows = await (await conn.execute(query)).fetchall()
            
            result = CleanupResult(
                step="Embeddings órfãos",
                records_found=len(rows),
                records_affected=0,
                details=[f"paddle_id={r[1]}" for r in rows[:10]]
            )
            
            if not self.dry_run and rows:
                delete_query = """
                    DELETE FROM paddle_embeddings
                    WHERE paddle_id NOT IN (SELECT id FROM paddles)
                """
                await conn.execute(delete_query)
                await conn.commit()
                result.records_affected = len(rows)
                logger.info(f"   ✅ {len(rows)} embeddings órfãos removidos")
            
            self.results.append(result)
    
    async def _clean_orphan_specs(self):
        """Remove specs sem paddle correspondente."""
        logger.info("🗑️  Verificando specs órfãos...")
        
        async with get_connection() as conn:
            query = """
                SELECT ps.id, ps.paddle_id
                FROM paddle_specs ps
                LEFT JOIN paddles p ON p.id = ps.paddle_id
                WHERE p.id IS NULL
            """
            rows = await (await conn.execute(query)).fetchall()
            
            result = CleanupResult(
                step="Specs órfãos",
                records_found=len(rows),
                records_affected=0,
                details=[f"paddle_id={r[1]}" for r in rows[:10]]
            )
            
            if not self.dry_run and rows:
                delete_query = """
                    DELETE FROM paddle_specs
                    WHERE paddle_id NOT IN (SELECT id FROM paddles)
                """
                await conn.execute(delete_query)
                await conn.commit()
                result.records_affected = len(rows)
                logger.info(f"   ✅ {len(rows)} specs órfãos removidos")
            
            self.results.append(result)
    
    async def _clean_stale_snapshots(self, days: int = 90):
        """Arquiva snapshots antigos (mantém apenas os mais recentes por paddle/retailer)."""
        logger.info(f"🗑️  Verificando snapshots > {days} dias...")
        
        async with get_connection() as conn:
            # Encontrar snapshots antigos que não são o mais recente
            query = f"""
                SELECT ps.id, ps.paddle_id, ps.retailer_id, ps.scraped_at
                FROM price_snapshots ps
                WHERE ps.scraped_at < NOW() - INTERVAL '{days} days'
                AND ps.id NOT IN (
                    SELECT DISTINCT ON (paddle_id, retailer_id) id
                    FROM price_snapshots
                    ORDER BY paddle_id, retailer_id, scraped_at DESC
                )
            """
            rows = await (await conn.execute(query)).fetchall()
            
            result = CleanupResult(
                step=f"Snapshots > {days} dias (não recentes)",
                records_found=len(rows),
                records_affected=0,
                details=[f"id={r[0]}, paddle_id={r[1]}, scraped_at={r[3]}" for r in rows[:5]]
            )
            
            if not self.dry_run and rows:
                # Em vez de deletar, marcar como arquivado
                archive_query = f"""
                    UPDATE price_snapshots
                    SET source_raw = source_raw || '{{"archived": true, "archived_at": "{datetime.now().isoformat()}"}}'::jsonb
                    WHERE id IN (
                        SELECT ps.id
                        FROM price_snapshots ps
                        WHERE ps.scraped_at < NOW() - INTERVAL '{days} days'
                        AND ps.id NOT IN (
                            SELECT DISTINCT ON (paddle_id, retailer_id) id
                            FROM price_snapshots
                            ORDER BY paddle_id, retailer_id, scraped_at DESC
                        )
                    )
                """
                await conn.execute(archive_query)
                await conn.commit()
                result.records_affected = len(rows)
                logger.info(f"   ✅ {len(rows)} snapshots arquivados")
            
            self.results.append(result)
    
    async def _find_duplicate_paddles(self):
        """Identifica possíveis duplicatas por nome similar."""
        logger.info("🔍 Buscando duplicatas por nome...")
        
        async with get_connection() as conn:
            # Pegar todos os nomes de paddles
            query = "SELECT id, name FROM paddles ORDER BY name"
            rows = await (await conn.execute(query)).fetchall()
            
            duplicates_found = []
            checked = set()
            
            for paddle_id, name in rows:
                if paddle_id in checked:
                    continue
                
                # Buscar matches fuzzy
                match_id, score = await fuzzy_match_paddles(name, threshold=0.85)
                
                if match_id and match_id != paddle_id and match_id not in checked:
                    duplicates_found.append({
                        "paddle_id_1": paddle_id,
                        "paddle_id_2": match_id,
                        "name": name,
                        "score": score
                    })
                    checked.add(paddle_id)
                    checked.add(match_id)
            
            result = CleanupResult(
                step="Paddles duplicados (fuzzy match > 0.85)",
                records_found=len(duplicates_found),
                records_affected=0,
                details=[f"{d['name']} (score: {d['score']:.2f})" for d in duplicates_found[:10]]
            )
            
            if not self.dry_run and duplicates_found:
                for dup in duplicates_found:
                    await add_to_review_queue(
                        queue_type="duplicate",
                        paddle_id=dup["paddle_id_1"],
                        related_paddle_id=dup["paddle_id_2"],
                        data={"match_score": dup["score"], "fuzzy_match": True}
                    )
                result.records_affected = len(duplicates_found)
                logger.info(f"   ✅ {len(duplicates_found)} duplicatas adicionadas à review queue")
            
            self.results.append(result)
    
    async def _flag_stale_paddles(self, days: int = 30):
        """Marca paddles sem atualização recente."""
        logger.info(f"🏴 Verificando paddles sem atualização > {days} dias...")
        
        async with get_connection() as conn:
            query = f"""
                SELECT p.id, p.name, MAX(ps.scraped_at) as last_scraped
                FROM paddles p
                LEFT JOIN price_snapshots ps ON ps.paddle_id = p.id
                GROUP BY p.id, p.name
                HAVING MAX(ps.scraped_at) < NOW() - INTERVAL '{days} days'
                   OR MAX(ps.scraped_at) IS NULL
            """
            rows = await (await conn.execute(query)).fetchall()
            
            result = CleanupResult(
                step=f"Paddles stale > {days} dias",
                records_found=len(rows),
                records_affected=0,
                details=[f"{r[1]} (last: {r[2] or 'N/A'})" for r in rows[:10]]
            )
            
            if not self.dry_run and rows:
                update_query = """
                    UPDATE paddles
                    SET needs_reembed = TRUE
                    WHERE id IN (
                        SELECT p.id
                        FROM paddles p
                        LEFT JOIN price_snapshots ps ON ps.paddle_id = p.id
                        GROUP BY p.id
                        HAVING MAX(ps.scraped_at) < NOW() - INTERVAL '30 days'
                           OR MAX(ps.scraped_at) IS NULL
                    )
                """
                await conn.execute(update_query)
                await conn.commit()
                result.records_affected = len(rows)
                logger.info(f"   ✅ {len(rows)} paddles marcados para re-scrape")
            
            self.results.append(result)
    
    async def _flag_broken_images(self):
        """Marca paddles com imagens que podem estar quebradas."""
        logger.info("🖼️  Verificando imagens suspeitas...")
        
        async with get_connection() as conn:
            # Paddles com placeholder ou URLs suspeitas
            query = """
                SELECT id, name, image_url
                FROM paddles
                WHERE image_url IS NULL
                   OR image_url = ''
                   OR image_url LIKE '%placeholder%'
                   OR image_url LIKE '%default%'
                   OR image_url LIKE '%no-image%'
                   OR LENGTH(image_url) < 60
            """
            rows = await (await conn.execute(query)).fetchall()
            
            result = CleanupResult(
                step="Imagens suspeitas/quebradas",
                records_found=len(rows),
                records_affected=0,
                details=[f"{r[1]}: {r[2][:50] if r[2] else 'N/A'}" for r in rows[:10]]
            )
            
            if not self.dry_run and rows:
                for row in rows:
                    paddle_id, name, image_url = row
                    await add_to_review_queue(
                        queue_type="spec_unmatched",
                        paddle_id=paddle_id,
                        data={"issue": "broken_or_missing_image", "current_url": image_url}
                    )
                result.records_affected = len(rows)
                logger.info(f"   ✅ {len(rows)} paddles com imagens suspeitas adicionados à review queue")
            
            self.results.append(result)
    
    async def _refresh_materialized_view(self):
        """Atualiza materialized view de preços."""
        logger.info("🔄 Atualizando materialized view...")
        
        async with get_connection() as conn:
            await conn.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY latest_prices")
            await conn.commit()
            logger.info("   ✅ latest_prices atualizado")
    
    def print_report(self):
        """Imprime relatório da limpeza."""
        print("\n" + "=" * 70)
        print(f"📊 RELATÓRIO DE LIMPEZA - {self.mode}")
        print("=" * 70)
        print()
        
        total_found = 0
        total_affected = 0
        
        for result in self.results:
            print(f"📋 {result.step}")
            print(f"   Encontrados:  {result.records_found}")
            if not self.dry_run:
                print(f"   Afetados:     {result.records_affected}")
            
            if result.details:
                print("   Exemplos:")
                for detail in result.details[:5]:
                    print(f"     - {detail}")
            print()
            
            total_found += result.records_found
            total_affected += result.records_affected
        
        print("=" * 70)
        print(f"TOTAL: {len(self.results)} operações")
        print(f"       {total_found} registros encontrados")
        if not self.dry_run:
            print(f"       {total_affected} registros afetados")
        print("=" * 70)
        print()
        
        if self.dry_run:
            print("💡 Para executar as alterações, rode com: --execute")
        else:
            print("✅ Limpeza concluída!")


async def main():
    """Função principal com verificações de segurança."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Limpeza do catálogo PickleIQ"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Simular sem alterar dados (default: True)"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Executar alterações reais (cuidado!)"
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Pular confirmação interativa (uso em CI)"
    )
    
    args = parser.parse_args()
    
    dry_run = not args.execute
    is_production = is_production_environment()
    
    # Delay intencional para prevenir execução acidental
    if args.execute:
        print("\n" + "=" * 70)
        print("⏳ Iniciando em 3 segundos...")
        print("   Pressione CTRL+C para cancelar")
        print("=" * 70)
        time.sleep(3)
    
    # Verificar ambiente
    if args.execute and is_production and not args.yes:
        print(f"\n🚨 PRODUÇÃO DETECTADA: {os.getenv('DATABASE_URL', 'DB_URL')[:50]}...")
        print("   Aguardando confirmação...\n")
    
    # Verificar permissões apenas em modo execução real
    if args.execute:
        async with get_connection() as conn:
            if not await check_user_permissions(conn):
                logger.error("❌ Usuário não tem permissões para operações destrutivas")
                print("\nERRO: Você não tem permissões suficientes.")
                print("Execute como usuário com privilégios adequados ou use --dry-run")
                sys.exit(1)
            logger.info("✅ Permissões verificadas")
    
    # Solicitar confirmação para execução real
    if args.execute and not dry_run:
        if not confirm_destructive_action(is_production, args.yes):
            print("\n❌ Execução cancelada pelo usuário")
            sys.exit(0)
    
    # Log da operação
    if args.execute:
        log_operation("cleanup_started", {
            "mode": "execute" if args.execute else "dry_run",
            "is_production": is_production,
            "yes_flag": args.yes
        })
    
    # Executar limpeza
    cleaner = CatalogCleaner(dry_run=dry_run)
    await cleaner.run_cleanup()
    cleaner.print_report()
    
    # Log do resultado
    if args.execute:
        total_affected = sum(r.records_affected for r in cleaner.results)
        log_operation("cleanup_completed", {
            "records_affected": total_affected,
            "operations": len(cleaner.results)
        })


if __name__ == "__main__":
    asyncio.run(main())
