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
            # Can be "Goto", "Scan", "Scatter" (going to the colony -> goto with the position of the colony)
            "action_info": None, # additional info, mainly used for "Goto" to store the destination position
            "previous_position": None, # to detect if we are stuck against a wall on the limit of the map
            "previous_action": None, # same
        }

        # add obstacles later when implementing a more complex strategy


    def decide_action(self, perception: AntPerception) -> AntAction:
        """Decide an action based on current perception"""

        # initialize memory for the ant if it doesn't exist yet
        if perception.ant_id not in self.memory["ant_memory"]:
            self.initialize_ant_memory(perception.ant_id)

        ax, ay = self.memory["ant_memory"][perception.ant_id]["ant_position"]

        # Decide action
        if perception.has_food:
            if self.ant_is_in_colony(perception):
                action = AntAction.DROP_FOOD
                self.memory["ant_memory"][perception.ant_id]["current_action"] = None
                self.memory["ant_memory"][perception.ant_id]["action_info"] = None
            else:
                self.memory["ant_memory"][perception.ant_id]["current_action"] = "Goto"
                self.memory["ant_memory"][perception.ant_id]["action_info"] = self.memory["colony_position"]
                action = self.goto(perception)

        elif self.ant_is_on_food(perception) and not perception.has_food:
            # Found food and not carrying any — pick it up and head home
            action = AntAction.PICK_UP_FOOD
            self.memory["ant_memory"][perception.ant_id]["current_action"] = "Goto"
            self.memory["ant_memory"][perception.ant_id]["action_info"] = self.memory["colony_position"]

        # elif perception.has_food and self.ant_is_in_colony(perception):
        #     # Back at colony with food — drop it and scatter again
        #     action = AntAction.DROP_FOOD
        #     self.memory["ant_memory"][perception.ant_id]["current_action"] = None
        #     self.memory["ant_memory"][perception.ant_id]["action_info"] = None

        elif self.memory["ant_memory"][perception.ant_id]["current_action"] == "Goto":
            dest = self.memory["ant_memory"][perception.ant_id]["action_info"]
            if self.memory["ant_memory"][perception.ant_id]["ant_position"] == dest:
                self.memory["ant_memory"][perception.ant_id]["current_action"] = None
                self.memory["ant_memory"][perception.ant_id]["action_info"] = None
                action = self.scatter(perception)
            else:
                action = self.goto(perception)

        else:
            action = self.scatter(perception)

        # Update absolute position after move
        if action == AntAction.MOVE_FORWARD:
            dir_x, dir_y = Direction.get_delta(perception.direction)
            self.memory["ant_memory"][perception.ant_id]["ant_position"] = (ax + dir_x, ay + dir_y)

            # Update food positions in memory using absolute coordinates
            for (cx, cy), cell_type in perception.visible_cells.items():
                abs_pos = (ax + cx, ay + cy)
                if cell_type == TerrainType.FOOD:
                    if abs_pos not in self.memory["ant_memory"][perception.ant_id]["food_positions"]:
                        self.memory["ant_memory"][perception.ant_id]["food_positions"].append(abs_pos)
                elif abs_pos in self.memory["ant_memory"][perception.ant_id]["food_positions"]:
                    self.memory["ant_memory"][perception.ant_id]["food_positions"].remove(abs_pos)

        if action == AntAction.MOVE_FORWARD:
            #print("saving previous position and action")
            print((ax, ay))
            print(perception.visible_cells.get((0, 0)))
            # position keeps changing despite being blocked by the limits. Thats because we update if the move was a forward but we don't check wether it worked.
            # can we check if it worked ? -> no
            self.memory["ant_memory"][perception.ant_id]["previous_position"] = (ax, ay)
            self.memory["ant_memory"][perception.ant_id]["previous_action"] = action


        return action




    def ant_is_in_colony(self, perception: AntPerception) -> bool:
        """Check if the ant is in the colony"""

        return perception.visible_cells.get((0, 0)) == TerrainType.COLONY


    def ant_is_on_food(self, perception: AntPerception) -> bool:
        """Check if the ant is on a food cell"""

        return perception.visible_cells.get((0, 0)) == TerrainType.FOOD

    def goto(self, perception):
        """Move toward the absolute destination stored in action_info."""
        ax, ay = self.memory["ant_memory"][perception.ant_id]["ant_position"]

        if self.memory["ant_memory"][perception.ant_id]["previous_action"] == AntAction.MOVE_FORWARD :
            pass
            print("previous action was move forward")
            print(self.memory["ant_memory"][perception.ant_id]["previous_position"] == (ax, ay)) # always false ... why ?

        if (self.memory["ant_memory"][perception.ant_id]["previous_action"] == AntAction.MOVE_FORWARD
                and self.memory["ant_memory"][perception.ant_id]["previous_position"] == (ax, ay)):
            # We tried to move forward but we are still in the same position, it means we are blocked by a wall or an obstacle, we should scatter to get out of it.
            print("scatter due to being stuck")
            return self.scatter(perception)

        dest_x, dest_y = self.memory["ant_memory"][perception.ant_id]["action_info"]

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

            # if there is a wall in front of us (not obstacle), scatter
            # can't differentiate between obstacle and wall that delimits the map
            #print(current_delta)
            #print(perception.visible_cells)
            # TerrainType.WALL is obstacle, what is limit of the map ?
            # if not possible to detect the terrain limit type we might be able to detect when hitting a wall and using an action message.
            if perception.visible_cells.get(current_delta) == TerrainType.WALL:
                print("scatter du to reaching a wall")
                return self.scatter(perception)
            # not really working
            # improve scatter if they are facing a wall and depending on the previous goto destination

            # don't think it is possible to detect if we have reached the limits of the map.
            # We can't even implement a goto() that goes around it because we don't detect it.
            # Solution : X "going forward" but we haven't moved + not in front of a wall => reached limit
            # can't be used for coop strategy because we don't have memory.

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
        destination = (ax + random.randint(-100, 100), ay + random.randint(-100, 100))
        self.memory["ant_memory"][perception.ant_id]["current_action"] = "Goto"
        self.memory["ant_memory"][perception.ant_id]["action_info"] = destination
        return self.goto(perception)

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






