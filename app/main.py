from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chat

app = FastAPI(
    title="Multi Tenent Chat App",
    description="Scalable FastAPI backend replacing Next.js API Routes",
    version="1.0.0"
)

# Configure CORS so your Next.js frontend can call it securely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins like ["http://localhost:3000"] in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the chat routing system
app.include_router(chat.router, prefix="/api")

@app.get("/")
def read_root():
    return {"status": "healthy", "service": "Logistics AI Backend"}