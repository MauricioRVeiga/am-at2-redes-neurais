from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

MENSALIDADE_MAXIMA = 150
SimNao = Literal["Yes", "No"]
ServicoDeInternet = Literal["Yes", "No", "No internet service"]
SERVICOS_DE_INTERNET = (
    "OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies",
)


class Cliente(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    gender: Literal["Male", "Female"] = Field(description="Gênero do cliente", examples=["Female"])
    SeniorCitizen: int = Field(ge=0, le=1, description="1 se o cliente tem 65 anos ou mais", examples=[0])
    Partner: SimNao = Field(description="Possui cônjuge ou companheiro(a)", examples=["Yes"])
    Dependents: SimNao = Field(description="Possui dependentes", examples=["No"])
    tenure: int = Field(ge=0, le=72, description="Meses de permanência na operadora", examples=[12])
    PhoneService: SimNao = Field(description="Possui linha telefônica", examples=["Yes"])
    MultipleLines: Literal["Yes", "No", "No phone service"] = Field(
        description="Possui múltiplas linhas", examples=["No"]
    )
    InternetService: Literal["DSL", "Fiber optic", "No"] = Field(
        description="Tipo de serviço de internet", examples=["Fiber optic"]
    )
    OnlineSecurity: ServicoDeInternet = Field(description="Contratou segurança online", examples=["No"])
    OnlineBackup: ServicoDeInternet = Field(description="Contratou backup online", examples=["No"])
    DeviceProtection: ServicoDeInternet = Field(description="Contratou proteção de aparelho", examples=["No"])
    TechSupport: ServicoDeInternet = Field(description="Contratou suporte técnico", examples=["No"])
    StreamingTV: ServicoDeInternet = Field(description="Contratou streaming de TV", examples=["Yes"])
    StreamingMovies: ServicoDeInternet = Field(description="Contratou streaming de filmes", examples=["Yes"])
    Contract: Literal["Month-to-month", "One year", "Two year"] = Field(
        description="Tipo de contrato", examples=["Month-to-month"]
    )
    PaperlessBilling: SimNao = Field(description="Recebe fatura digital", examples=["Yes"])
    PaymentMethod: Literal[
        "Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"
    ] = Field(description="Forma de pagamento", examples=["Electronic check"])
    MonthlyCharges: float = Field(
        ge=0, le=MENSALIDADE_MAXIMA, allow_inf_nan=False, description="Valor da mensalidade", examples=[89.9]
    )
    TotalCharges: float = Field(
        ge=0, le=72 * MENSALIDADE_MAXIMA, allow_inf_nan=False,
        description="Total cobrado durante a permanência", examples=[1078.8],
    )

    @model_validator(mode="after")
    def validar_consistencia(self) -> Self:
        sem_telefone = self.PhoneService == "No"
        if sem_telefone != (self.MultipleLines == "No phone service"):
            raise ValueError("MultipleLines deve ser 'No phone service' se, e somente se, PhoneService for 'No'")

        sem_internet = self.InternetService == "No"
        for servico in SERVICOS_DE_INTERNET:
            if sem_internet != (getattr(self, servico) == "No internet service"):
                raise ValueError(
                    f"{servico} deve ser 'No internet service' se, e somente se, InternetService for 'No'"
                )

        if self.TotalCharges > self.tenure * MENSALIDADE_MAXIMA:
            raise ValueError(
                f"TotalCharges não pode exceder tenure x {MENSALIDADE_MAXIMA} ({self.tenure * MENSALIDADE_MAXIMA})"
            )
        return self


class Predicao(BaseModel):
    categoria_prevista: Literal["cancela", "permanece"] = Field(description="Classe inferida pelo modelo")
    score_confianca: float = Field(ge=0, le=1, description="Probabilidade da classe prevista")
    probabilidade_cancelamento: float = Field(
        ge=0, le=1, description="Probabilidade de cancelamento, útil para aplicar limiares de decisão próprios"
    )
