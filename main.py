"""Minimal A2A protocol server: greets whoever it's asked to greet."""

import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import add_a2a_routes_to_fastapi, create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH, DEFAULT_RPC_URL, TransportProtocol

from agent_executor import GreeterAgentExecutor

PUBLIC_URL = os.environ.get("A2A_PUBLIC_URL", "http://localhost:8000")

AGENT_CARD = AgentCard(
    name="Greeter Agent",
    description="Proof-of-concept A2A agent that replies 'Olá <name>' for a given name.",
    version="1.0.0",
    supported_interfaces=[
        AgentInterface(
            url=f"{PUBLIC_URL}{DEFAULT_RPC_URL}",
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
            description="Receives a name and replies 'Ola <name>'.",
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
    agent_card_routes=create_agent_card_routes(AGENT_CARD, card_url=AGENT_CARD_WELL_KNOWN_PATH),
    jsonrpc_routes=create_jsonrpc_routes(request_handler, DEFAULT_RPC_URL, enable_v0_3_compat=True),
)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
