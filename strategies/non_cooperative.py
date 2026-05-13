from environment import TerrainType, AntPerception, Direction
from ant import AntAction, AntStrategy

import random
import math


class NonCooperativeStrategy(AntStrategy):
    """
    # TODO: Insert your code here
    """


    def __init__(self):
        """Initialize the strategy with last action tracking"""

        self.memory = {
            "colony_position": (0, 0),  # storing the absolute position of the colony we consider to be 0,0, doesn't have to be in memory. It is a fixed variable.
            # The external code clearly does not use the same coordinates but if we use our coordinates only in our code it should not break everything (I hope)
            "ant_memory": {},
        }


    def initialize_ant_memory(self, ant_id):
        """Initialize memory for a specific ant"""
        self.memory["ant_memory"][ant_id] = {
            "ant_position": (0, 0),  # is at the colony in the beginning
            "food_positions": [], # list of absolute positions of food the ant has seen,
            "current_action": "Scatter",
            # Can be "Goto", "Scan", "Scatter", "Spy" (going to the colony -> goto with the position of the colony)
            "goto_destination": None, # absolute position of the destination when the current action is "Goto"
            "spy_pause": 0, # number of steps during which the ant cannot reinitiate a spy action, to avoid too much spying and allow time to find food after spying
        }

        # add obstacles later when implementing a more complex strategy


    def decide_action(self, perception: AntPerception) -> AntAction:
        """Decide an action based on current perception"""

        # initialize memory for the ant if it doesn't exist yet
        if perception.ant_id not in self.memory["ant_memory"]:
            self.initialize_ant_memory(perception.ant_id)

        ax, ay = self.memory["ant_memory"][perception.ant_id]["ant_position"]
        dir_x, dir_y = Direction.get_delta(perception.direction)

        if perception.can_see_food():
            for (cx, cy), cell_type in perception.visible_cells.items():
                if cell_type == TerrainType.FOOD:
                    food_position = (ax + cx, ay + cy)
                    if food_position not in self.memory["ant_memory"][perception.ant_id]["food_positions"]:
                        self.memory["ant_memory"][perception.ant_id]["food_positions"].append(food_position)

        # Decide action
        if perception.has_food:
            if self.ant_is_in_colony(perception):
                action = AntAction.DROP_FOOD
                self.memory["ant_memory"][perception.ant_id]["current_action"] = None
            else:
                self.memory["ant_memory"][perception.ant_id]["current_action"] = "Goto"
                self.memory["ant_memory"][perception.ant_id]["goto_destination"] = self.memory["colony_position"]
                action = self.goto(perception)

        elif self.ant_is_on_food(perception) and not perception.has_food: # can remove has_food due to previous condition, but clearer to keep it ?
            # Found food and not carrying any — pick it up and head home
            action = AntAction.PICK_UP_FOOD
            self.memory["ant_memory"][perception.ant_id]["current_action"] = "Goto"
            self.memory["ant_memory"][perception.ant_id]["goto_destination"] = self.memory["colony_position"]

        elif self.memory["ant_memory"][perception.ant_id]["current_action"] == "Goto":
            # Try to spy if a single food-carrying ant is nearby and the cooldown has expired
            if (any(has_food for _, has_food in perception.nearby_ants)
                    and len(perception.nearby_ants) == 1 # can remove ?
                    and self.memory["ant_memory"][perception.ant_id]["spy_pause"] == 0):
                spy_dest = self.spy(perception)
                if spy_dest is not None:
                    self.memory["ant_memory"][perception.ant_id]["goto_destination"] = spy_dest
                    self.memory["ant_memory"][perception.ant_id]["spy_pause"] = 100

            dest = self.memory["ant_memory"][perception.ant_id]["goto_destination"]
            if self.memory["ant_memory"][perception.ant_id]["ant_position"] == dest:
                self.memory["ant_memory"][perception.ant_id]["current_action"] = None
                action = self.scatter(perception)
            else:
                action = self.goto(perception)

        elif self.memory["ant_memory"][perception.ant_id]["food_positions"]:
            closest_food = self.closest_food(perception)
            self.memory["ant_memory"][perception.ant_id]["current_action"] = "Goto"
            self.memory["ant_memory"][perception.ant_id]["goto_destination"] = closest_food
            action = self.goto(perception)

        else:
            action = self.scatter(perception)

        # Update absolute position after move
        if action == AntAction.MOVE_FORWARD:
            # if there is a map limit in front of us, bounce back
            if len(perception.visible_cells) == 1:  # only (0,0) in visible cells
                action = self.bounce_back(perception)

            # if there is an ant in front of us, do not move and do not update the position in memory
            elif any([other_ant[0] == (dir_x, dir_y) for other_ant in perception.nearby_ants]):
                if not perception.has_food:
                    self.scatter(perception)
                action = AntAction.NO_ACTION
                # add step-aside for ants not holding food

            else:
                # update position in memory
                self.memory["ant_memory"][perception.ant_id]["ant_position"] = (ax + dir_x, ay + dir_y)

                # Update food positions in memory using absolute coordinates
                for (cx, cy), cell_type in perception.visible_cells.items():
                    abs_pos = (ax + cx, ay + cy)
                    if cell_type == TerrainType.FOOD:
                        if abs_pos not in self.memory["ant_memory"][perception.ant_id]["food_positions"]:
                            self.memory["ant_memory"][perception.ant_id]["food_positions"].append(abs_pos)
                    elif abs_pos in self.memory["ant_memory"][perception.ant_id]["food_positions"]:
                        self.memory["ant_memory"][perception.ant_id]["food_positions"].remove(abs_pos)

        # remove one step of the spy pause if it is active, to eventually allow spying again after a certain time
        if self.memory["ant_memory"][perception.ant_id]["spy_pause"]:
            self.memory["ant_memory"][perception.ant_id]["spy_pause"] -= 1

        return action


    def ant_is_in_colony(self, perception: AntPerception) -> bool:
        """Check if the ant is in the colony"""
        return perception.visible_cells.get((0, 0)) == TerrainType.COLONY


    def ant_is_on_food(self, perception: AntPerception) -> bool:
        """Check if the ant is on a food cell"""
        return perception.visible_cells.get((0, 0)) == TerrainType.FOOD


    def goto(self, perception):
        """Move toward the absolute destination stored in memory."""
        ax, ay = self.memory["ant_memory"][perception.ant_id]["ant_position"]

        dest_x, dest_y = self.memory["ant_memory"][perception.ant_id]["goto_destination"]

        rel_x = dest_x - ax
        rel_y = dest_y - ay

        if (rel_x, rel_y) == (0, 0):
            return AntAction.NO_ACTION # do something else ? It should not happen

        all_directions = [ # use .get_delta instead of hardcoding the deltas ?
            (Direction.NORTH, (0, -1)),
            (Direction.NORTHEAST, (1, -1)),
            (Direction.EAST, (1, 0)),
            (Direction.SOUTHEAST, (1, 1)),
            (Direction.SOUTH, (0, 1)),
            (Direction.SOUTHWEST, (-1, 1)),
            (Direction.WEST, (-1, 0)),
            (Direction.NORTHWEST, (-1, -1)),
        ]

        def alignment(delta):
            delta_x, delta_y = delta
            length = math.sqrt(delta_x ** 2 + delta_y ** 2)
            return (delta_x * rel_x + delta_y * rel_y) / length

        best_dir, best_delta = max(all_directions, key=lambda d: alignment(d[1]))
        current_delta = Direction.get_delta(perception.direction)

        if current_delta == best_delta:
            return AntAction.MOVE_FORWARD
        else:
            dirs_in_order = [d[0] for d in all_directions]
            current_idx = dirs_in_order.index(perception.direction)
            target_idx = dirs_in_order.index(best_dir)

            cw_dist = (target_idx - current_idx) % 8
            ccw_dist = (current_idx - target_idx) % 8

            if cw_dist <= ccw_dist:
                return AntAction.TURN_RIGHT
            else:
                return AntAction.TURN_LEFT


    def scan(self):
        """Scan the surrounding area for food"""

        # take into account the cells the ant already saw to avoid scanning the same area again
        # many ways to improve that scan by storing different values ?

        # first version : simple 360° scan around the ant

        pass


    def scatter(self, perception):
        """Pick a random absolute destination and go there."""
        ax, ay = self.memory["ant_memory"][perception.ant_id]["ant_position"]
        destination = (ax + random.randint(-250, 250), ay + random.randint(-250, 250))
        self.memory["ant_memory"][perception.ant_id]["current_action"] = "Goto"
        self.memory["ant_memory"][perception.ant_id]["goto_destination"] = destination
        return self.goto(perception)


    def avoid_ant(self, perception):
        """Avoid collision with nearby ants by changing direction momentarilly."""
        pass


    def bounce_back(self, perception):
        """
        Bounce against the environment limit or wall by going in the opposite direction.
        Essentially calcules a goto action with the opposite of the current direction as destination.
        """
        # go to a direction opposite to the env limit we reached
        dir_x, dir_y = Direction.get_delta(perception.direction)
        if dir_x == 1 or dir_x == -1:
            # hit vertical wall
            dir_x = -dir_x
        if dir_y == 1 or dir_y == -1:
            # hit horizontal wall
            dir_y = -dir_y
        self.memory["ant_memory"][perception.ant_id]["current_action"] = "Goto"
        self.memory["ant_memory"][perception.ant_id]["goto_destination"] = (dir_x, dir_y)
        return self.goto(perception)


    def spy(self, perception) -> tuple | None:
        """
        Infer food direction from a single observation of a nearby food-carrying ant.

        Since the observed ant is heading toward the colony at (0, 0), the food source
        lies in the direction from the colony outward through the observed ant's position.
        We project 50 steps in that direction from our own position as a destination.

        Returns the absolute destination tuple, or None if no useful ant is visible.
        """
        ax, ay = self.memory["ant_memory"][perception.ant_id]["ant_position"]

        if not perception.nearby_ants:
            return None

        nearby_ant_rel_pos, nearby_ant_has_food = perception.nearby_ants[0]
        if not nearby_ant_has_food:
            return None

        # Absolute position of the observed ant
        obs_x = ax + nearby_ant_rel_pos[0]
        obs_y = ay + nearby_ant_rel_pos[1]

        # The observed ant is moving toward (0, 0), so food lies in the direction
        # from the colony outward through the observed ant: food_dir = (obs_x, obs_y)
        length = math.sqrt(obs_x ** 2 + obs_y ** 2)
        if length == 0:
            return None  # observed ant is at the colony, no useful information

        # Normalise and project 50 steps from our own position
        dest_x = ax + int((obs_x / length) * 50)
        dest_y = ay + int((obs_y / length) * 50)

        return (dest_x, dest_y)


    def closest_food(self, perception):
        """Return the absolute position of the closest known food."""
        ax, ay = self.memory["ant_memory"][perception.ant_id]["ant_position"]
        return min(
            self.memory["ant_memory"][perception.ant_id]["food_positions"],
            key=lambda food: (food[0] - ax) ** 2 + (food[1] - ay) ** 2
        )

    # Étapes :
    # implémenter l'enregistrement des positions de nourriture + déplacement vers la nourriture la plus proche
    # implémenter implémenter un scatter plus intelligent : lorsqu'il y a un obstacle, refaire un scatter vers un autre endroit
    # implémenter un scan + quand l'utiliser ?


    # ATTENTION :
    # Une fourmi peut porter maximum une nourriture à la fois
    # radius de vision : 3, pas 4 !

    # Il n'est pas possible qu'un nouriture soit mis à un autre endroit que la colonie. Il n'y aura donc jamais de nouriture
    # à un ednroit où il n'y en avait pas jusque là.

    # A-t-on une info du nombre de nouriture totale sur le terrain ? Quand est-ce que le jeu s'arete-t-il ?
    # temps et nombre de pas limités. Si 90% de la nouriture a été trouvée dans ce temps là on considére que la stratégie réussis.