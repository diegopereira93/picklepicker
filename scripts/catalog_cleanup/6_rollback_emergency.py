#!/usr/bin/env python3
"""
Script de Rollback de Emergência - PickleIQ Catalog Cleanup
Restaura dados do backup em caso de problemas após limpeza.

⚠️  ATENÇÃO: Use apenas em emergências!

Uso:
    python scripts/catalog_cleanup/rollback_emergency.py --list
    python scripts/catalog_cleanup/rollback_emergency.py --backup backup_20240409_143052
"""

import asyncio
import sys
import time
from datetime import datetime

sys.path.insert(0, "/home/diego/Documentos/picklepicker")
sys.path.insert(0, "/home/diego/Documentos/picklepicker/pipeline")

from pipeline.db.connection import get_connection


async def list_backups():
    """Lista backups disponíveis."""
    async with get_connection() as conn:
        query = """
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name LIKE 'backup_%'
            ORDER BY schema_name DESC
        """
        rows = await (await conn.execute(query)).fetchall()
        
        print("\n📦 Backups disponíveis:")
        print("-" * 70)
        for row in rows:
            schema = row[0]
            # Contar tabelas no backup
            count_query = """
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_schema = %s
            """
            count_row = await (await conn.execute(count_query, (schema,))).fetchone()
            print(f"  - {schema} ({count_row[0] if count_row else 0} tabelas)")
        print()
        return [r[0] for r in rows]


async def verify_backup_integrity(backup_schema: str) -> bool:
    """Verifica se backup tem todas as tabelas necessárias."""
    required_tables = ['paddles', 'price_snapshots', 'paddle_specs', 
                      'paddle_embeddings', 'review_queue']
    
    async with get_connection() as conn:
        for table in required_tables:
            query = """
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables
                    WHERE table_schema = %s AND table_name = %s
                )
            """
            row = await (await conn.execute(query, (backup_schema, table))).fetchone()
            if not row or not row[0]:
                print(f"❌ Tabela {table} não encontrada no backup {backup_schema}")
                return False
    
    return True


async def rollback_table(conn, table: str, backup_schema: str, dry_run: bool = True):
    """Restaura uma tabela do backup."""
    print(f"  🔄 Restaurando {table}...")
    
    if dry_run:
        # Apenas contar registros
        query = f"SELECT COUNT(*) FROM {backup_schema}.{table}"
        row = await (await conn.execute(query)).fetchone()
        count = row[0] if row else 0
        print(f"     (dry-run) Restauraria {count} registros")
        return count
    
    # Limpar tabela atual e restaurar do backup
    try:
        # Usar TRUNCATE CASCADE para limpar dependências
        await conn.execute(f"TRUNCATE {table} CASCADE")
        
        # Inserir dados do backup
        await conn.execute(f"""
            INSERT INTO {table}
            SELECT * FROM {backup_schema}.{table}
        """)
        
        # Contar registros restaurados
        query = f"SELECT COUNT(*) FROM {table}"
        row = await (await conn.execute(query)).fetchone()
        count = row[0] if row else 0
        
        print(f"     ✅ {count} registros restaurados")
        return count
    except Exception as e:
        print(f"     ❌ Erro ao restaurar {table}: {e}")
        raise


async def perform_rollback(backup_schema: str, dry_run: bool = True, force: bool = False):
    """Executa rollback de todas as tabelas."""
    
    if not dry_run and not force:
        print("\n" + "=" * 70)
        print("⚠️  ROLLBACK DE EMERGÊNCIA")
        print("=" * 70)
        print(f"\nIsso irá SUBSTITUIR todos os dados atuais pelo backup: {backup_schema}")
        print("⚠️  TODAS AS ALTERAÇÕES DESDE O BACKUP SERÃO PERDIDAS!")
        print("\nPara confirmar, digite 'FAZER-ROLLBACK': ", end="")
        
        confirmation = input().strip()
        if confirmation != "FAZER-ROLLBACK":
            print("\n❌ Rollback cancelado")
            return False
    
    print(f"\n{'🧪 SIMULAÇÃO' if dry_run else '⚡ EXECUÇÃO'} de rollback:")
    print("-" * 70)
    
    # Ordem é crítica: dependências primeiro
    tables_order = [
        'retailers',        # Referenciado por price_snapshots
        'paddles',          # Referenciado por todas as outras
        'price_snapshots',  # Depende de paddles e retailers
        'paddle_specs',     # Depende de paddles
        'paddle_embeddings', # Depende de paddles
        'review_queue',     # Depende de paddles
    ]
    
    async with get_connection() as conn:
        try:
            total_restored = 0
            
            for table in tables_order:
                count = await rollback_table(conn, table, backup_schema, dry_run)
                total_restored += count
            
            if not dry_run:
                await conn.commit()
                print(f"\n✅ Rollback concluído! {total_restored} registros restaurados")
                
                # Registrar rollback
                await conn.execute("""
                    INSERT INTO review_queue (type, data, status, created_at)
                    VALUES ('rollback_emergency', %s, 'resolved', NOW())
                """, ({"backup_schema": backup_schema, "records_restored": total_restored},))
                await conn.commit()
            else:
                print(f"\n💡 Simulação: {total_restored} registros seriam restaurados")
                print("   Execute sem --dry-run para executar o rollback")
            
            return True
            
        except Exception as e:
            if not dry_run:
                await conn.rollback()
            print(f"\n❌ ERRO DURANTE ROLLBACK: {e}")
            print("   O banco pode estar em estado inconsistente!")
            print("   Entre em contato com o DBA imediatamente.")
            raise


async def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Rollback de emergência do catálogo PickleIQ"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Listar backups disponíveis"
    )
    parser.add_argument(
        "--backup",
        help="Schema de backup para restaurar (ex: backup_20240409_143052)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simular rollback sem alterar dados"
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Pular confirmação (uso em CI/automação)"
    )
    
    args = parser.parse_args()
    
    if args.list:
        await list_backups()
        return
    
    if not args.backup:
        print("❌ Especifique o backup com --backup ou liste com --list")
        sys.exit(1)
    
    # Verificar se backup existe
    print(f"🔍 Verificando backup: {args.backup}")
    
    if not await verify_backup_integrity(args.backup):
        print("❌ Backup inválido ou incompleto!")
        sys.exit(1)
    
    print("✅ Backup verificado")
    
    # Delay de segurança
    if not args.yes:
        print("\n⏳ Iniciando em 5 segundos... Pressione CTRL+C para cancelar")
        time.sleep(5)
    
    # Executar rollback
    try:
        success = await perform_rollback(
            args.backup, 
            dry_run=args.dry_run, 
            force=args.yes
        )
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Falha crítica: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
