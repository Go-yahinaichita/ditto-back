from fastapi import FastAPI, Request
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain_google_vertexai import ChatVertexAI


def setup_runnable(app: FastAPI) -> None:
    model = ChatVertexAI(
        model="gemini-1.5-flash-001",
        temperature=0,
        max_tokens=None,
        max_retries=6,
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You're a very knowledgeable historian who provides accurate and eloquent answers to historical questions.",
            ),
            ("human", "{question}"),
        ]
    )
    runnable = prompt | model | StrOutputParser()
    app.state.runnable = runnable


async def get_runnable(request: Request) -> Runnable:
    runnable: Runnable = request.app.state.runnable
    return runnable
