import re

def load_variables(filepath="VARIABLES.md"):
    vars = {}
    with open(filepath, "r") as f:
        content = f.read()

    # Simple regex to extract VARIABLE : VALUE
    matches = re.findall(r"([A-Z_0-9]+)\s*:\s*(.+)", content)
    for key, value in matches:
        # Try to parse as int or float or list/dict
        val = value.strip()
        if val.startswith("{") or val.startswith("["):
            # Keep as string
            vars[key] = val
        else:
            try:
                if "." in val:
                    vars[key] = float(val)
                else:
                    vars[key] = int(val)
            except ValueError:
                vars[key] = val

    # Manual overrides for known list variables if parsing failed or was incomplete
    vars["NIVEAUX_ENTROPIE"] = [0.05, 0.1, 0.2, 0.5, 1.0, 2.0]
    vars["NIVEAUX_CONFLIT"] = [0.0, 0.2, 0.5, 0.8]
    if "SEED_GLOBAL" not in vars:
        vars["SEED_GLOBAL"] = 42

    return vars
