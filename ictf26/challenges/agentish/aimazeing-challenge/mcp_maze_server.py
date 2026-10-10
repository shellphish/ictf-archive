"""
MCP Server for Roguelike Maze CTF Challenge

Implements a procedurally generated maze with multiple room types.
The agent must navigate the maze, collect 4 puzzle pieces, and reach
the final room to obtain the flag.

Room types:
  - LEVER: Solve a riddle to pull the right lever (blue/pink/green).
           Doors are blocked until the correct lever is pulled.
           Wrong lever = lose 1 life.
  - TREASURE: Contains 1-3 gold coins (and possibly a puzzle piece).
              Collect ALL items at once.
  - CORRIDOR: Simple room with open doors in all 4 directions.
  - MERCHANT: Sells 1 puzzle piece for 5 gold coins.
  - FINAL: Bring all 4 puzzle pieces here to get the flag.

Every room has a door on each wall leading to the adjacent room in
the grid (except at maze borders). All doors are always open — the
only blocking mechanism is lever rooms where doors stay sealed until
the riddle is solved.

Rarity (rarest -> most common): merchant < treasure < corridor < lever
Minimum 20 gold coins distributed across treasure rooms.
"""

import json
import os
import random
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
FLAG = os.environ["FLAG_CHALLENGE"]
MAZE_WIDTH = 5
MAZE_HEIGHT = 5
TOTAL_ROOMS = MAZE_WIDTH * MAZE_HEIGHT  # 25
PLAYER_LIVES = 3
MIN_TOTAL_GOLD = 20
TOTAL_PUZZLE_PIECES_IN_TREASURES = 4
PUZZLE_PRICE = 5

# Room type distribution weights (rarity)
ROOM_WEIGHTS = {
    "lever": 40,
    "corridor": 30,
    "treasure": 20,
    "merchant": 10,
}

# ---------------------------------------------------------------------------
# Riddles for Lever Rooms
# ---------------------------------------------------------------------------
RIDDLES = [
    {
        "text": "The color of the sky on a clear day.",
        "answer": "blue",
        "hint": "Look up when it's not raining."
    },
    {
        "text": "The color of grass in springtime.",
        "answer": "green",
        "hint": "Meadows are covered in this color."
    },
    {
        "text": "The color of flamingos.",
        "answer": "pink",
        "hint": "An elegant tropical bird."
    },
    {
        "text": "The color of the deep ocean.",
        "answer": "blue",
        "hint": "Think of ocean waves."
    },
    {
        "text": "The color of mint leaves.",
        "answer": "green",
        "hint": "A refreshing aromatic herb."
    },
    {
        "text": "The color of cherry blossoms.",
        "answer": "pink",
        "hint": "Sakura in Japanese."
    },
    {
        "text": "Mix red and white. What color do you get?",
        "answer": "pink",
        "hint": "A delicate shade."
    },
    {
        "text": "Mix yellow and blue. What color do you get?",
        "answer": "green",
        "hint": "The color of nature."
    },
    {
        "text": "The lever color that shares its name with a melancholic music genre.",
        "answer": "blue",
        "hint": "A music genre born in the southern USA."
    },
    {
        "text": "The color of an emerald.",
        "answer": "green",
        "hint": "A precious gemstone."
    },
    {
        "text": "The color associated with the animated cartoon panther.",
        "answer": "pink",
        "hint": "A famous feline cartoon character."
    },
    {
        "text": "The color of our planet as seen from space.",
        "answer": "blue",
        "hint": "Earth is called the ___ planet."
    },
    {
        "text": "RGB(0, 255, 0) — what color does this represent?",
        "answer": "green",
        "hint": "The middle channel at maximum."
    },
    {
        "text": "RGB(0, 0, 255) — what color does this represent?",
        "answer": "blue",
        "hint": "The third channel at maximum."
    },
    {
        "text": "The color that rhymes with 'think'.",
        "answer": "pink",
        "hint": "P _ _ _"
    },
    {
        "text": "The lever whose color name has exactly 4 letters.",
        "answer": "blue",
        "hint": "B-L-U-E"
    },
    {
        "text": "The lever whose color name has exactly 5 letters.",
        "answer": "green",
        "hint": "G-R-E-E-N"
    },
    {
        "text": "The lever whose color name has exactly 4 letters and starts with P.",
        "answer": "pink",
        "hint": "P-I-N-K"
    },
]


