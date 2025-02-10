from typing import Annotated

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from app.schemas.syagent import FutureProfile


class SimState(TypedDict):
    messages: Annotated[list, add_messages]
    future_profile: FutureProfile
