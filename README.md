# Onboarding Assistant — Assistente de Onboarding com IA Multi-Agente

Assistente inteligente que responde às dúvidas mais comuns de funcionários recém-contratados durante o **onboarding**, consultando a documentação oficial da empresa (políticas de RH e documentação técnica interna) em vez de depender do conhecimento genérico do modelo.

O sistema usa uma arquitetura **multi-agente** com **RAG (Retrieval-Augmented Generation)**: um agente coordenador recebe a pergunta, decide qual especialista é responsável por respondê-la e delega a tarefa. Cada especialista busca a resposta diretamente na documentação real da empresa, o que reduz alucinações e garante respostas ancoradas em fontes oficiais.

## O problema que resolve

Todo funcionário novo faz as mesmas perguntas nas primeiras semanas — "qual o horário de trabalho?", "como configuro a VPN?", "como funciona o home office?". Isso consome tempo do RH e dos times técnicos. Este projeto centraliza esse atendimento em um assistente que responde 24/7, sempre com base na documentação vigente.

## Como funciona (arquitetura)

```
Pergunta do funcionário
        │
        ▼
   API (FastAPI)  ──►  Flow (CrewAI)
                            │
                            ▼
                 Agente Coordenador (manager)
                    roteia a pergunta
                   ┌────────┴────────┐
                   ▼                 ▼
        Especialista de RH   Especialista Técnico
                   │                 │
                   ▼                 ▼
             RAG sobre          RAG sobre
           manual_rh.txt     docs_tecnicos.txt
        (embeddings + busca vetorial no ChromaDB)
```

1. **Entrada** — A pergunta chega via endpoint HTTP (`POST /perguntar`) exposto com FastAPI.
2. **Orquestração** — Um `Flow` do CrewAI recebe a pergunta e dispara a *crew*.
3. **Roteamento** — Uma *crew* com processo **hierárquico** usa um agente gerente (`gpt-4o`) que classifica a pergunta e delega ao especialista correto.
4. **Especialistas** — Dois agentes especializados:
   - **Especialista de RH**: horário de trabalho, home office, benefícios, férias, avaliação de desempenho.
   - **Especialista Técnico**: VPN, Git, acesso a bancos de dados, CI/CD, política de senhas.
5. **Busca na documentação (RAG)** — Cada especialista tem uma ferramenta própria que:
   - Fatia o documento em *chunks* (`RecursiveCharacterTextSplitter`);
   - Gera *embeddings* com o modelo `text-embedding-3-small` da OpenAI;
   - Indexa e busca os trechos mais relevantes no **ChromaDB**;
   - Devolve apenas o contexto relevante para o agente formular a resposta.
6. **Guardrails** — Se a pergunta estiver **fora do escopo** (não é RH nem técnica), o assistente recusa educadamente em vez de "inventar" uma resposta com conhecimento geral do LLM.

## Decisões técnicas que vale destacar

- **Separação por especialista + RAG isolado por domínio**: cada agente consulta apenas a sua base de conhecimento, o que melhora a precisão e evita respostas cruzadas indevidas.
- **Processo hierárquico com agente gerente**: o roteamento não é feito por `if/else` manual, mas por um agente que interpreta a intenção da pergunta.
- **Combate a alucinações**: as instruções (backstory + task) exigem que os agentes só respondam com base na documentação oficial, e o *guardrail* de fora de escopo evita respostas fora do domínio.
- **API pronta para integração**: exposta via FastAPI, o assistente pode ser plugado em um chat interno, Slack, intranet, etc.

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Orquestração de agentes | [CrewAI](https://crewai.com) (Flows + Crews) |
| LLM / Embeddings | OpenAI (`gpt-4o`, `text-embedding-3-small`) |
| RAG / Busca vetorial | LangChain + ChromaDB |
| API | FastAPI + Uvicorn |
| Gerência de dependências | uv |
| Linguagem | Python 3.10+ |

## Como rodar

Pré-requisitos: Python >=3.10 <3.14 e uma `OPENAI_API_KEY`.

```bash
# 1. Instalar o uv (se ainda não tiver)
pip install uv

# 2. Instalar as dependências
crewai install

# 3. Configurar a chave da OpenAI no arquivo .env
#    OPENAI_API_KEY=sua_chave_aqui
```

### Via linha de comando

```bash
crewai run
```

Executa o fluxo com uma pergunta de exemplo e imprime a resposta final no terminal.

### Via API

```bash
uvicorn api:app --reload
```

Depois é só enviar uma pergunta:

```bash
curl -X POST http://localhost:8000/perguntar \
  -H "Content-Type: application/json" \
  -d '{"pergunta": "Como configuro a VPN?"}'
```

Resposta:

```json
{ "resposta": "..." }
```

## Estrutura do projeto

```
.
├── api.py                          # Endpoint FastAPI
├── docs/
│   ├── manual_rh.txt               # Base de conhecimento de RH
│   └── docs_tecnicos.txt           # Base de conhecimento técnica
└── src/onboarding_assistant_v2/
    ├── main.py                     # Flow do CrewAI (entrada e orquestração)
    ├── tools/custom_tool.py        # Ferramentas de RAG (RH e Técnica)
    └── crews/onboarding_crew/
        ├── onboarding_crew.py      # Definição da crew e dos agentes
        └── config/
            ├── agents.yaml         # Papéis, objetivos e comportamento dos agentes
            └── tasks.yaml          # Tarefa de atendimento e regras de escopo
```

## Possíveis evoluções

- Persistir o índice vetorial (hoje é reconstruído a cada consulta) para reduzir latência e custo.
- Adicionar novos domínios de conhecimento (ex.: financeiro, jurídico) criando novos especialistas.
- Histórico de conversa e memória para perguntas de acompanhamento.
- Observabilidade (logs, métricas e avaliação da qualidade das respostas).
