import io


def test_full_flow(logged_in):
    c = logged_in
    assert c.get("/api/analysis").status_code == 404           # nothing uploaded yet
    assert c.post("/upload", data={"use_sample": "1"}).status_code == 302
    a = c.get("/api/analysis").get_json()
    assert a["kpis"]["customers"] == 2000 and a["filename"] == "WideLens_Nagpur_Sample.xlsx"
    j = c.post("/api/rank", json={"radius": 4}).get_json()
    assert j["recommendations"][0]["rank"] == 1 and j["radius"] == 4
    assert 0 <= j["recommendations"][0]["robust_top1"] <= 1


def test_rank_clamps_bad_input(logged_in):
    logged_in.post("/upload", data={"use_sample": "1"})
    r = logged_in.post("/api/rank", json={"radius": "abc", "weights": {"demand": -5, "gap": 1000}})
    assert r.status_code == 200


def test_pdf(logged_in):
    logged_in.post("/upload", data={"use_sample": "1"})
    r = logged_in.post("/api/report.pdf", json={})
    assert r.status_code == 200 and r.data[:4] == b"%PDF"


def test_bad_upload_rejected(logged_in):
    r = logged_in.post("/upload", data={"file": (io.BytesIO(b"a,b\n1,2"), "x.csv")}, content_type="multipart/form-data", follow_redirects=True)
    assert b"missing required column" in r.data
