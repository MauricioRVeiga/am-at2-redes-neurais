import math
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .schemas import Cliente, Predicao

CAMINHO_MODELO = Path(__file__).resolve().parent.parent / "models" / "pipeline_rede_neural.joblib"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.modelo = joblib.load(CAMINHO_MODELO)
    yield


app = FastAPI(title="Previsão de Churn - Telco", lifespan=lifespan)


def _serializavel(valor):
    if isinstance(valor, float) and not math.isfinite(valor):
        return str(valor)
    if isinstance(valor, dict):
        return {chave: _serializavel(v) for chave, v in valor.items()}
    if isinstance(valor, list):
        return [_serializavel(v) for v in valor]
    return valor


@app.exception_handler(RequestValidationError)
async def erro_de_validacao(_: Request, erro: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": jsonable_encoder(_serializavel(erro.errors()))})


@app.get("/diagnostico/modelo")
def diagnostico(request: Request) -> dict[str, str]:
    return {
        "status": "operacional_v2",
        "framework": "FastAPI-Production",
        "modelo": type(request.app.state.modelo.named_steps["mlp"]).__name__,
    }


@app.post("/predict", response_model=Predicao)
def predict(cliente: Cliente, request: Request) -> Predicao:
    modelo = request.app.state.modelo
    probabilidades = dict(zip(modelo.classes_, modelo.predict_proba(pd.DataFrame([cliente.model_dump()]))[0]))
    categoria = max(probabilidades, key=probabilidades.get)
    return Predicao(
        categoria_prevista=str(categoria),
        score_confianca=float(probabilidades[categoria]),
        probabilidade_cancelamento=float(probabilidades["cancela"]),
    )
