from onboarding_assistant_v2.tools.custom_tool import (
    FerramentaConsultaRH,
    FerramentaConsultaTecnica,
)
from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class OnboardingCrew:
    """Onboarding Assistant Crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def especialista_rh(self) -> Agent:
        return Agent(
            config=self.agents_config["especialista_rh"],  # type: ignore[index]
            tools=[FerramentaConsultaRH()],
        )

    @agent
    def especialista_tecnico(self) -> Agent:
        return Agent(
            config=self.agents_config["especialista_tecnico"],  # type: ignore[index]
            tools=[FerramentaConsultaTecnica()],
        )

    @task
    def tarefa_atendimento(self) -> Task:
        return Task(
            config=self.tasks_config["tarefa_atendimento"],  # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Onboarding Assistant Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            manager_llm="gpt-4o",
            verbose=True,
        )
