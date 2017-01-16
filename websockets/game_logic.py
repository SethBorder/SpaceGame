import json, random, string, math, time, threading
from player_ship import Ship
from asteroid import Asteroid
import utils

# This class runs the actual asteroids game logic.
# Internally the coordinate system used is 200x100, so the client has to convert.
# The loop is started in socket_server.py, and runs as long as the server is up.
# On create:
#   - The client will provide a username, and the server will create a game_id.
#   - The server will then return the inital state of the game space.
# TODO: Add a unique ship identifier to avoid collisions and prevent spoofing.
# TODO: Require usernames to be unique.
# On update:
#   - The client will provide their game_id and username, which uniquely identify
#     their ship, along with information on inputs.
#   - The server will then update the ship's input status, and send back the current
#     game state.

lock = threading.Lock()

class AsteroidsGame(object):
  ACCELERATION = 0.005;
  TURN_SPEED = 0.0075;
  SHIP_TOP_SPEED = 5;
  
  def __init__(self):
    self.games = {}
    
  def loop(self):
    while True:
      start_time = utils.get_time()
      for game_id in list(self.games):
        self.increment_game(game_id)
      end_time = utils.get_time()
      # The goal here is 17ms loops, which corresponds to 60fps, which is the speed that
      # the client updates at, so there's not a lot of reason to update faster. However,
      # if we get behind the algorithm uses delta time, so it will keep up, it just might
      # get jerkier.
      sleep_time = 17 - (end_time - start_time)
      if sleep_time > 0:
        time.sleep(sleep_time / 1000)

  def input(self, raw_data):
    data = json.loads(raw_data)
    state = data['gamestate']
    if state == "new":
      return self.create_new_game(data)
    else:
      self.update_player(data)
      game_id = data["game_id"]
      with lock:
        return json.dumps(self.games[game_id])
    
  def create_new_game(self, data):
    game_key = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))
    username = data["name"]
    ship = self.new_ship(username)
    milli_time = utils.get_time()
    print("Made ship!")
    asteroid = self.make_asteroid(1, 2)
    print("Made asteroid!")
    game_state = {
      "game_id": game_key,
      "ships": [
        ship,
      ],
      "last_updated": milli_time,
      "asteroids": [
        asteroid
      ]
    }
    with lock:
      self.games[game_key] = game_state
    return json.dumps(game_state)
  
  def update_player(self, data):
    game_id = data["game_id"]
    name = data["name"]
    with lock:
      game_data = self.games[game_id]
    # List comprehension. Grab the first (only) element in the ships array
    # where the name matches the username.
    # TODO: Switch to using unique ids for the ships.
    ship_index = -1
    raw_ships = game_data["ships"]
    for i in range(0, len(raw_ships)):
      if raw_ships[i]["name"] == name:
        ship_index = i
        break
    if ship_index == -1:
      raise Exception("Failed to find ship!")
    ship_dict = raw_ships[i]
    ship_dict["inputs"] = data["keys"]
    with lock:
      self.games[game_id]["ships"][i] = ship_dict
  
  def increment_game(self, game_id):
    with lock:
      game_state = self.games[game_id]
    time_delta = utils.get_time() - game_state["last_updated"]
    raw_ships = game_state["ships"]
    raw_asteroids = game_state["asteroids"]
    ships = [Ship.from_dict(s) for s in raw_ships]
    asteroids = [Asteroid.from_dict(a) for a in raw_asteroids]
    for ship in ships:
      AsteroidsGame.move_ship(ship, time_delta)
    for asteroid in asteroids:
      asteroid.update()
    raw_ships = [s.to_dict() for s in ships]
    raw_asteroids = [a.to_dict() for a in asteroids]
    
    game_state["ships"] = raw_ships
    game_state["asteroids"] = raw_asteroids
    game_state["last_updated"] = utils.get_time()
    with lock:
      self.games[game_id] = game_state
    return json.dumps(game_state)
  
  @staticmethod
  def move_ship(ship, dt):
    # TODO: Potentially move into ship class.
    if ship.inputs["up"]:
      ship.accelerate(AsteroidsGame.ACCELERATION * dt)
    if ship.inputs["down"]:
      ship.accelerate(-AsteroidsGame.ACCELERATION * dt)
    if ship.inputs["left"]:
      ship.rotate(-AsteroidsGame.TURN_SPEED * dt)
    if ship.inputs["right"]:
      ship.rotate(AsteroidsGame.TURN_SPEED * dt)
    if ship.inputs["space"]:
      ship.fire()
      pass
    ship.move()
    return ship
  
  @staticmethod
  def new_ship(username):
    ship_dict = Ship(name=username).to_dict()
    print(ship_dict)
    return ship_dict
  
  @staticmethod
  def make_asteroid(uid, stage):
    x = random.randint(0, 200)
    y = random.randint(0, 100)
    #TODO: Make this actually avoid the ship, so we can simply add new asteroids to start a new level.
    while 40 < x < 60:
      x = random.randint(0, 100)
    while 40 < y < 60:
      y = random.randint(0, 100)
      
    direction = random.random() * 2 * math.pi
    speed = random.random() / 5
    dx = math.cos(direction) * speed
    dy = math.sin(direction) * speed
    size = 8 + random.random() * 2
    num_children = random.randint(2, 3)
    return {
        "id": uid,
        "center": {
          "x": x,
          "y": y
          },
        "speed": {
          "x": dx,
          "y": dy
          },
        "size": size,
        "stage": 3,
        "num_children": num_children,
        "rotation": 0,
        "dead": False,
    }
  
  
    
    
    
    
    
    
    
    
    
    
  