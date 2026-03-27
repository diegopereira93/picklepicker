"""Tests for prompt engineering and metric translation."""

import pytest
from backend.app.prompts import SYSTEM_PROMPT, translate_metrics
from backend.app.schemas import SpecsResponse


def test_system_prompt__contains_portuguese():
    """Verify system prompt is in Portuguese."""
    assert "Você é um especialista" in SYSTEM_PROMPT
    assert "português brasileiro" in SYSTEM_PROMPT
    assert "raquetes" in SYSTEM_PROMPT


def test_translate_metrics__all_fields_present():
    """Verify all 5 metric fields are translated."""
    specs = SpecsResponse(
        swingweight=115,
        twistweight=7.2,
        weight_oz=8.3,
        core_thickness_mm=14.0,
        face_material="fiberglass"
    )
    result = translate_metrics(specs)

    assert "peso_balanceado" in result
    assert "torcao" in result
    assert "peso_total" in result
    assert "nucleoInterno" in result
    assert "facePrincipal" in result


def test_translate_metrics__missing_specs():
    """Handle NULL specs gracefully."""
    result = translate_metrics(None)

    assert result["peso_balanceado"] == "Dado não disponível"
    assert result["torcao"] == "Dado não disponível"
    assert result["peso_total"] == "Dado não disponível"
    assert result["nucleoInterno"] == "Dado não disponível"
    assert result["facePrincipal"] == "Dado não disponível"


def test_translate_metrics__output_portuguese():
    """All output text is in Portuguese."""
    specs = SpecsResponse(
        swingweight=95,
        twistweight=4.5,
        weight_oz=7.0,
        core_thickness_mm=13.5,
        face_material="carbon"
    )
    result = translate_metrics(specs)

    # Check for Portuguese words
    full_text = " ".join(result.values())
    assert "toque" in full_text or "controle" in full_text or "potência" in full_text or "leve" in full_text
    assert "Dado não disponível" not in full_text  # All should be populated


def test_metric_ranges__swingweight_explanation_matches():
    """Swingweight explanation matches value."""
    # Light swingweight (< 100)
    specs_light = SpecsResponse(
        swingweight=95,
        twistweight=5.0,
        weight_oz=7.5,
        core_thickness_mm=13.0,
        face_material="graphite"
    )
    result_light = translate_metrics(specs_light)
    assert "velocidade" in result_light["peso_balanceado"].lower()

    # Medium swingweight (100-115)
    specs_medium = SpecsResponse(
        swingweight=110,
        twistweight=5.0,
        weight_oz=8.0,
        core_thickness_mm=14.0,
        face_material="graphite"
    )
    result_medium = translate_metrics(specs_medium)
    assert "equilíbrio" in result_medium["peso_balanceado"].lower()

    # Heavy swingweight (> 115)
    specs_heavy = SpecsResponse(
        swingweight=125,
        twistweight=5.0,
        weight_oz=8.5,
        core_thickness_mm=15.0,
        face_material="graphite"
    )
    result_heavy = translate_metrics(specs_heavy)
    assert "potência" in result_heavy["peso_balanceado"].lower()


def test_translate_metrics__weight_conversion_oz_to_grams():
    """Weight conversion from oz to grams is correct."""
    specs = SpecsResponse(
        swingweight=110,
        twistweight=5.5,
        weight_oz=8.0,  # ~227g
        core_thickness_mm=14.0,
        face_material="fiberglass"
    )
    result = translate_metrics(specs)

    # 8.0 oz * 28.35 ≈ 226.8g, rounds to 227g
    assert "227g" in result["peso_total"]


def test_translate_metrics__core_thickness_recognized():
    """Core thickness translations recognized."""
    # Thin core (< 13mm)
    specs_thin = SpecsResponse(
        swingweight=110,
        twistweight=5.5,
        weight_oz=8.0,
        core_thickness_mm=12.0,
        face_material="fiberglass"
    )
    result_thin = translate_metrics(specs_thin)
    assert "fino" in result_thin["nucleoInterno"].lower()

    # Medium core (13-16mm)
    specs_med = SpecsResponse(
        swingweight=110,
        twistweight=5.5,
        weight_oz=8.0,
        core_thickness_mm=14.5,
        face_material="fiberglass"
    )
    result_med = translate_metrics(specs_med)
    assert "médio" in result_med["nucleoInterno"].lower()

    # Thick core (> 16mm)
    specs_thick = SpecsResponse(
        swingweight=110,
        twistweight=5.5,
        weight_oz=8.0,
        core_thickness_mm=17.0,
        face_material="fiberglass"
    )
    result_thick = translate_metrics(specs_thick)
    assert "espesso" in result_thick["nucleoInterno"].lower()


def test_translate_metrics__face_material_recognized():
    """Face material translations recognized."""
    # Fiberglass
    specs_fg = SpecsResponse(
        swingweight=110,
        twistweight=5.5,
        weight_oz=8.0,
        core_thickness_mm=14.0,
        face_material="fiberglass"
    )
    result_fg = translate_metrics(specs_fg)
    assert "Fibra de vidro" in result_fg["facePrincipal"]

    # Graphite
    specs_gr = SpecsResponse(
        swingweight=110,
        twistweight=5.5,
        weight_oz=8.0,
        core_thickness_mm=14.0,
        face_material="graphite"
    )
    result_gr = translate_metrics(specs_gr)
    assert "Grafite" in result_gr["facePrincipal"]

    # Carbon
    specs_carbon = SpecsResponse(
        swingweight=110,
        twistweight=5.5,
        weight_oz=8.0,
        core_thickness_mm=14.0,
        face_material="carbon"
    )
    result_carbon = translate_metrics(specs_carbon)
    assert "Carbono" in result_carbon["facePrincipal"]
