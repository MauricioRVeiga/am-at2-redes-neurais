from contextlib import asynccontextmanager
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, Request

from .schemas import Cliente, Predicao

CAMINHO_MODELO = Path(__file__).resolve().parent.parent / "models" / "pipeline_rede_neural.joblib"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.modelo = joblib.load(CAMINHO_MODELO)
    yield


app = FastAPI(title="Previsão de Churn - Telco", version="2.0.0", lifespan=lifespan)


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
    probabilidades = modelo.predict_proba(pd.DataFrame([cliente.model_dump()]))[0]
    indice = probabilidades.argmax()
    return Predicao(
        categoria_prevista=str(modelo.classes_[indice]),
        score_confianca=float(probabilidades[indice]),
    )
