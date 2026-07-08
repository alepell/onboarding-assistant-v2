#!/usr/bin/env python

from pydantic import BaseModel

from crewai.flow import Flow, listen, start

from onboarding_assistant_v2.crews.onboarding_crew.onboarding_crew import OnboardingCrew


class OnboardingState(BaseModel):
    pergunta_funcionario: str = ""
    resposta_final: str = ""


class OnboardingFlow(Flow[OnboardingState]):

    @start()
    def receber_pergunta(self, crewai_trigger_payload: dict = None):
        print("Recebendo pergunta do funcionário")

        if crewai_trigger_payload:
            self.state.pergunta_funcionario = crewai_trigger_payload.get(
                "pergunta", "Qual o horário de trabalho?"
            )
            print(f"Using trigger payload: {crewai_trigger_payload}")
        else:
            self.state.pergunta_funcionario = "Qual o horário de trabalho?"

        print(f"Pergunta: {self.state.pergunta_funcionario}")

    @listen(receber_pergunta)
    def rotear_e_responder(self):
        print(f"Roteando pergunta: {self.state.pergunta_funcionario}")
        result = (
            OnboardingCrew()
            .crew()
            .kickoff(inputs={"pergunta_funcionario": self.state.pergunta_funcionario})
        )

        print("Resposta gerada")
        self.state.resposta_final = result.raw


def kickoff():
    onboarding_flow = OnboardingFlow()
    onboarding_flow.kickoff()
    print("\n=== RESPOSTA FINAL ===")
    print(onboarding_flow.state.resposta_final)


def plot():
    onboarding_flow = OnboardingFlow()
    onboarding_flow.plot()


def run_with_trigger():
    """
    Run the flow with trigger payload.
    """
    import json
    import sys

    if len(sys.argv) < 2:
        raise Exception(
            "No trigger payload provided. Please provide JSON payload as argument."
        )

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    onboarding_flow = OnboardingFlow()

    try:
        result = onboarding_flow.kickoff({"crewai_trigger_payload": trigger_payload})
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the flow with trigger: {e}")


if __name__ == "__main__":
    kickoff()