# ---------------------------------------------------------------------------
# Maze Generation
# ---------------------------------------------------------------------------
class Room:
    def __init__(self, room_id: int, x: int, y: int, room_type: str):
        self.room_id = room_id
        self.x = x
        self.y = y
        self.room_type = room_type
        # Doors: direction -> target_room_id (full grid, always open)
        self.doors: dict[str, int] = {}
        # Room-specific state
        self.visited = False
        self.riddle = None              # lever rooms
        self.lever_pulled = False       # lever rooms: True once correct lever pulled
        self.gold_coins: int = 0        # treasure rooms: how many coins
        self.items_collected = False     # treasure rooms
        self.merchant_stock: int = 0    # merchant rooms: puzzle pieces available
        self.merchant_sold: bool = False

    def to_dict(self):
        d = {
            "room_id": self.room_id,
            "coordinates": f"({self.x}, {self.y})",
            "type": self.room_type,
            "visited": self.visited,
            "doors": {}
        }
        for direction, target_id in self.doors.items():
            d["doors"][direction] = {
                "direction": direction,
                "leads_to": target_id,
                "status": "open"
            }
        return d


class MazeGame:
    def __init__(self, seed=None):
        if seed is None:
            seed = int(time.time() * 1000) % (2**31)
        self.seed = seed
        self.rng = random.Random(seed)

        self.rooms: dict[int, Room] = {}
        self.player_pos: int = 0
        self.player_lives: int = PLAYER_LIVES
        self.inventory: dict[str, int] = {
            "gold_coin": 0,
            "puzzle_piece": 0,
        }
        self.game_over = False
        self.game_won = False

        self._generate_maze()

    def _coord_to_id(self, x, y):
        return y * MAZE_WIDTH + x

    def _id_to_coord(self, room_id):
        return room_id % MAZE_WIDTH, room_id // MAZE_WIDTH

    def _generate_maze(self):
        """Generate the full maze as a grid with doors on every wall."""
        room_ids = list(range(TOTAL_ROOMS))
        directions_deltas = {
            "north": (0, -1),
            "south": (0, 1),
            "east": (1, 0),
            "west": (-1, 0),
        }

        # --- Pick final room: far from start (0,0) ---
        final_candidates = []
        for rid in room_ids:
            x, y = self._id_to_coord(rid)
            if abs(x) + abs(y) >= (MAZE_WIDTH + MAZE_HEIGHT) // 2:
                final_candidates.append(rid)
        final_room_id = self.rng.choice(final_candidates) if final_candidates else TOTAL_ROOMS - 1

        # --- Assign room types ---
        remaining = [rid for rid in room_ids if rid != final_room_id and rid != 0]
        self.rng.shuffle(remaining)

        total_weight = sum(ROOM_WEIGHTS.values())
        type_assignments: dict[int, str] = {}
        for rid in remaining:
            roll = self.rng.randint(1, total_weight)
            cumulative = 0
            chosen = "lever"
            for rtype, w in ROOM_WEIGHTS.items():
                cumulative += w
                if roll <= cumulative:
                    chosen = rtype
                    break
            type_assignments[rid] = chosen

        # Start room is always a corridor
        self.rooms[0] = Room(0, 0, 0, "corridor")

        # Final room
        fx, fy = self._id_to_coord(final_room_id)
        self.rooms[final_room_id] = Room(final_room_id, fx, fy, "final")

        for rid, rtype in type_assignments.items():
            rx, ry = self._id_to_coord(rid)
            self.rooms[rid] = Room(rid, rx, ry, rtype)

        # --- Create full grid connectivity (door on every wall to valid neighbor) ---
        for rid in room_ids:
            rx, ry = self._id_to_coord(rid)
            for dname, (dx, dy) in directions_deltas.items():
                nx, ny = rx + dx, ry + dy
                if 0 <= nx < MAZE_WIDTH and 0 <= ny < MAZE_HEIGHT:
                    nid = self._coord_to_id(nx, ny)
                    self.rooms[rid].doors[dname] = nid

        # --- Distribute puzzle pieces across treasure rooms ---
        treasure_rooms = [rid for rid, room in self.rooms.items() if room.room_type == "treasure"]
        self.rng.shuffle(treasure_rooms)

        # If not enough treasure rooms, convert some lever rooms
        while len(treasure_rooms) < TOTAL_PUZZLE_PIECES_IN_TREASURES:
            lever_rooms = [rid for rid, room in self.rooms.items()
                          if room.room_type == "lever" and rid != 0 and rid != final_room_id]
            if lever_rooms:
                convert_id = self.rng.choice(lever_rooms)
                self.rooms[convert_id].room_type = "treasure"
                treasure_rooms.append(convert_id)
            else:
                break

        # Mark which treasure rooms have a puzzle piece
        puzzle_placed = 0
        puzzle_treasure_ids = set()
        for rid in treasure_rooms:
            if puzzle_placed >= TOTAL_PUZZLE_PIECES_IN_TREASURES:
                break
            puzzle_treasure_ids.add(rid)
            puzzle_placed += 1

        self._puzzle_treasure_ids = puzzle_treasure_ids

        # --- Assign gold coins to treasure rooms (1-3 each, min 20 total) ---
        gold_assignments: dict[int, int] = {}
        total_gold = 0
        for rid in treasure_rooms:
            coins = self.rng.randint(1, 3)
            gold_assignments[rid] = coins
            total_gold += coins

        # Top up if below minimum
        while total_gold < MIN_TOTAL_GOLD:
            rid = self.rng.choice(treasure_rooms)
            gold_assignments[rid] += 1
            total_gold += 1

        for rid in treasure_rooms:
            self.rooms[rid].gold_coins = gold_assignments.get(rid, 1)

        # --- Assign riddles to lever rooms ---
        lever_rooms = [rid for rid, room in self.rooms.items() if room.room_type == "lever"]
        available_riddles = list(RIDDLES)
        self.rng.shuffle(available_riddles)
        for i, rid in enumerate(lever_rooms):
            self.rooms[rid].riddle = available_riddles[i % len(available_riddles)]

        # --- Populate merchant stock (each sells exactly 1 puzzle piece) ---
        merchant_rooms = [rid for rid, room in self.rooms.items() if room.room_type == "merchant"]
        for rid in merchant_rooms:
            self.rooms[rid].merchant_stock = 1

        # Mark start as visited
        self.rooms[0].visited = True

    # -------------------------------------------------------------------
    # Helper: check if a lever room blocks passage
    # -------------------------------------------------------------------
    def _can_leave_room(self, room: Room) -> tuple[bool, str]:
        """Check if the player can leave the current room.
        Lever rooms block movement until the riddle is solved."""
        if room.room_type == "lever" and not room.lever_pulled:
            return False, (
                "The doors in this lever room are sealed! "
                "You must solve the riddle and pull the correct lever before you can leave."
            )
        return True, ""

    # -------------------------------------------------------------------
    # Game Actions
    # -------------------------------------------------------------------

    def look(self) -> dict:
        """Describe the current room."""
        room = self.rooms[self.player_pos]
        room.visited = True

        info = {
            "room_id": room.room_id,
            "coordinates": f"({room.x}, {room.y})",
            "type": room.room_type,
            "doors": {},
            "player": {
                "lives": self.player_lives,
                "inventory": dict(self.inventory),
                "position": room.room_id,
            }
        }

        for direction, target_id in room.doors.items():
            info["doors"][direction] = {
                "status": "open",
                "leads_to_room": target_id
            }

        # Room-specific info
        if room.room_type == "lever":
            if room.lever_pulled:
                info["lever_status"] = "already_pulled"
                info["description"] = "The levers have already been pulled. The doors are open and you may leave."
            else:
                info["riddle"] = room.riddle["text"]
                info["hint"] = room.riddle["hint"]
                info["available_levers"] = ["blue", "pink", "green"]
                info["description"] = (
                    "A room with three colored levers: BLUE, PINK and GREEN. "
                    "A sign displays a riddle. Pull the correct lever to unseal the doors. "
                    "Warning: pulling the wrong lever costs you a life!"
                )
                # Show doors as sealed
                for d in info["doors"]:
                    info["doors"][d]["status"] = "sealed"

        elif room.room_type == "treasure":
            if room.items_collected:
                info["description"] = "The treasure room is empty. Everything has already been collected."
                info["treasure"] = {"gold_coins": 0, "has_puzzle_piece": False}
            else:
                has_puzzle = room.room_id in self._puzzle_treasure_ids
                info["treasure"] = {
                    "gold_coins": room.gold_coins,
                    "has_puzzle_piece": has_puzzle,
                }
                items_desc = f"{room.gold_coins} gold coin(s)"
                if has_puzzle:
                    items_desc += " and a PUZZLE PIECE"
                info["description"] = (
                    f"A treasure room! You find {items_desc}. "
                    "Use 'collect_treasure' to grab everything."
                )

        elif room.room_type == "corridor":
            info["description"] = (
                f"A simple corridor with {len(room.doors)} door(s). All doors are open."
            )

        elif room.room_type == "merchant":
            if room.merchant_sold or room.merchant_stock <= 0:
                info["merchant_stock"] = {}
                info["description"] = "A mysterious merchant greets you, but has nothing left to sell."
            else:
                info["merchant_stock"] = {"puzzle_piece": room.merchant_stock}
                info["prices"] = {"puzzle_piece": PUZZLE_PRICE}
                info["description"] = (
                    f"A mysterious merchant greets you. "
                    f"For sale: Puzzle Piece = {PUZZLE_PRICE} gold coins."
                )

        elif room.room_type == "final":
            info["description"] = (
                "The final room! An ancient altar stands at the center, waiting for 4 puzzle pieces. "
                f"You have {self.inventory['puzzle_piece']}/4 puzzle pieces."
            )
            if self.inventory["puzzle_piece"] >= 4:
                info["description"] += " You seem to have all the pieces! Use 'assemble_puzzle' to complete the challenge."

        return info

    def move(self, direction: str) -> dict:
        """Move to an adjacent room through a door."""
        if self.game_over:
            return {"success": False, "error": "The game is over."}

        direction = direction.lower().strip()
        room = self.rooms[self.player_pos]

        # Check if lever room blocks us
        can_leave, reason = self._can_leave_room(room)
        if not can_leave:
            return {"success": False, "error": reason}

        if direction not in room.doors:
            available = list(room.doors.keys())
            return {
                "success": False,
                "error": f"There is no door to the '{direction}'. Available directions: {available}"
            }

        target_id = room.doors[direction]
        self.player_pos = target_id
        new_room = self.rooms[self.player_pos]
        new_room.visited = True

        return {
            "success": True,
            "message": f"You moved {direction}.",
            "new_room": self.look()
        }

    def pull_lever(self, color: str) -> dict:
        """Pull a lever in a lever room."""
        if self.game_over:
            return {"success": False, "error": "The game is over."}

        room = self.rooms[self.player_pos]
        if room.room_type != "lever":
            return {"success": False, "error": "There are no levers in this room."}

        if room.lever_pulled:
            return {"success": False, "error": "The levers have already been pulled."}

        color = color.lower().strip()
        if color not in ["blue", "pink", "green"]:
            return {"success": False, "error": f"Invalid color: '{color}'. Choose from: blue, pink, green."}

        correct = room.riddle["answer"]
        if color == correct:
            room.lever_pulled = True
            return {
                "success": True,
                "message": f"Correct! The {color} lever was the right one. The doors are now unsealed!",
                "lives": self.player_lives
            }
        else:
            self.player_lives -= 1
            if self.player_lives <= 0:
                self.game_over = True
                return {
                    "success": False,
                    "message": f"Wrong! The correct lever was {correct}. You lost your last life!",
                    "lives": 0,
                    "game_over": True
                }
            return {
                "success": False,
                "message": f"Wrong! You lost a life. Remaining lives: {self.player_lives}. Try again!",
                "lives": self.player_lives
            }

    def collect_treasure(self) -> dict:
        """Collect all items from a treasure room."""
        if self.game_over:
            return {"success": False, "error": "The game is over."}

        room = self.rooms[self.player_pos]
        if room.room_type != "treasure":
            return {"success": False, "error": "You are not in a treasure room."}

        if room.items_collected:
            return {"success": False, "error": "This treasure room has already been looted."}

        collected = {}
        # Collect gold
        if room.gold_coins > 0:
            self.inventory["gold_coin"] += room.gold_coins
            collected["gold_coins"] = room.gold_coins

        # Collect puzzle piece if present
        if room.room_id in self._puzzle_treasure_ids:
            self.inventory["puzzle_piece"] += 1
            collected["puzzle_piece"] = 1

        room.items_collected = True

        return {
            "success": True,
            "message": f"You collected: {collected}",
            "inventory": dict(self.inventory)
        }

    def buy_item(self, item: str) -> dict:
        """Buy an item from a merchant."""
        if self.game_over:
            return {"success": False, "error": "The game is over."}

        room = self.rooms[self.player_pos]
        if room.room_type != "merchant":
            return {"success": False, "error": "You are not in a merchant room."}

        item = item.lower().strip()

        if item != "puzzle_piece":
            return {"success": False, "error": f"The merchant does not sell '{item}'. Only 'puzzle_piece' is available."}

        if room.merchant_sold or room.merchant_stock <= 0:
            return {"success": False, "error": "The merchant has nothing left to sell."}

        if self.inventory["gold_coin"] < PUZZLE_PRICE:
            return {
                "success": False,
                "error": f"Not enough gold coins. Cost: {PUZZLE_PRICE}, you have: {self.inventory['gold_coin']}"
            }

        self.inventory["gold_coin"] -= PUZZLE_PRICE
        self.inventory["puzzle_piece"] += 1
        room.merchant_stock -= 1
        room.merchant_sold = True

        return {
            "success": True,
            "message": f"You bought a puzzle piece for {PUZZLE_PRICE} gold coins.",
            "inventory": dict(self.inventory)
        }

    def assemble_puzzle(self) -> dict:
        """Attempt to assemble the puzzle in the final room."""
        if self.game_over:
            return {"success": False, "error": "The game is over."}

        room = self.rooms[self.player_pos]
        if room.room_type != "final":
            return {"success": False, "error": "You are not in the final room."}

        if self.inventory["puzzle_piece"] >= 4:
            self.game_won = True
            self.game_over = True
            return {
                "success": True,
                "message": (
                    "YOU WON! The 4 puzzle pieces fit perfectly onto the altar. "
                    "A blinding light reveals the flag!"
                ),
                "flag": FLAG
            }
        else:
            return {
                "success": False,
                "error": f"You are missing pieces! You have {self.inventory['puzzle_piece']}/4 puzzle pieces.",
                "hint": "Explore the maze to find puzzle pieces in treasure rooms or buy them from merchants."
            }

    def get_map(self) -> dict:
        """Return a map of visited rooms only."""
        visited_rooms = {}
        for rid, room in self.rooms.items():
            if room.visited:
                visited_rooms[str(rid)] = room.to_dict()
        return {
            "visited_rooms": visited_rooms,
            "total_rooms": TOTAL_ROOMS,
            "player_position": self.player_pos,
            "maze_size": f"{MAZE_WIDTH}x{MAZE_HEIGHT}"
        }

    def get_status(self) -> dict:
        """Return current game status."""
        return {
            "player": {
                "lives": self.player_lives,
                "inventory": dict(self.inventory),
                "position": self.player_pos,
                "coordinates": f"({self.rooms[self.player_pos].x}, {self.rooms[self.player_pos].y})"
            },
            "game_over": self.game_over,
            "game_won": self.game_won,
            "rooms_visited": sum(1 for r in self.rooms.values() if r.visited),
            "total_rooms": TOTAL_ROOMS
        }


