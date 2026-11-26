import uuid


async def test_create_and_get_collection(client):
    created = await client.post(
        "/collections",
        json={"name": "Notas", "description": "apuntes"},
    )
    assert created.status_code == 201
    body = created.json()
    assert body["name"] == "Notas"
    assert body["description"] == "apuntes"
    assert body["id"]

    fetched = await client.get(f"/collections/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Notas"

    listed = await client.get("/collections")
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [body["id"]]


async def test_duplicate_name_returns_409(client):
    payload = {"name": "Única"}
    assert (await client.post("/collections", json=payload)).status_code == 201
    duplicate = await client.post("/collections", json=payload)
    assert duplicate.status_code == 409


async def test_patch_is_partial_and_empty_body_keeps_fields(client):
    created = await client.post(
        "/collections",
        json={"name": "Original", "description": "sigue aquí"},
    )
    collection_id = created.json()["id"]

    empty = await client.patch(f"/collections/{collection_id}", json={})
    assert empty.status_code == 200
    assert empty.json()["name"] == "Original"
    assert empty.json()["description"] == "sigue aquí"

    renamed = await client.patch(
        f"/collections/{collection_id}",
        json={"description": "nueva"},
    )
    assert renamed.status_code == 200
    assert renamed.json()["name"] == "Original"
    assert renamed.json()["description"] == "nueva"


async def test_patch_duplicate_name_returns_409(client):
    await client.post("/collections", json={"name": "A"})
    other = await client.post("/collections", json={"name": "B"})
    response = await client.patch(
        f"/collections/{other.json()['id']}",
        json={"name": "A"},
    )
    assert response.status_code == 409
    fetched = await client.get(f"/collections/{other.json()['id']}")
    assert fetched.json()["name"] == "B"


async def test_delete_collection(client):
    created = await client.post("/collections", json={"name": "Borrar"})
    collection_id = created.json()["id"]

    deleted = await client.delete(f"/collections/{collection_id}")
    assert deleted.status_code == 204
    assert (await client.get(f"/collections/{collection_id}")).status_code == 404


async def test_missing_collection_returns_404(client):
    missing = uuid.uuid4()
    assert (await client.get(f"/collections/{missing}")).status_code == 404
    assert (await client.patch(f"/collections/{missing}", json={"name": "x"})).status_code == 404
    assert (await client.delete(f"/collections/{missing}")).status_code == 404


async def test_invalid_collection_returns_422(client):
    assert (await client.post("/collections", json={"name": ""})).status_code == 422
    assert (await client.post("/collections", json={})).status_code == 422
