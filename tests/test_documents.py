import uuid


async def _collection(client, name="Docs"):
    response = await client.post("/collections", json={"name": name})
    assert response.status_code == 201
    return response.json()["id"]


async def test_create_document_starts_pending(client):
    collection_id = await _collection(client)
    created = await client.post(
        f"/collections/{collection_id}/documents",
        json={"title": "Uno", "content": "hola"},
    )
    assert created.status_code == 201
    body = created.json()
    assert body["status"] == "pending"
    assert body["collection_id"] == collection_id
    assert body["title"] == "Uno"
    assert body["content"] == "hola"

    fetched = await client.get(f"/documents/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["status"] == "pending"

    listed = await client.get(f"/collections/{collection_id}/documents")
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [body["id"]]


async def test_client_cannot_set_status(client):
    collection_id = await _collection(client)
    created = await client.post(
        f"/collections/{collection_id}/documents",
        json={"title": "Uno", "content": "hola", "status": "processed"},
    )
    assert created.status_code == 201
    assert created.json()["status"] == "pending"


async def test_document_in_missing_collection_returns_404(client):
    missing = uuid.uuid4()
    created = await client.post(
        f"/collections/{missing}/documents",
        json={"title": "Uno", "content": "hola"},
    )
    assert created.status_code == 404
    listed = await client.get(f"/collections/{missing}/documents")
    assert listed.status_code == 404


async def test_patch_is_partial_and_empty_body_keeps_fields(client):
    collection_id = await _collection(client)
    created = await client.post(
        f"/collections/{collection_id}/documents",
        json={"title": "Original", "content": "texto"},
    )
    document_id = created.json()["id"]

    empty = await client.patch(f"/documents/{document_id}", json={})
    assert empty.status_code == 200
    assert empty.json()["title"] == "Original"
    assert empty.json()["content"] == "texto"
    assert empty.json()["status"] == "pending"

    updated = await client.patch(
        f"/documents/{document_id}",
        json={"title": "Nuevo"},
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Nuevo"
    assert updated.json()["content"] == "texto"


async def test_delete_collection_deletes_its_documents(client):
    collection_id = await _collection(client)
    created = await client.post(
        f"/collections/{collection_id}/documents",
        json={"title": "Uno", "content": "hola"},
    )
    document_id = created.json()["id"]

    deleted = await client.delete(f"/collections/{collection_id}")
    assert deleted.status_code == 204
    assert (await client.get(f"/documents/{document_id}")).status_code == 404


async def test_delete_document(client):
    collection_id = await _collection(client)
    created = await client.post(
        f"/collections/{collection_id}/documents",
        json={"title": "Uno", "content": "hola"},
    )
    document_id = created.json()["id"]

    deleted = await client.delete(f"/documents/{document_id}")
    assert deleted.status_code == 204
    assert (await client.get(f"/documents/{document_id}")).status_code == 404
    assert (await client.get(f"/collections/{collection_id}")).status_code == 200


async def test_missing_document_returns_404(client):
    missing = uuid.uuid4()
    assert (await client.get(f"/documents/{missing}")).status_code == 404
    assert (await client.patch(f"/documents/{missing}", json={"title": "x"})).status_code == 404
    assert (await client.delete(f"/documents/{missing}")).status_code == 404


async def test_invalid_document_returns_422(client):
    collection_id = await _collection(client)
    assert (
        await client.post(
            f"/collections/{collection_id}/documents",
            json={"title": "Uno", "content": ""},
        )
    ).status_code == 422
    assert (
        await client.post(
            f"/collections/{collection_id}/documents",
            json={"title": "", "content": "hola"},
        )
    ).status_code == 422
