from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from typing import List

app = FastAPI()

class SignalData(BaseModel):
    id: int
    quantidade_carros: int
    carros_por_segundo: float
    tempo_sinal_aberto: float

@app.post("/sinais")
async def receive_signals(signals: List[SignalData]):
    # Processar os dados dos sinais aqui
    return {"message": "Dados recebidos com sucesso", "data": signals}

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Semaforo IA API",
        version="1.0.0",
        description="API para receber dados de sinais de trânsito",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
