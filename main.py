"""Minimal A2A protocol server: greets whoever it's asked to greet."""

import logging
import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

from a2a.compat.v0_3.types import AgentCapabilities as AgentCapabilitiesV0_3
from a2a.compat.v0_3.types import AgentCard as AgentCardV0_3
from a2a.compat.v0_3.types import AgentSkill as AgentSkillV0_3
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import add_a2a_routes_to_fastapi, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH, DEFAULT_RPC_URL, TransportProtocol

from agent_executor import GreeterAgentExecutor

PUBLIC_URL = os.environ.get("A2A_PUBLIC_URL", "http://localhost:8000")
RPC_URL = f"{PUBLIC_URL}{DEFAULT_RPC_URL}"

AGENT_CARD = AgentCard(
    name="Greeter Agent",
    description="Proof-of-concept A2A agent that replies 'Olá <name>' for a given name.",
    version="1.0.0",
    supported_interfaces=[
        AgentInterface(
            url=RPC_URL,
            protocol_binding=TransportProtocol.JSONRPC,
            protocol_version="1.0",
        )
    ],
    capabilities=AgentCapabilities(streaming=False, push_notifications=False),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    skills=[
        AgentSkill(
            id="greet",
            name="Greet",
            description="Receives a name and replies 'Olá <name>'.",
            tags=["greeting", "demo"],
            examples=["Nelson"],
        )
    ],
)

# Served at the well-known agent-card path instead of AGENT_CARD above: ODC's A2A
# client validates against the v0.3 schema (requires a top-level "url" field),
# which the v1.0-native AgentCard/AgentInterface shape doesn't have.
AGENT_CARD_V0_3 = AgentCardV0_3(
    name="Greeter Agent",
    description="Proof-of-concept A2A agent that replies 'Olá <name>' for a given name.",
    url=RPC_URL,
    version="1.0.0",
    capabilities=AgentCapabilitiesV0_3(streaming=False, pushNotifications=False),
    defaultInputModes=["text/plain"],
    defaultOutputModes=["text/plain"],
    skills=[
        AgentSkillV0_3(
            id="greet",
            name="Greet",
            description="Receives a name and replies 'Olá <name>'.",
            tags=["greeting", "demo"],
            examples=["Nelson"],
        )
    ],
)

request_handler = DefaultRequestHandler(
    agent_executor=GreeterAgentExecutor(),
    task_store=InMemoryTaskStore(),
    agent_card=AGENT_CARD,
)

app = FastAPI(title="A2A Greeter Agent")
add_a2a_routes_to_fastapi(
    app,
    jsonrpc_routes=create_jsonrpc_routes(request_handler, DEFAULT_RPC_URL, enable_v0_3_compat=True),
)


@app.get(AGENT_CARD_WELL_KNOWN_PATH)
async def agent_card() -> dict:
    return AGENT_CARD_V0_3.model_dump(by_alias=True, exclude_none=True)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
