from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .routers import users, auth, products, cart, checkout

models.Base.metadata.create_all(bind=engine)

app = FastAPI(max_request_size=100 * 1024 * 1024)


@app.get("/")
def read_root():
    return {"Hanuman": "Jay Shree Ram"}

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(checkout.router)