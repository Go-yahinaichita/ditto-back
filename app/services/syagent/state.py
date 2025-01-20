from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from typing import Annotated, List
from app.schemas.syagent import CurrentProfile, FutureProfile

class State(TypedDict):
    messages: Annotated[List, add_messages]
    current_profile: CurrentProfile
    future_profile: FutureProfile
