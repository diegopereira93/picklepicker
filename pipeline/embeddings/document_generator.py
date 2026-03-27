"""Document generator for paddle specifications to narrative text."""

import logging

logger = logging.getLogger(__name__)


def swingweight_to_description(swingweight: float) -> str:
    """Convert swingweight to description."""
    if swingweight < 80:
        return "Leve e ágil"
    elif swingweight < 105:
        return "Equilibrado"
    else:
        return "Pesado para potência"


def swingweight_to_style(swingweight: float) -> str:
    """Convert swingweight to recommended style."""
    if swingweight < 80:
        return "jogadores que priorizam velocidade e controle"
    elif swingweight < 105:
        return "jogadores que buscam equilíbrio entre controle e potência"
    else:
        return "jogadores que buscam máxima potência"


def twistweight_to_description(twistweight: float) -> str:
    """Convert twistweight to description."""
    if twistweight < 80:
        return "Precisão alta"
    elif twistweight < 110:
        return "Equilibrado"
    else:
        return "Maior tolerância a off-center hits"


def twistweight_to_skill(twistweight: float) -> str:
    """Convert twistweight to skill recommendation."""
    if twistweight < 80:
        return "ideal para jogadores avançados"
    elif twistweight < 110:
        return "bom para intermediários a avançados"
    else:
        return "tolerante para todos os níveis"


def core_to_description(core_mm: float) -> str:
    """Convert core thickness to feel description."""
    if core_mm < 11:
        return "resposta viva e rápida"
    elif core_mm < 13:
        return "equilíbrio entre resposta e controle"
    else:
        return "absorção de vibração e controle superior"


def generate_paddle_document(paddle: dict) -> str:
    """
    Generate a 200-400 token narrative document from paddle specs.

    Args:
        paddle: dict with keys: name, brand, retailer, price_min, and specs dict
                (swingweight, twistweight, weight_oz, core_thickness_mm, face_material)

    Returns:
        Narrative string suitable for embedding
    """
    name = paddle.get("name", "Unknown")
    brand = paddle.get("brand", "Unknown")
    retailer = paddle.get("retailer", "Unknown")
    price_min = paddle.get("price_min", 0)

    specs = paddle.get("specs", {}) or {}
    swingweight = specs.get("swingweight")
    twistweight = specs.get("twistweight")
    weight_oz = specs.get("weight_oz")
    core_thickness_mm = specs.get("core_thickness_mm")
    face_material = specs.get("face_material", "Composição desconhecida")

    # Build narrative
    doc = f"{brand} {name} raquete de pickleball.\n\n"
    doc += "Especificações:\n"

    if weight_oz:
        doc += f"- Peso: {weight_oz} oz\n"

    if swingweight:
        doc += f"- Swingweight: {swingweight}\n"

    if twistweight:
        doc += f"- Twistweight: {twistweight}\n"

    if core_thickness_mm:
        doc += f"- Espessura do núcleo: {core_thickness_mm}mm\n"

    doc += f"- Material da face: {face_material}\n\n"

    doc += "Perfil de desempenho:\n"

    if swingweight:
        doc += f"{swingweight_to_description(swingweight)} — ideal para {swingweight_to_style(swingweight)}\n"

    if twistweight:
        doc += f"{twistweight_to_description(twistweight)} — {twistweight_to_skill(twistweight)}\n"

    if core_thickness_mm:
        doc += f"Núcleo {core_thickness_mm}mm oferece {core_to_description(core_thickness_mm)}\n\n"

    doc += f"Disponível em {retailer} a partir de R$ {price_min:.2f}"

    return doc
