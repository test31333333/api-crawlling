from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()


@app.get("/ttt")
async def read_main():
    return {"msg": "Hello  dfsdf dsf adsfsd adsf adsf asdfWorld"}



@app.post("/ttt/rr")
async def read_main():
    return {"msg": "ttttttttttttttttttttttttttt  dfsdf dsf adsfsd adsf adsf asdfWorld"}

@app.get("/yyy/yy/yy")
async def read_main():
    return {"msg": "yyyyyyyyyyyyyyyf adsf asdfWorld"}



client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}