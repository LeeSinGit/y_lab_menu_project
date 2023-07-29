from api.endpoints.router import router as router_operation
from fastapi import FastAPI


app = FastAPI(title='YP Project')

app.include_router(router_operation)
