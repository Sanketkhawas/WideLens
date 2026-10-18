def test_dashboard_requires_login(client):
    r = client.get("/app")
    assert r.status_code == 302 and "/login" in r.headers["Location"]


def test_register_and_login(client):
    client.post("/register", data=dict(name="A", email="a@x.com", password="password123", confirm_password="password123"))
    r = client.post("/login", data=dict(email="a@x.com", password="password123"))
    assert r.status_code == 302


def test_wrong_password(client):
    client.post("/register", data=dict(name="A", email="a@x.com", password="password123", confirm_password="password123"))
    r = client.post("/login", data=dict(email="a@x.com", password="nope"), follow_redirects=True)
    assert b"Invalid Email or Password" in r.data
