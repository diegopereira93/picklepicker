"""Utilitários compartilhados para normalização e validação de dados de raquetes."""

import re
import unicodedata

KNOWN_BRANDS: set[str] = {
    "selkirk", "joola", "franklin", "onomic", "engage", "paddletek",
    "prokennex", "babolat", "head", "yonex", "vulcan", "gearbox",
    "electrum", "diadem", "dropshot", "niupipo", "bsport", "eleven",
    "slk", "proton", "ronbus", "sixzero", "breadnbutters",
}


def normalize_paddle_name(name: str) -> str:
    if not name:
        return ""
    
    normalized = ''.join(
        c for c in unicodedata.normalize('NFD', name)
        if unicodedata.category(c) != 'Mn'
    )
    normalized = normalized.lower().strip()
    
    stop_words = {'raquete', 'raquetes', 'de', 'pickleball', 'para', 
                  'com', 'sem', 'the', 'and', 'or'}
    words = [w for w in normalized.split() if w not in stop_words]
    normalized = ' '.join(words)
    normalized = re.sub(r'[^a-z0-9\s-]', ' ', normalized)
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    return normalized


def validate_image_belongs_to_product(image_url: str, product_name: str) -> bool:
    """Valida se uma URL de imagem provavelmente pertence ao produto especificado.
    
    Retorna True se a imagem é provavelmente válida, False caso contrário.
    """
    if not image_url or not product_name:
        return False
    
    # URLs de imagem reais geralmente são mais longas que 60 caracteres
    if len(image_url) < 60:
        return False
    
    # Verifica extensões de imagem válidas
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.gif')
    url_lower = image_url.lower()
    if not any(url_lower.endswith(ext) for ext in valid_extensions):
        return False
    
    # Padrões que indicam imagens inválidas/genéricas
    invalid_patterns = [
        'placeholder', 'default', 'no-image', 'sem-imagem',
        'logo', 'marca', 'brand', 'watermark', 'banner',
        'promo', 'oferta', 'categoria'
    ]
    
    if any(pattern in url_lower for pattern in invalid_patterns):
        return False
    
    # Extrai palavras-chave do nome do produto (excluindo palavras comuns)
    skip_words = {'the', 'and', 'or', 'de', 'do', 'da', 'em', 'um', 'uma',
                  'raquete', 'pickleball', 'com', 'sem'}
    keywords = [
        w.lower() for w in product_name.split() 
        if w.lower() not in skip_words and len(w) > 2
    ]
    
    # Verifica se alguma palavra-chave do produto aparece na URL
    matching_keywords = [kw for kw in keywords if kw in url_lower]
    
    # Se encontrou palavras-chave, provavelmente é a imagem correta
    if matching_keywords:
        return True
    
    # Para URLs de CDN conhecidos sem palavras-chave, valida por domínio
    cdn_domains = [
        'mitiendanube.com', 'cloudfront.net', 'amazonaws.com',
        'dropshotbrasil.com.br', 'joola.com.br', 'shopify.com', 'shopifycdn.com', 'cdn.',
        'cdn.', 'images.', 'img.', 'products.', 'produtos.'
    ]
    is_known_cdn = any(domain in url_lower for domain in cdn_domains)
    
    return is_known_cdn


def extract_brand_from_name(name: str) -> str:
    """Extrai a marca do nome do produto usando lookup de marcas conhecidas.

    Primeiro verifica cada palavra contra KNOWN_BRANDS (case-insensitive).
    Se não encontrar, faz fallback para a primeira palavra após remover stop words.
    """
    if not name:
        return ""

    cleaned = re.sub(r'^(raquete[s]?\s+|de\s+|para\s+)', '', name, flags=re.IGNORECASE)
    words = cleaned.strip().split()

    # Check each word against known brands
    for word in words:
        normalized = re.sub(r'[^a-z]', '', word.lower())
        if normalized in KNOWN_BRANDS:
            return normalized.capitalize()

    # Fallback: first word after removing stop words
    stop_words = {"de", "para", "com", "sem", "the", "and", "or", "em", "um", "uma"}
    for word in words:
        w = word.lower().strip()
        if w not in stop_words and len(w) > 1:
            return w.capitalize()

    return words[0].capitalize() if words else ""
