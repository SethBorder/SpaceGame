import utils, math, json
import bullet
from utils import Point, Vector
from bullet import Bullet
from mover import Mover

class Ship(Mover):
  
  def __init__(
    self,
    center = Point(utils.X_MAX / 2, utils.Y_MAX / 2),
    speed = Vector(0, 0),
    rotation = -math.pi/2,
    name = "testy mc testface",
    inputs = {
    "up": False,
    "down": False,
    "left": False,
    "right": False,
    "space": False},
    bullets = [],
    bullet_countdown = 0,
    bullet_recharge = 7,
    bullet_speed = 2.5,
    dead = False,
    death_countdown = 0,
    max_bullets = 7,
    size = 10/6,
    last_updated = None,
    leaving = False,
    score = 0,
    ):
    super().__init__(center, speed, rotation)
    # self.center = center
    # self.speed = speed
    # self.rotation = rotation
    self.name = name
    self.inputs = inputs
    self.bullets = list(bullets)
    self.bullet_countdown = bullet_countdown
    self.bullet_recharge = bullet_recharge
    self.bullet_speed = bullet_speed
    self.dead = dead
    self.death_countdown = death_countdown
    self.max_bullets = max_bullets
    self.size = size
    self.last_updated = utils.get_time() if last_updated == None else last_updated
    self.leaving = leaving
    self.score = score

  def from_dict(self, data):
    super().from_dict(data)
    bullet_list = [Bullet().from_dict(b) for b in data["bullets"]]

    self.name = data["name"]
    self.inputs = data["inputs"]
    self.bullets = bullet_list
    self.bullet_countdown = data["bullet_countdown"]
    self.bullet_recharge = data["bullet_recharge"]
    self.bullet_speed = data["bullet_speed"]
    self.dead = data["dead"]
    self.death_countdown = data["death_countdown"]
    self.max_bullets = data["max_bullets"]
    self.size = data["size"]
    self.last_updated = data["last_updated"]
    self.leaving = data["leaving"]
    self.score = data["score"]
    
    # For chaining.
    return self
  
    # return Ship(
    #   Point(data["center"]["x"], data["center"]["y"]),
    #   Vector(data["speed"]["x"], data["speed"]["y"]),
    #   data["rotation"],
    #   data["name"],
    #   data["inputs"],
    #   bullet_list,
    #   data["bullet_countdown"],
    #   data["bullet_recharge"],
    #   data["bullet_speed"],
    #   data["dead"],
    #   data["death_countdown"],
    #   data["max_bullets"],
    #   data["size"],
    #   data["last_updated"],
    #   data["leaving"],
    #   data["score"])
  
  def to_dict(self):
    inherited_entries = super().to_dict()
    raw_bullet_list = [b.to_dict() for b in self.bullets]
    new_entries = {
      "name": self.name,
      "inputs": self.inputs,
      "bullets": raw_bullet_list,
      "bullet_countdown": self.bullet_countdown,
      "bullet_recharge": self.bullet_recharge,
      "bullet_speed": self.bullet_speed,
      "dead": self.dead,
      "death_countdown": self.death_countdown,
      "max_bullets": self.max_bullets,
      "size": self.size,
      "last_updated": self.last_updated,
      "leaving": self.leaving,
      "score": self.score,
    }
    return {**new_entries, **inherited_entries}
  
  def fire(self):
    if self.bullet_countdown == 0 and not self.dead:
      self.bullets.append(self.createBullet())
      if len(self.bullets) > self.max_bullets:
        self.bullets.pop(0)

      self.bullet_countdown = self.bullet_recharge

  
  def createBullet(self):
    start_point = self.nose().copy()
    direction = self.rotation
    unit_vector_for_direction = Vector.unit_vector(direction)
    # The bullet will always fire straight, but if the ship is going fast the bullets should still outrun it.
    # To do this, we project the ships speed along the unit vector in the direction the bullet will be travelling.
    # Then we add the base bullet speed. This should only have noticable effect when travelling quickly and firing forwards.
    bullet_speed = self.speed.dot_product(unit_vector_for_direction) + self.bullet_speed
    speed = Vector.dir_mag(direction, bullet_speed)
    return Bullet(start_point, speed)

  def update_bullets(self):
    i = 0
    length = len(self.bullets)
    while i < length:
      if self.bullets[i].dead:
        self.bullets.pop(i)
        length -= 1
      else:
        self.bullets[i].update()
        i += 1
    
  def accelerate(self, amount):
    self.speed.add_in_direction(amount, self.rotation)
    
  def rotate(self, rads):
    self.rotation += rads
    
      
  # TODO: Use delta time for all called methods as well.
  def update(self, dt):
    if (self.dead):
      self.bullets = []
      self.bullet_countdown = self.bullet_recharge
      self.death_countdown = 3000
    
    if self.death_countdown > 0:
      self.death_countdown -= dt
      
    if self.bullet_countdown > 0:
      self.bullet_countdown -= 1
      
    super().move()
    self.update_bullets()
    
  def set_update_time(time):
    self.last_updated = time

  # def move(self):
  #   self.center.x += self.speed.x
  #   self.center.y += self.speed.y 
  #   self.center = utils.wrap_around(self.center)
    
  def getBoundingBox(self):
    backLeft = Point.rotate(Point(self.center.x - self.size, self.center.y + self.size), self.center, self.rotation)
    backRight = Point.rotate(Point(self.center.x + self.size, self.center.y + self.size), self.center, self.rotation)
    frontLeft = Point.rotate(Point(self.center.x - self.size, self.center.y - self.size), self.center, self.rotation)
    frontRight = Point.rotate(Point(self.center.x + self.size, self.center.y - self.size), self.center, self.rotation)
    return (frontLeft, frontRight, backRight, backLeft)
    
  def nose(self):
    return Point.rotate(Point(self.center.x + 2*self.size, self.center.y), self.center, self.rotation)
  
  
  
  
  
  
  
  
  
  
  