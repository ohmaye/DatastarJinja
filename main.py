from init import templates, app

from fastapi import Request
from fastapi.responses import HTMLResponse
from datastar_py.responses import DatastarFastAPIResponse

from src.school import router as school_router


# Include routes from other modules
app.include_router(school_router)


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="layout/index.html", context={})


@app.get("/something")
def something(request: Request):
    def tst(sse):
        yield sse.merge_fragments(["""<div id="hello">DID IT</div>"""])

    return DatastarFastAPIResponse(tst)


# class Item(BaseModel):
#     name: str
#     price: float
#     is_offer: Union[bool, None] = None

# @app.get("/items/{id}", response_class=HTMLResponse)
# async def get_item(request: Request, id: str):
#     return templates.TemplateResponse(request=request, name="item.html", context={"id": id})


# @app.get("/updates")
# async def updates(request: Request):
#     print("IS DATASTAR", is_datastar(request))

#     async def tst(sse):
#         yield sse.merge_fragments(["""<div id="hello">DID IT</div>"""])

#     return DatastarFastAPIResponse(tst)
