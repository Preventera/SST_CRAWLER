# Réduire le nombre d'URLs de départ (uniquement la première URL)
start_urls=test_sources[TEST_SOURCE]['start_urls'][:1],

# Réduire la profondeur à 0 (seulement les pages de départ)
settings.update({
    # ...
    'DEPTH_LIMIT': 0,  # Ne crawler que les URLs de départ
    # ...
})