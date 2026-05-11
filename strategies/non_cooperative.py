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

        # Current action, can be "Goto", "Scan", "Scatter" ("gohome" -> goto with the position of the colony)
        # self.current_action = "Scatter"
        # self.action_info = None  # additional info for the action
        # scan and scatter info are None, for goto it is the position to go to (relative to the ant position)
        # self.memory = {
        #     "colony_relative_position": (0,0), # storing the position of the colony
        #     "food_positions": [], # storing positions of food seen but not yet collected
        #     "visited_positions": set() # storing positions already seen to avoid redundant scanning => for later use
        # }

        self.memory = {
            "colony_position": (0, 0),  # storing the absolute position of the colony we consider to be 0,0
            # The external code clearly does not use the same coordinates but if we use our coordinates only in our code it should not break everything (I hope)
            "ant_memory": {},
        }


    def initialize_ant_memory(self, ant_id):
        """Initialize memory for a specific ant"""
        self.memory["ant_memory"][ant_id] = {
            "ant_position": (0, 0),  # is at the colony in the beginning
            "food_positions": [],
            "current_action": "Scatter",
            "action_info": None
        }



    def decide_action(self, perception: AntPerception) -> AntAction:
        """Decide an action based on current perception"""



        # initialize memory for the ant if it doesn't exist yet
        if perception.ant_id not in self.memory["ant_memory"]:
            self.initialize_ant_memory(perception.ant_id)


        for (dx, dy), cell_type in perception.visible_cells.items():
            # storing the relative position of food if seen
            if cell_type == TerrainType.FOOD:
                relative_position = (dx, dy)
                if relative_position not in self.memory["ant_memory"][perception.ant_id]["food_positions"]:
                    self.memory["ant_memory"][perception.ant_id]["food_positions"].append(relative_position)
            # removing the relative position of food if it is no longer seen (because the ant moved or because it was picked up by another ant)
            if (dx, dy) in self.memory["ant_memory"][perception.ant_id][
                "food_positions"] and cell_type != TerrainType.FOOD:
                self.memory["ant_memory"][perception.ant_id]["food_positions"].remove((dx, dy))


        if self.ant_is_on_food(perception):
            action = AntAction.PICK_UP_FOOD
            # Remove this position from memory since we're picking it up
            if (0, 0) in self.memory["ant_memory"][perception.ant_id]["food_positions"]:
                self.memory["ant_memory"][perception.ant_id]["food_positions"].remove((0, 0))
            # If more food in memory, go to next one; otherwise go home if carrying food
            if len(self.memory["ant_memory"][perception.ant_id]["food_positions"]) != 0:
                if perception.ant_id == 1:
                    print("1")
                    print("food in memory, going to closest food at", self.memory["ant_memory"][perception.ant_id]["food_positions"])
                #closest_food = self.closest_food(perception)
                self.memory["ant_memory"][perception.ant_id]["current_action"] = "Goto"
                #self.memory["ant_memory"][perception.ant_id]["action_info"] = closest_food
                self.memory["ant_memory"][perception.ant_id]["action_info"] = self.memory["ant_memory"][perception.ant_id]["food_positions"][0]  # go to the first food in memory optimise later to go to the closest
            elif perception.has_food:  # has_food will be true next turn, anticipate it
                print(f"Ant {perception.ant_id} has food, going to colony at {self.memory['colony_position']}")
                self.memory["ant_memory"][perception.ant_id]["current_action"] = "Goto"
                self.memory["ant_memory"][perception.ant_id]["action_info"] = self.memory["colony_position"]
            else:
                self.memory["ant_memory"][perception.ant_id]["current_action"] = None
                self.memory["ant_memory"][perception.ant_id]["action_info"] = None

        elif perception.has_food and self.ant_is_in_colony(perception):
            action = AntAction.DROP_FOOD
            self.memory["ant_memory"][perception.ant_id]["current_action"] = None
            self.memory["ant_memory"][perception.ant_id]["action_info"] = None

        elif self.memory["ant_memory"][perception.ant_id]["current_action"] == "Goto":
            dest = self.memory["ant_memory"][perception.ant_id]["action_info"]
            action = self.goto(perception, dest)

        elif len(self.memory["ant_memory"][perception.ant_id]["food_positions"]) != 0:
            # New food spotted while not in a goto — head to closest
            closest_food = self.closest_food(perception)
            action = self.goto(perception, closest_food)
            self.memory["ant_memory"][perception.ant_id]["current_action"] = "Goto"

        else:
            action = self.scatter(perception)


        # updating the ant's position
        if action == AntAction.MOVE_FORWARD:
            dx, dy = Direction.get_delta(perception.direction)
            self.memory["ant_memory"][perception.ant_id]["ant_position"] = (self.memory["ant_memory"][perception.ant_id]["ant_position"][0] + dx,
                                                                            self.memory["ant_memory"][perception.ant_id]["ant_position"][1] + dy)


        if perception.ant_id == 1:  # print the action and the colony relative position for one of the ants to check values
            #print(f"Ant {perception.ant_id} action: {action}, colony_relative_position: {self.memory['colony_relative_position']}")
            pass


        #test_action, new_dest = self.goto(perception, (40, 120)) # relative position !
        #print(new_dest)
        # -> problem with values, in this test, the destination always being the same, the ant will always go to one of the cardinalities
        # needs update of the destination through memory
        # there still is a problem with orientation. With a fixed value the ant should turn continuously.


        return action




    def ant_is_in_colony(self, perception: AntPerception) -> bool:
        """Check if the ant is in the colony"""

        return perception.visible_cells.get((0, 0)) == TerrainType.COLONY


    def ant_is_on_food(self, perception: AntPerception) -> bool:
        """Check if the ant is on a food cell"""

        return perception.visible_cells.get((0, 0)) == TerrainType.FOOD

    import math

    def goto(self, perception, destination):

        gx, gy = destination

        all_directions = [ # use .get_delta instead of hardcoding the deltas
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
            ddx, ddy = delta
            length = math.sqrt(ddx ** 2 + ddy ** 2)  # 1.0 for cardinals, √2 for diagonals
            return (ddx * gx + ddy * gy) / length  # normalize so all dirs are comparable

        best_dir, best_delta = max(all_directions, key=lambda d: alignment(d[1]))
        bdx, bdy = best_delta

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
        """Randomly explore the environment when no information is available"""

        # possibility to search randomly or using a more efficient method like a spiral, zigzag, other pattern ?

        # go to random relative position
        destination = (random.randint(-100, 100), random.randint(-100, 100))
        #print(f"Scattering to random destination: {destination}")
        action = self.goto(perception, destination)
        #print(f"Scatter action: {action}, New destination: {new_dest}")
        self.memory["ant_memory"][perception.ant_id]["current_action"] = "Goto"

        return action


    def closest_food(self, perception):
        """Move towards the closest food source seen"""

        # On peut se souvenir de la nourriture qu'on aurait vu. Imaginons qu'on voit deux nouritures et qu'en se
        # déplaçant vers l'une on perds de vue l'autre. On peut s'en souvenir pour la rejoindre par après.
        return(min(self.memory["ant_memory"][perception.ant_id]["food_relative_positions"],
            key=lambda food: food[0] ** 2 + food[1] ** 2))  # find the closest food using the distance to the ant (0,0)

        # => attention : obstacles ! => dans une verion améliorée



    # WARNING : un pas est défini par une action (decide_action).
    # On ne peut pas faire plusieurs actions par tour. decide_action() doit renvoyer une action unique
    # (avancer, rotation, pickup, drop, déposer un type de pheromones, ne rien faire)

    # radius de vision : 3, pas 4 !

    # Étapes :
    # à redéterminer



    # Non-cooperative strategy:
    # aucun partage d'information mais on a une mémoire


    # ATTENTION :
    # Une fourmi peut porter autant de nouriture qu'elle veut. Il ne semble pas y avoir de limite. Mieux vaut chercher
    # dans une zone le maximum de nouriture avant de l'apporter à la colonie.

    # Il n'est pas possible qu'un nouriture soit mis à un autre endroit que la colonie. Il n'y aura donc jamais de nouriture à un ednroit où il n'y en avait pas jusque là.

    # A-t-on une info du nombre de nouriture totale sur le terrain ? Quand est-ce que le jeu s'arete-t-il ?
    # temps et nombre de pas limités. Si 90% de la nouriture a été trouvée dans ce temps là on considére que la stratégie réussis.






