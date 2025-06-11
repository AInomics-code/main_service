from fastapi import APIRouter, Request

from rest.agents.la_dona import process as la_dona

router = APIRouter()

@router.post("/hola")
async def la_dona_process(request: Request):
    return await la_dona(request)
