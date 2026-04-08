"""Script de migração para corrigir mismatch de imagens em dados existentes."""

import asyncio
import logging
from pipeline.db.connection import get_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def migrate_existing_data():
    """Executa migração para limpar dados existentes com mismatch."""
    async with get_connection() as conn:
        logger.info("Iniciando migração de dados existentes...")
        
        # Conta registros antes
        result = await conn.execute("SELECT COUNT(*) FROM paddles")
        total_before = (await result.fetchone())[0]
        
        result = await conn.execute(
            "SELECT COUNT(*) FROM paddles WHERE image_url IS NULL OR image_url = ''"
        )
        sem_imagem_before = (await result.fetchone())[0]
        
        logger.info(f"Total de raquetes: {total_before}")
        logger.info(f"Sem imagem: {sem_imagem_before}")
        
        # Remove imagens inválidas
        await conn.execute("""
            UPDATE paddles 
            SET image_url = NULL
            WHERE image_url IS NOT NULL 
            AND (
                image_url ~* 'placeholder|default|no-image|sem-imagem|logo|marca|brand|watermark|banner|promo|oferta|categoria'
                OR length(image_url) < 60
                OR image_url !~* '\\.(jpg|jpeg|png|webp|gif)$'
            )
        """)
        
        # Atualiza timestamps para forçar re-scrape
        await conn.execute("""
            UPDATE paddles 
            SET updated_at = NOW()
            WHERE image_url IS NULL OR image_url = ''
        """)
        
        await conn.commit()
        
        # Conta registros depois
        result = await conn.execute(
            "SELECT COUNT(*) FROM paddles WHERE image_url IS NULL OR image_url = ''"
        )
        sem_imagem_after = (await result.fetchone())[0]
        
        logger.info(f"Migração concluída!")
        logger.info(f"Raquetes sem imagem válida: {sem_imagem_after}")
        logger.info(f"Estas raquetes serão re-scraped na próxima execução dos crawlers")


if __name__ == "__main__":
    asyncio.run(migrate_existing_data())
