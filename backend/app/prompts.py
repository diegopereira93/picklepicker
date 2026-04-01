"""Prompt engineering for paddle recommendation chatbot."""

from typing import Dict, Optional
from app.schemas import SpecsResponse


SYSTEM_PROMPT = """
Você é um especialista em raquetes de pickleball brasileiro.
Recomende as 3 melhores raquetes com base no perfil do usuário.

Para cada recomendação:
- Nome e marca da raquete
- 2-3 razões por que é perfeita para o usuário
- Preço em BRL e onde comprar (link de afiliado)

Seja conciso, conversacional e em português brasileiro.
"""

PADDLE_ENRICHMENT_PROMPT = """
Extraia informações estruturadas sobre a raquete de pickleball a partir do texto fornecido.

Retorne um JSON com os seguintes campos:

{
  "skill_level": "beginner|intermediate|advanced|null",
  "specs": {
    "swingweight": 100,
    "twistweight": 7,
    "weight_oz": 7.8,
    "core_thickness_mm": 16,
    "face_material": "carbon fiber"
  },
  "in_stock": true
}

Instruções de extração:

1. skill_level — Classifique o nível de habilidade:
   - 'beginner': raquetes para iniciantes, controle, fácil de usar
   - 'intermediate': raquetes intermediárias, versáteis, equilíbrio
   - 'advanced': raquetes avançadas, potência, profissionais
   - null: se não houver indicação clara

2. specs — Extraia especificações técnicas:
   - swingweight: inteiro (100-120 range)
   - twistweight: inteiro (6-10 range)
   - weight_oz: float (7.5-8.5 oz)
   - core_thickness_mm: float (14mm, 16mm)
   - face_material: string ("carbon fiber", "fiberglass", "graphite")

3. in_stock — Booleano baseado em indicadores de disponibilidade:
   - true: "em estoque", "disponível", "pronta entrega"
   - false: "fora de estoque", "esgotado", "pré-venda"
   - null: se não houver indicação

Seja conservador — retorne null quando não houver dados claros.
"""


def translate_metrics(specs: Optional[SpecsResponse]) -> Dict[str, str]:
    """
    Translate technical specs to plain Portuguese descriptions.

    Args:
        specs: SpecsResponse with swingweight, twistweight, weight_oz, core_thickness_mm, face_material

    Returns:
        Dict with Portuguese keys and user-friendly descriptions
    """
    if not specs:
        return {
            "peso_balanceado": "Dado não disponível",
            "torcao": "Dado não disponível",
            "peso_total": "Dado não disponível",
            "nucleoInterno": "Dado não disponível",
            "facePrincipal": "Dado não disponível",
        }

    result = {}

    # Swingweight translation
    if specs.swingweight is not None:
        sw = specs.swingweight
        if sw < 100:
            explanation = "Leve — ótima para velocidade e manobras rápidas"
        elif sw < 115:
            explanation = "Média — bom equilíbrio entre controle e potência"
        else:
            explanation = "Pesada — máxima potência, exige mais força"
        result["peso_balanceado"] = f"Média ({sw} pontos) — {explanation}"
    else:
        result["peso_balanceado"] = "Dado não disponível"

    # Twistweight translation
    if specs.twistweight is not None:
        tw = specs.twistweight
        if tw < 5.5:
            explanation = "Muito baixa — máxima estabilidade"
        elif tw < 7.0:
            explanation = "Baixa — menos vibração, mais precisão"
        else:
            explanation = "Alta — maior potência mas mais vibração"
        result["torcao"] = f"Torcão ({tw}) — {explanation}"
    else:
        result["torcao"] = "Dado não disponível"

    # Weight in grams
    if specs.weight_oz is not None:
        weight_g = round(specs.weight_oz * 28.35)  # Convert oz to grams
        result["peso_total"] = f"{weight_g}g — confortável para longas sessões"
    else:
        result["peso_total"] = "Dado não disponível"

    # Core thickness translation (approximated performance characteristic)
    if specs.core_thickness_mm is not None:
        ct = specs.core_thickness_mm
        if ct < 13:
            result["nucleoInterno"] = f"Núcleo fino ({ct}mm) — leve e responsivo"
        elif ct < 16:
            result["nucleoInterno"] = f"Núcleo médio ({ct}mm) — equilíbrio ideal"
        else:
            result["nucleoInterno"] = f"Núcleo espesso ({ct}mm) — máxima potência"
    else:
        result["nucleoInterno"] = "Dado não disponível"

    # Face material
    if specs.face_material:
        face_translation = {
            "fiberglass": "Fibra de vidro — durabilidade alta",
            "graphite": "Grafite — leve e rígido",
            "carbon": "Carbono — máxima potência",
        }
        result["facePrincipal"] = face_translation.get(specs.face_material.lower(), f"{specs.face_material} — material especializado")
    else:
        result["facePrincipal"] = "Dado não disponível"

    return result
