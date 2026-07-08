from typing import Type

from pydantic import BaseModel, Field
from crewai.tools import BaseTool

from dotenv import load_dotenv

load_dotenv()

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma


def criar_retriever(caminho_arquivo: str):
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        texto = f.read()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_text(texto)

    modelo_embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_store = Chroma.from_texts(chunks, modelo_embeddings)

    return vector_store.as_retriever(search_kwargs={"k": 2})


class ConsultaInput(BaseModel):
    """Input schema para as ferramentas de consulta."""

    pergunta: str = Field(
        ..., description="A pergunta do funcionário a ser pesquisada na documentação."
    )


class FerramentaConsultaRH(BaseTool):
    name: str = "Consulta Política de RH"
    description: str = (
        "Use esta ferramenta para responder perguntas sobre política de RH: "
        "horário de trabalho, home office, benefícios, férias e avaliação de desempenho."
    )
    args_schema: Type[BaseModel] = ConsultaInput

    def _run(self, pergunta: str) -> str:
        retriever = criar_retriever("docs/manual_rh.txt")
        chunks_relevantes = retriever.invoke(pergunta)
        contexto = "\n\n".join([chunk.page_content for chunk in chunks_relevantes])
        return contexto


class FerramentaConsultaTecnica(BaseTool):
    name: str = "Consulta Documentação Técnica"
    description: str = (
        "Use esta ferramenta para responder perguntas sobre ferramentas internas: "
        "VPN, Git, acesso a bancos de dados, CI/CD e política de senhas."
    )
    args_schema: Type[BaseModel] = ConsultaInput

    def _run(self, pergunta: str) -> str:
        retriever = criar_retriever("docs/docs_tecnicos.txt")
        chunks_relevantes = retriever.invoke(pergunta)
        contexto = "\n\n".join([chunk.page_content for chunk in chunks_relevantes])
        return contexto
