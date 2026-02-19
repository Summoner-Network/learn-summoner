import argparse, json, asyncio
from typing import Any, Optional

from summoner.client import SummonerClient
from summoner.protocol import Test, Move, Stay, Event, Direction, Node
from summoner.visionary import ClientFlowVisualizer

state_lock = asyncio.Lock()

relations = {}

import random
AGENT_ID = f"ChangeMe_Agent_10_{random.randint(0,1000)}"
viz = ClientFlowVisualizer(title=f"{AGENT_ID} Graph", port=random.randint(7777,8887))

client = SummonerClient(name=AGENT_ID)

client_flow = client.flow().activate()
client_flow.add_arrow_style(stem="-", brackets=("[", "]"), separator=",", tip=">")
Trigger = client_flow.triggers()


@client.hook(direction=Direction.RECEIVE, priority=0)
async def validate(msg: Any) -> Optional[dict]:
    if not (isinstance(msg, dict) and "remote_addr" in msg and "content" in msg): return
    address: str = msg["remote_addr"]
    content: Any = msg["content"]
    print(content)
    if not isinstance(content, dict): return
    if content.get("to", "") not in [None, AGENT_ID]: return
    if "from" not in content:
        client.logger.info(f"[hook:recv] missing content.from")
        return
    return content

@client.hook(direction=Direction.RECEIVE, priority=1)
async def check_sender(content: dict) -> Optional[dict]:
    if  any(s == content.get("from","")[:len(s)] for s in [
                                "ChangeMe_Agent_6",
                                "ChangeMe_Agent_7",
                                "ChangeMe_Agent_8",
                                "ChangeMe_Agent_9",
                                "ChangeMe_Agent_10",
                            ]): 
        return content
    else:
        client.logger.info(f"[hook:recv] reject 'from':{content.get('from')} | 'type':{content.get('type')}")


@client.upload_states()
async def upload_states(msg: Any) -> list[str]:
    global relations
    sender_id = msg.get("from")
    if not sender_id: return
    async with state_lock:
        relations.setdefault(sender_id, "register")
        viz.push_states(relations)
    return { sender_id: relations[sender_id] }


@client.receive(route="register --> contact")
async def on_register(msg: Any) -> Event: 
    if msg["message"] == "Hello": 
        return Move(Trigger.ok)

@client.receive(route="register --> ban")
async def on_register(msg: Any) -> Event: 
    if msg["message"] == "I don't like you": 
        return Move(Trigger.ok)

@client.receive(route="contact --> friend")
async def on_register(msg: Any) -> Event: 
    if msg["message"] == "I like you": 
        return Move(Trigger.ok)


@client.download_states()
async def download_states(possible_states: dict[str, list[Node]]) -> None:
    global relations
    for sender_id, sender_states in possible_states.items():
        states = [s for s in sender_states if str(s) != str(relations[sender_id])]
        if states:
            async with state_lock:
                relations[sender_id] = states[0]
        viz.push_states(relations)


@client.receive(route="register")
async def on_register(msg: Any) -> Event: 
    client.logger.info(msg)
    return Test(Trigger.ok)

@client.receive(route="contact")
async def on_contact(msg: Any) -> Event: 
    client.logger.info(msg)
    return Test(Trigger.ok)

@client.receive(route="friend")
async def on_friend(msg: Any) -> Event: 
    client.logger.info(msg)
    return Test(Trigger.ok)

@client.receive(route="ban")
async def on_ban(msg: Any) -> Event: 
    client.logger.info(msg)
    return Test(Trigger.ok)

@client.send(route="clock")
async def send_on_clock() -> str: 
    async with state_lock:
        viz.push_states(["clock"])
    await asyncio.sleep(3)
    return {"message": "Hello", "to": None}

@client.hook(direction=Direction.SEND)
async def sign(msg: Any) -> Optional[dict]:
    client.logger.info(f"[hook:send] sign {AGENT_ID}")
    if isinstance(msg, str): msg = {"message": msg}
    if not isinstance(msg, dict): return
    msg.update({"from": AGENT_ID})
    return msg

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a Summoner client with a specified config.")
    parser.add_argument('--config', dest='config_path', required=False, help='The relative path to the config file (JSON) for the client (e.g., --config configs/client_config.json)')
    args = parser.parse_args()

    # Start visual window (browser) and build graph from dna
    viz.attach_logger(client.logger)
    viz.start(open_browser=True)
    viz.set_graph_from_dna(json.loads(client.dna()), parse_route=client_flow.parse_route)
    viz.push_states(["register"])

    client.run(host = "__server__", port = 8888, config_path=args.config_path or "configs/client_config.json")
