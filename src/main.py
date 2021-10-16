from typing import List, Optional
from fastapi import FastAPI
from fastapi.param_functions import Query
from fastapi.responses import PlainTextResponse
from mangum import Mangum


app = FastAPI()


@app.get("/math/add", response_class=PlainTextResponse)
async def addition(i: Optional[List[int]] = Query([])):
    return str(sum(i))


@app.get("/")
async def health():
    return {"status": "OK"}


handler = Mangum(app)
