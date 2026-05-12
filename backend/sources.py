import requests
from typing import List, Dict, Any


POKEAPI_BASE = "https://pokeapi.co/api/v2"


def get_json(url: str) -> Dict[str, Any]:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def clean_text(value: str) -> str:
    return " ".join(value.replace("\n", " ").replace("\f", " ").split())


def fetch_pokemon_data(limit: int = 1025) -> List[Dict[str, str]]:
    docs = []
    pokemon_list = get_json(f"{POKEAPI_BASE}/pokemon?limit={limit}")["results"]

    for item in pokemon_list:
        name = item["name"]
        print(f"Fetching Pokémon: {name}")

        pokemon = get_json(item["url"])
        species = get_json(pokemon["species"]["url"])

        types = [t["type"]["name"] for t in pokemon["types"]]
        abilities = [a["ability"]["name"] for a in pokemon["abilities"]]
        stats = {s["stat"]["name"]: s["base_stat"] for s in pokemon["stats"]}

        flavor_entries = []
        for entry in species.get("flavor_text_entries", []):
            if entry["language"]["name"] == "en":
                flavor_entries.append(clean_text(entry["flavor_text"]))

        unique_entries = list(dict.fromkeys(flavor_entries))[:5]

        text = f"""
        Pokémon: {name}
        National Dex ID: {pokemon["id"]}
        Height: {pokemon["height"]}
        Weight: {pokemon["weight"]}
        Types: {", ".join(types)}
        Abilities: {", ".join(abilities)}
        Base stats: {stats}
        Generation: {species["generation"]["name"]}
        Color: {species["color"]["name"]}
        Shape: {species["shape"]["name"] if species["shape"] else "unknown"}
        Habitat: {species["habitat"]["name"] if species["habitat"] else "unknown"}
        Legendary: {species["is_legendary"]}
        Mythical: {species["is_mythical"]}
        Baby Pokémon: {species["is_baby"]}
        Pokédex entries: {" | ".join(unique_entries)}
        Evolution chain URL: {species["evolution_chain"]["url"]}
        """

        docs.append({
            "id": f"pokemon-{pokemon['id']}",
            "source": "pokeapi",
            "title": name,
            "text": clean_text(text),
        })

    return docs


def fetch_move_data(limit: int = 100000) -> List[Dict[str, str]]:
    docs = []
    moves = get_json(f"{POKEAPI_BASE}/move?limit={limit}")["results"]

    for item in moves:
        name = item["name"]
        print(f"Fetching move: {name}")

        move = get_json(item["url"])

        effect = ""
        for effect_entry in move.get("effect_entries", []):
            if effect_entry["language"]["name"] == "en":
                effect = clean_text(effect_entry["effect"])
                break

        flavor = ""
        for flavor_entry in move.get("flavor_text_entries", []):
            if flavor_entry["language"]["name"] == "en":
                flavor = clean_text(flavor_entry["flavor_text"])
                break

        text = f"""
        Move: {name}
        Type: {move["type"]["name"]}
        Category: {move["damage_class"]["name"]}
        Power: {move["power"]}
        Accuracy: {move["accuracy"]}
        PP: {move["pp"]}
        Priority: {move["priority"]}
        Effect chance: {move["effect_chance"]}
        Short description: {flavor}
        Effect: {effect}
        """

        docs.append({
            "id": f"move-{move['id']}",
            "source": "pokeapi",
            "title": name,
            "text": clean_text(text),
        })

    return docs


def fetch_ability_data(limit: int = 100000) -> List[Dict[str, str]]:
    docs = []
    abilities = get_json(f"{POKEAPI_BASE}/ability?limit={limit}")["results"]

    for item in abilities:
        name = item["name"]
        print(f"Fetching ability: {name}")

        ability = get_json(item["url"])

        effect = ""
        for effect_entry in ability.get("effect_entries", []):
            if effect_entry["language"]["name"] == "en":
                effect = clean_text(effect_entry["effect"])
                break

        pokemon_with_ability = [p["pokemon"]["name"] for p in ability.get("pokemon", [])]

        text = f"""
        Ability: {name}
        Effect: {effect}
        Pokémon with this ability: {", ".join(pokemon_with_ability[:100])}
        """

        docs.append({
            "id": f"ability-{ability['id']}",
            "source": "pokeapi",
            "title": name,
            "text": clean_text(text),
        })

    return docs
