#!/usr/bin/env python3
"""
Script de Backup dos Dados do Catálogo PickleIQ
Cria backups das tabelas principais antes da limpeza.

Uso:
    python scripts/catalog_cleanup/2_backup_data.py
    python scripts/catalog_cleanup/2_backup_data.py --schema-name pre_cleanup_20240115
"""

import asyncio
import json
import logging
import sys
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

sys.path.insert(0, "/home/diego/Documentos/picklepicker")
sys.path.insert(0, "/home/diego/Documentos/picklepicker/pipeline")

from pipeline.db.connection import get_connection


class CatalogBackup:
    """Gerenciador de backups do catálogo."""
    
    TABLES_TO_BACKUP = [
        "paddles",
        "price_snapshots",
        "paddle_specs",
        "paddle_embeddings",
        "review_queue",
        "retailers",
    ]
    
    def __init__(self, schema_name: str = None):
        self.schema_name = schema_name or f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.backup_stats = {}
    
    async def create_backup(self) -> dict:
        """Cria backup completo das tabelas."""
        logger.info(f"💾 Iniciando backup no schema: {self.schema_name}")
        
        async with get_connection() as conn:
            # Criar schema
            await conn.execute(f"CREATE SCHEMA IF NOT EXISTS {self.schema_name}")
            await conn.commit()
            
            for table in self.TABLES_TO_BACKUP:
                await self._backup_table(conn, table)
            
            # Backup dos metadados
            await self._backup_metadata(conn)
            
        logger.info(f"✅ Backup completo! Schema: {self.schema_name}")
        return self.backup_stats
    
    async def _backup_table(self, conn, table_name: str):
        """Faz backup de uma tabela específica."""
        logger.info(f"  📦 Fazendo backup da tabela: {table_name}")
        
        # Criar tabela de backup
        create_query = f"""
            CREATE TABLE {self.schema_name}.{table_name} AS
            SELECT * FROM {table_name}
        """
        await conn.execute(create_query)
        
        # Contar registros
        count_query = f"SELECT COUNT(*) FROM {self.schema_name}.{table_name}"
        row = await (await conn.execute(count_query)).fetchone()
        count = row[0] if row else 0
        
        self.backup_stats[table_name] = count
        logger.info(f"     ✅ {count} registros copiados")
    
    async def _backup_metadata(self, conn):
        """Backup dos metadados e estrutura."""
        logger.info("  📋 Salvando metadados...")
        
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "schema_name": self.schema_name,
            "tables_backed_up": self.TABLES_TO_BACKUP,
            "record_counts": self.backup_stats,
        }
        
        # Criar tabela de metadados
        await conn.execute(f"""
            CREATE TABLE {self.schema_name}._metadata (
                key TEXT PRIMARY KEY,
                value JSONB
            )
        """)
        
        await conn.execute(
            f"INSERT INTO {self.schema_name}._metadata (key, value) VALUES (%s, %s)",
            ("backup_info", json.dumps(metadata))
        )
        await conn.commit()
        
        logger.info("     ✅ Metadados salvos")
    
    async def verify_backup(self) -> bool:
        """Verifica integridade do backup."""
        logger.info("🔍 Verificando integridade do backup...")
        
        async with get_connection() as conn:
            for table in self.TABLES_TO_BACKUP:
                # Verificar se tabela existe
                check_query = f"""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_schema = %s AND table_name = %s
                    )
                """
                row = await (await conn.execute(check_query, (self.schema_name, table))).fetchone()
                
                if not row or not row[0]:
                    logger.error(f"   ❌ Tabela {table} não encontrada no backup!")
                    return False
                
                # Verificar se tem dados (se original tinha)
                orig_count = self.backup_stats.get(table, 0)
                if orig_count > 0:
                    count_query = f"SELECT COUNT(*) FROM {self.schema_name}.{table}"
                    row = await (await conn.execute(count_query)).fetchone()
                    backup_count = row[0] if row else 0
                    
                    if backup_count != orig_count:
                        logger.error(
                            f"   ❌ Contagem mismatch em {table}: "
                            f"original={orig_count}, backup={backup_count}"
                        )
                        return False
                
                logger.info(f"   ✅ {table}: OK")
        
        logger.info("✅ Backup verificado com sucesso!")
        return True
    
    async def list_backups(cls):
        """Lista todos os backups existentes."""
        async with get_connection() as conn:
            query = """
                SELECT schema_name
                FROM information_schema.schemata
                WHERE schema_name LIKE 'backup_%'
                ORDER BY schema_name DESC
            """
            result = await conn.execute(query)
            rows = await result.fetchall()
            return [row[0] for row in rows]


async def main():
    """Função principal."""
    import argparse
    import time
    
    parser = argparse.ArgumentParser(
        description="Backup dos dados do catálogo PickleIQ"
    )
    parser.add_argument(
        "--schema-name",
        help="Nome customizado para o schema de backup (default: backup_YYYYMMDD_HHMMSS)"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verificar backup após criar"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Listar backups existentes"
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Pular confirmação"
    )
    
    args = parser.parse_args()
    
    if args.list:
        backups = await CatalogBackup.list_backups()
        print("\n📦 Backups existentes:")
        for backup in backups:
            print(f"  - {backup}")
        return
    
    # Delay intencional para prevenir execução acidental
    if not args.yes:
        print("\n" + "=" * 70)
        print("⏳ Criando backup em 2 segundos...")
        print("   Pressione CTRL+C para cancelar")
        print("=" * 70)
        time.sleep(2)
    
    # Criar backup
    backup = CatalogBackup(schema_name=args.schema_name)
    stats = await backup.create_backup()
    
    print("\n" + "=" * 70)
    print("📊 RESUMO DO BACKUP")
    print("=" * 70)
    print(f"Schema: {backup.schema_name}")
    print()
    for table, count in stats.items():
        print(f"  {table:30s}: {count:>8} registros")
    print()
    
    if args.verify:
        success = await backup.verify_backup()
        if not success:
            logger.error("❌ Falha na verificação do backup!")
            sys.exit(1)
    
    print("=" * 70)
    print("✅ Backup concluído com sucesso!")
    print("=" * 70)
    print()
    print("Para restaurar o backup, execute:")
    print(f"  psql $DATABASE_URL -c \"\i restore_{backup.schema_name}.sql\"")


if __name__ == "__main__":
    asyncio.run(main())
