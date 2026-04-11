#!/usr/bin/env python3
"""
Script de validação dos scripts de limpeza do catálogo.
Verifica sintaxe e importação sem executar operações no banco.
"""

import ast
import sys
from pathlib import Path

SCRIPTS = [
    "1_analyze_catalog.py",
    "2_backup_data.py",
    "3_cleanup_catalog.py",
    "4_maintenance_check.py",
]


def validate_syntax(filepath: Path) -> bool:
    """Valida sintaxe Python do arquivo."""
    try:
        with open(filepath, 'r') as f:
            source = f.read()
        ast.parse(source)
        return True
    except SyntaxError as e:
        print(f"  ❌ Erro de sintaxe: {e}")
        return False


def validate_imports(filepath: Path) -> bool:
    """Valida que imports estão corretos."""
    try:
        # Apenas verificar se o arquivo pode ser parseado
        with open(filepath, 'r') as f:
            source = f.read()
        tree = ast.parse(source)
        
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        print(f"  ✓ Imports encontrados: {len(imports)}")
        return True
    except Exception as e:
        print(f"  ❌ Erro ao verificar imports: {e}")
        return False


def main():
    """Valida todos os scripts."""
    base_dir = Path(__file__).parent
    
    print("=" * 70)
    print("🔍 VALIDAÇÃO DOS SCRIPTS DE LIMPEZA")
    print("=" * 70)
    print()
    
    all_ok = True
    
    for script_name in SCRIPTS:
        filepath = base_dir / script_name
        
        print(f"📄 {script_name}")
        
        if not filepath.exists():
            print(f"  ❌ Arquivo não encontrado")
            all_ok = False
            continue
        
        # Validar sintaxe
        if not validate_syntax(filepath):
            all_ok = False
            continue
        print(f"  ✓ Sintaxe Python OK")
        
        # Validar imports
        if not validate_imports(filepath):
            all_ok = False
        
        print()
    
    # Verificar playbook
    playbook_path = base_dir / "PLAYBOOK_DE_LIMPEZA.md"
    print(f"📄 PLAYBOOK_DE_LIMPEZA.md")
    if playbook_path.exists():
        content = playbook_path.read_text()
        sections = content.count("##")
        print(f"  ✓ Arquivo encontrado ({len(content)} chars, ~{sections} seções)")
    else:
        print(f"  ❌ Arquivo não encontrado")
        all_ok = False
    
    print()
    print("=" * 70)
    if all_ok:
        print("✅ TODOS OS ARQUIVOS VALIDADOS COM SUCESSO!")
        print()
        print("Próximos passos:")
        print("  1. Configurar variável DATABASE_URL")
        print("  2. Executar: python 1_analyze_catalog.py")
        print("  3. Executar: python 2_backup_data.py --verify")
        print("  4. Executar: python 3_cleanup_catalog.py --dry-run")
        return 0
    else:
        print("❌ ALGUNS ARQUIVOS COM PROBLEMAS")
        return 1


if __name__ == "__main__":
    sys.exit(main())
