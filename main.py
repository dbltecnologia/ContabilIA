from fastapi import FastAPI
from modules.focus_nfe.focus_client import _load_dotenv_if_present
from modules.focus_nfe.router import router as focus_router
from modules.focus_nfe.webhooks import router as webhook_router
from fastapi.staticfiles import StaticFiles
from modules.focus_nfe.database import init_db
import os
import uvicorn

app = FastAPI(
    title="Contabil IA - API Server",
    description="API para gestão de documentos fiscais integrando FocusNFE e outros módulos.",
    version="2.1.0"
)

# Startup event
@app.on_event("startup")
def on_startup():
    _load_dotenv_if_present()
    init_db()

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Contabil IA API is running", "docs": "/docs"}

# Include Routers
app.include_router(focus_router, prefix="/api")
app.include_router(webhook_router, prefix="/api")

# Serve Storage (PDFs/XMLs)
if not os.path.exists("storage"):
    os.makedirs("storage")
app.mount("/storage", StaticFiles(directory="storage"), name="storage")

# Serve Dashboard (Build folder)
# Se a pasta dist existir, serve ela como root. Caso contrário, serve uma mensagem.
DASHBOARD_PATH = "dashboard/dist"
if os.path.exists(DASHBOARD_PATH):
    app.mount("/dashboard", StaticFiles(directory=DASHBOARD_PATH, html=True), name="dashboard")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
