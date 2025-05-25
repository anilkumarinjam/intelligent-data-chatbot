import json

FORMULA_FILE = "formula_registry.json"

def load_formulas():
    try:
        with open(FORMULA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_formulas(formulas: dict):
    with open(FORMULA_FILE, "w") as f:
        json.dump(formulas, f, indent=4)

def add_formula(name: str, formula_code: str, description: str = ""):
    formulas = load_formulas()
    formulas[name] = {"code": formula_code, "description": description}
    save_formulas(formulas)

def get_all_formulas():
    return load_formulas()
