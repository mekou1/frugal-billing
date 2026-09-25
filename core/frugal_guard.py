"""
core/frugal_guard.py — Linter Statique Garde-Fou Frugal (Pure Stdlib Python).

Vérifie mécaniquement par parsing AST :
1. Règle des 150 lignes par fichier.
2. Complexité cyclomatique de McCabe <= 8 par fonction.
3. Zéro float monétaire (détection statique d'usage de float sur montants/prix/balance).
"""
import ast, os, pathlib, sys
from dataclasses import dataclass
from typing import List, Tuple

MONEY_KEYWORDS = {"amount", "price", "balance", "cost", "total", "fee", "tax", "rate"}

@dataclass(frozen=True)
class Violation:
    file_path: str
    line: int
    rule: str
    message: str

def compute_mccabe(node: ast.AST) -> int:
    """Calcule la complexité cyclomatique de McCabe d'un nœud fonction."""
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.ExceptHandler, ast.With, ast.Assert)):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
    return complexity

class GuardVisitor(ast.NodeVisitor):
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.violations: List[Violation] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_complexity(node)
        self._check_money_args(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_complexity(node)
        self._check_money_args(node)
        self.generic_visit(node)

    def _check_complexity(self, node: ast.AST) -> None:
        name = getattr(node, "name", "unknown")
        score = compute_mccabe(node)
        if score > 8:
            self.violations.append(Violation(
                self.file_path, getattr(node, "lineno", 1), "MCCABE_MAX_8",
                f"Fonction '{name}' trop complexe (McCabe={score} > 8)"
            ))

    def _check_money_args(self, node: ast.AST) -> None:
        args = getattr(getattr(node, "args", None), "args", [])
        for arg in args:
            if any(k in arg.arg.lower() for k in MONEY_KEYWORDS):
                annotation = ast.unparse(arg.annotation) if arg.annotation else ""
                if "float" in annotation.lower():
                    self.violations.append(Violation(
                        self.file_path, arg.lineno, "ZERO_FLOAT_MONEY",
                        f"Argument monétaire '{arg.arg}' typé en float (utiliser Decimal ou int)"
                    ))

def audit_file(file_path: pathlib.Path) -> List[Violation]:
    """Audite un fichier source unique selon les règles fondamentales."""
    violations: List[Violation] = []
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return [Violation(str(file_path), 1, "IO_ERROR", str(e))]

    lines = content.splitlines()
    if len(lines) > 150:
        violations.append(Violation(
            str(file_path), 151, "MAX_150_LINES",
            f"Fichier trop long ({len(lines)} lignes > 150)"
        ))

    try:
        tree = ast.parse(content)
        visitor = GuardVisitor(str(file_path))
        visitor.visit(tree)
        violations.extend(visitor.violations)
    except SyntaxError as e:
        violations.append(Violation(str(file_path), e.lineno or 1, "SYNTAX_ERROR", str(e)))
    return violations

def run_guard_cli(args: List[str]) -> int:
    """Point d'entrée CLI pour 'frugal check'."""
    targets = [pathlib.Path(a) for a in args] if args else [pathlib.Path("core")]
    all_violations: List[Violation] = []
    audited_count = 0

    for target in targets:
        files = [target] if target.is_file() else list(target.rglob("*.py"))
        for f in files:
            if "__pycache__" in str(f) or "tests/adversarial" in str(f):
                continue
            audited_count += 1
            all_violations.extend(audit_file(f))

    if not all_violations:
        print(f"✅ Garde-Fou : {audited_count} fichiers audités — 100% conformes (150L, McCabe <= 8, zéro float)")
        return 0

    print(f"❌ Garde-Fou : {len(all_violations)} violations détectées sur {audited_count} fichiers :")
    for v in all_violations:
        print(f"  [{v.rule}] {v.file_path}:{v.line} — {v.message}")
    return 1

if __name__ == "__main__":
    sys.exit(run_guard_cli(sys.argv[1:]))
