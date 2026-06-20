import requests


ARTIC_ARTWORK_URL = "https://api.artic.edu/api/v1/artworks/{artwork_id}"


class ArticAPIError(Exception):
    pass


def get_artwork_by_id(artwork_id: str) -> dict | None:
    try:
        response = requests.get(
            ARTIC_ARTWORK_URL.format(artwork_id=artwork_id),
            params={"fields": "id,title"},
            timeout=10,
        )
    except requests.RequestException as exc:
        raise ArticAPIError from exc

    if response.status_code == 404:
        return None

    try:
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ArticAPIError from exc

    data = response.json().get("data")
    if not data:
        return None

    return data