import json
import pkgutil

CATALOG_PATH = "data/leon_a_locations.json"


def load_catalog():
    data = pkgutil.get_data(__name__, CATALOG_PATH)
    if data is None:
        raise FileNotFoundError(CATALOG_PATH)

    return json.loads(data)

LEON_A_LOCATIONS = load_catalog()