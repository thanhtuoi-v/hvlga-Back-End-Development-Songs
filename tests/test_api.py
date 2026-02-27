import json
import pytest


# --- Health & Count ---

def test_health(client):
    """GET /health returns 200 and status OK."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data.get("status") == "OK"


def test_count(client):
    """GET /count returns 200 and includes count field."""
    res = client.get("/count")
    assert res.status_code == 200
    data = res.get_json()
    assert "count" in data
    assert isinstance(data["count"], int)


# --- GET songs ---

def test_get_songs(client):
    """GET /songs returns list of songs in results."""
    res = client.get("/songs")
    assert res.status_code == 200
    data = res.get_json()
    assert "results" in data
    assert isinstance(data["results"], list)


def test_get_song_by_id(client):
    """GET /songs/<id> with existing id returns 200 and correct song."""
    res = client.get("/songs/1")
    assert res.status_code == 200
    data = res.get_json()
    assert "results" in data
    assert data["results"]["id"] == 1


def test_get_song_by_id_not_found(client):
    """GET /songs/<id> with non-existent id returns 404."""
    res = client.get("/songs/99")
    assert res.status_code == 404
    data = res.get_json()
    assert "message" in data


# --- POST (create) song ---
def test_create_song(client, song):
    """POST /songs with valid body creates new song, returns 201."""
    res = client.post(
        "/songs",
        data=json.dumps(song),
        content_type="application/json"
    )
    assert res.status_code == 201
    data = res.get_json()
    assert "message" in data


def test_create_song_duplicate_id(client, song):
    """POST /songs with existing id returns 409."""
    client.post("/songs", data=json.dumps(song), content_type="application/json")
    res = client.post("/songs", data=json.dumps(song), content_type="application/json")
    assert res.status_code == 409
    data = res.get_json()
    assert "message" in data


# --- PUT (update) song ---

def test_update_song(client, song):
    """PUT /songs/<id> updates song, returns 201."""
    client.post("/songs", data=json.dumps(song), content_type="application/json")
    song["title"] = "Updated title"
    res = client.put(
        f"/songs/{song['id']}",
        data=json.dumps(song),
        content_type="application/json"
    )
    assert res.status_code == 201


def test_update_song_not_found(client, song):
    """PUT /songs/<id> with non-existent id returns 404."""
    res = client.put(
        "/songs/99998",
        data=json.dumps({"id": 99998, "title": "x", "lyrics": "y"}),
        content_type="application/json"
    )
    assert res.status_code == 404


# --- DELETE song ---

def test_delete_song(client, song):
    """DELETE /songs/<id> deletes song by id, returns 204."""
    client.post("/songs", data=json.dumps(song), content_type="application/json")
    res = client.delete(f"/songs/{song['id']}")
    assert res.status_code == 204


def test_delete_song_not_found(client):
    """DELETE /songs/<id> with non-existent id returns 404."""
    res = client.delete("/songs/99997")
    assert res.status_code == 404
    data = res.get_json()
    assert "message" in data
