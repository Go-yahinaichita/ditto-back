from typing import Annotated, List

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from app.schemas.syagent import CurrentProfile, FutureProfile


class State(TypedDict):
    messages: Annotated[List, add_messages]
    current_prof: CurrentProfile
    future_prof: FutureProfile
