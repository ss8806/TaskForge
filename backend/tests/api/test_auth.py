def test_register(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "test123"}
    )
    assert response.status_code == 201
