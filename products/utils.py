def format_variant_combo(combo: str) -> str:
    if not combo:
        return "Default"

    parts = []
    for item in combo.split(","):
        if ":" in item:
            k, v = item.split(":", 1)
            parts.append(f"{k.strip()}: {v.strip()}")
        else:
            parts.append(item.strip())

    return " / ".join(parts)