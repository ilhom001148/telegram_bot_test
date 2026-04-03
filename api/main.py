from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.auth import router as auth_router
from api.routes.dashboard import router as dashboard_router
from api.routes.groups import router as groups_router
from api.routes.messages import router as messages_router
from api.routes.questions import router as questions_router
from api.routes.knowledge import router as knowledge_router

app = FastAPI(title="Telegram Bot Admin API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(groups_router)
app.include_router(messages_router)
app.include_router(questions_router)
app.include_router(knowledge_router)


@app.get("/")
def root():
    return {"message": "API is running"}