# ---------------------------------------------------------------------------
# Global Game Instance (one per server session)
# ---------------------------------------------------------------------------
GAME: MazeGame | None = None


def get_game() -> MazeGame:
    global GAME
    if GAME is None:
        seed_env = os.environ.get("MAZE_SEED")
        seed = int(seed_env) if seed_env else None
        GAME = MazeGame(seed=seed)
    return GAME


# ---------------------------------------------------------------------------
# JSON-RPC Handler
# ---------------------------------------------------------------------------
class MazeRPCHandler(BaseHTTPRequestHandler):

    METHODS = {
        "look": lambda params: get_game().look(),
        "move": lambda params: get_game().move(params.get("direction", "")),
        "pull_lever": lambda params: get_game().pull_lever(params.get("color", "")),
        "collect_treasure": lambda params: get_game().collect_treasure(),
        "buy_item": lambda params: get_game().buy_item(params.get("item", "")),
        "assemble_puzzle": lambda params: get_game().assemble_puzzle(),
        "get_map": lambda params: get_game().get_map(),
        "get_status": lambda params: get_game().get_status(),
    }

    def do_POST(self):
        if self.path != "/rpc":
            self._send_json({"error": "Not found"}, 404)
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            request = json.loads(body)
        except json.JSONDecodeError:
            self._send_json({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None})
            return

        method = request.get("method", "")
        params = request.get("params", {})
        req_id = request.get("id", 1)

        # MCP tools/call convention
        if method == "tools/call":
            tool_name = params.get("name", "")
            tool_args = params.get("arguments", {})
            if tool_name in self.METHODS:
                try:
                    result = self.METHODS[tool_name](tool_args)
                    self._send_json({
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]
                        }
                    })
                except Exception as e:
                    self._send_json({
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {"code": -32603, "message": str(e)}
                    })
            else:
                self._send_json({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                })

        elif method == "tools/list":
            tools = []
            tool_schemas = {
                "look": {
                    "description": "Observe the current room and its doors",
                    "arguments": []
                },
                "move": {
                    "description": "Move in a direction (north/south/east/west)",
                    "arguments": [
                        {"name": "direction", "type": "str", "required": True,
                         "description": "Direction: north, south, east, west"}
                    ]
                },
                "pull_lever": {
                    "description": "Pull a colored lever (blue/pink/green) in a lever room",
                    "arguments": [
                        {"name": "color", "type": "str", "required": True,
                         "description": "Color: blue, pink, green"}
                    ]
                },
                "collect_treasure": {
                    "description": "Collect all items from a treasure room",
                    "arguments": []
                },
                "buy_item": {
                    "description": "Buy an item from the merchant",
                    "arguments": [
                        {"name": "item", "type": "str", "required": True,
                         "description": "Item to buy: puzzle_piece (costs 5 gold)"}
                    ]
                },
                "assemble_puzzle": {
                    "description": "Assemble the puzzle in the final room (need 4 pieces)",
                    "arguments": []
                },
                "get_map": {
                    "description": "Show the map of visited rooms",
                    "arguments": []
                },
                "get_status": {
                    "description": "Show the current player status",
                    "arguments": []
                },
            }
            for name, schema in tool_schemas.items():
                tools.append({"name": name, **schema})

            self._send_json({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": tools}
            })
        else:
            self._send_json({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Unknown method: {method}"}
            })

    def do_GET(self):
        if self.path == "/health":
            self._send_json({"status": "healthy", "game_active": GAME is not None})
        elif self.path == "/mcp/status":
            self._send_json({"status": "running", "tools": list(self.METHODS.keys())})
        else:
            self._send_json({"error": "Use POST /rpc for JSON-RPC calls"}, 400)

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def log_message(self, format, *args):
        pass


def main():
    import argparse
    parser = argparse.ArgumentParser(description="MCP Maze Server")
    parser.add_argument("--port", type=int, default=7001)
    args = parser.parse_args()

    # Pre-initialize game
    game = get_game()
    total_gold = sum(r.gold_coins for r in game.rooms.values() if r.room_type == "treasure")
    print(f"Maze generated (seed={game.seed}, {TOTAL_ROOMS} rooms)")
    print(f"Final room: {[rid for rid, r in game.rooms.items() if r.room_type == 'final'][0]}")
    print(f"Treasure rooms: {sum(1 for r in game.rooms.values() if r.room_type == 'treasure')}")
    print(f"  - with puzzle piece: {len(game._puzzle_treasure_ids)}")
    print(f"  - total gold coins: {total_gold}")
    print(f"Merchant rooms: {sum(1 for r in game.rooms.values() if r.room_type == 'merchant')}")
    print(f"Lever rooms: {sum(1 for r in game.rooms.values() if r.room_type == 'lever')}")

    server = HTTPServer(("0.0.0.0", args.port), MazeRPCHandler)
    print(f"MCP Maze Server listening on port {args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()