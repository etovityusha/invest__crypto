import uvicorn
from fastapi import FastAPI

import api.tokens.endpoints as tokens_endpoints
from core.sql_app import models
from core.sql_app.database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(tokens_endpoints.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7070, log_level="info")
