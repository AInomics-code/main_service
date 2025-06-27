from fastapi import Request

async def invoke_agent(request: Request):
    return "meow"
