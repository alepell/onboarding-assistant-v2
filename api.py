from fastapi import FastAPI
from pydantic import BaseModel

from onboarding_assistant_v2.main import OnboardingFlow

app = FastAPI()


class PerguntaRequest(BaseModel):
    pergunta: str


@app.post("/perguntar")
def perguntar(request: PerguntaRequest):
    onboarding_flow = OnboardingFlow()
    onboarding_flow.kickoff(
        inputs={"crewai_trigger_payload": {"pergunta": request.pergunta}}
    )
    return {"resposta": onboarding_flow.state.resposta_final}
