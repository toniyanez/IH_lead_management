def calculate_score(summary, growth_phase):
    score = 0
    keywords = ["IVD", "AI", "digital health", "medtech", "IVDR", "FDA"]
    for keyword in keywords:
        if keyword.lower() in summary.lower():
            score += 10

    growth_map = {
        "pre-seed": 10,
        "seed": 20,
        "series a": 30,
        "series b": 40,
        "series c": 50,
        "consolidation": 60,
        "expansion": 70
    }

    score += growth_map.get(growth_phase.lower(), 0)
    return min(score, 100)
