# AT2 - Redes Neurais MLP e Deploy de API

Previsão de cancelamento de clientes (churn) de uma operadora de telecomunicações com um `MLPClassifier` encapsulado em um Pipeline do Scikit-Learn e servido por uma API FastAPI.

## Dataset

**Telco Customer Churn** - https://www.kaggle.com/datasets/blastchar/telco-customer-churn

7.043 clientes, 19 variáveis preditoras (3 numéricas e 16 categóricas) e alvo binário `Churn`. O arquivo original está em `data/dataset.csv`.

## Resultados (conjunto de teste, 20% estratificado)

| Métrica | Valor |
|---|---|
| Acurácia | 0.8155 |
| MCC | 0.4982 |
| F1 `cancela` | 0.6108 |
| F1 `permanece` | 0.8791 |

Arquitetura: `(128, 64, 32)`, ReLU, Adam com `learning_rate_init=0.001`, `alpha=0.001`, early stopping e `random_state=77`.

## Estrutura

```
data/dataset.csv                     base original do Kaggle
models/pipeline_rede_neural.joblib   pipeline (ColumnTransformer + MLP) serializado
notebooks/analise_treinamento.ipynb  EDA, treinamento e avaliação
src/schemas.py                       contratos Pydantic de entrada e saída
src/app.py                           aplicação FastAPI, lifespan e rotas
requisicoes.http                     testes de integração HTTP
```

## Como reproduzir

Pré-requisito: [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
uv sync
```

### Treinar o modelo

Abra o notebook e execute todas as células:

```bash
uv run jupyter lab notebooks/analise_treinamento.ipynb
```

Ou execute direto pelo terminal:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace notebooks/analise_treinamento.ipynb
```

O pipeline treinado é gravado em `models/pipeline_rede_neural.joblib`.

### Subir a API

```bash
uv run uvicorn src.app:app --reload
```

Documentação interativa em http://127.0.0.1:8000/docs.

| Método | Rota | Descrição |
|---|---|---|
| GET | `/diagnostico/modelo` | Status do serviço e tipo do modelo |
| POST | `/predict` | Recebe os dados do cliente e retorna `categoria_prevista`, `score_confianca` e `probabilidade_cancelamento` |

`score_confianca` é a probabilidade da classe prevista. `probabilidade_cancelamento` é sempre a probabilidade de `cancela`, para quem precisar aplicar um limiar de decisão diferente de 0,5.

### Validação da entrada

- Tipos estritos: texto em campo numérico, número em texto ou booleano em inteiro retornam `422`.
- Categorias restritas aos valores existentes na base.
- Limites numéricos: `tenure` de 0 a 72, `MonthlyCharges` de 0 a 150 e `TotalCharges` de 0 a 10.800.
- Consistência entre campos: `MultipleLines = "No phone service"` exige `PhoneService = "No"` (e vice-versa); os serviços de internet usam `"No internet service"` exatamente quando `InternetService = "No"`; `TotalCharges` não pode passar de `tenure × 150`.
- O corpo deve conter apenas as 19 features. `customerID` não é aceito.

### Testar

Com a API rodando, abra `requisicoes.http` no VS Code (extensão REST Client) ou em uma IDE JetBrains e execute as requisições. O arquivo cobre o endpoint de metadados, dois perfis com predições opostas e três payloads inválidos que retornam `422`.

Exemplo com curl:

```bash
curl -s http://127.0.0.1:8000/diagnostico/modelo -H "User-Agent: Tester-Audit-Agent"
```
