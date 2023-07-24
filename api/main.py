from fastapi import FastAPI
from router import router as router_operation


app = FastAPI(title='YP Project')

app.include_router(router_operation)
