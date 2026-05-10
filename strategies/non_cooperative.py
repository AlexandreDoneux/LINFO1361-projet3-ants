from environment import TerrainType, AntPerception, Direction
from ant import AntAction, AntStrategy

import random


class NonCooperativeStrategy(AntStrategy):
    """
    # TODO: Insert your code here
    """
    # store for each ant :
    # - position de la colonie
    # - position de la nouriture vue mais pas encore récupérée
    # - position des endroits déjà vus ? => beaucoup de données à stocker
    # - l'action particulière qu'il fait
    #      - se déplace à un entroit particulier (goto) + position
    #      - faire un scan de la zone (radar) + position/info de ce scan => voir techniques dans le cours
    #      - faire une stratégie de recherche (scatter) + position/info de ce scatter => voir techniques dans le cours
    #
    # - position des nourritures récupérées et déjà récupérées ? => pour approfondir la recherche dans cette zone

    def __init__(self):
        """Initialize the strategy with last action tracking"""

        # Current action, can be "Goto", "Scan", "Scatter" ("gohome" -> goto with the position of the colony)
        self.current_action = "Scatter"
        self.action_info = None  # additional info for the action
        # scan and scatter info are None, for goto it is the position to go to (relative to the ant position)
        self.memory = {
            "colony_relative_position": (0,0), # storing the relative position of the colony
            "food_relative_positions": [], # storing relative positions of food seen but not yet collected
            "visited_positions": set() # storing positions already seen to avoid redundant scanning => for later use
        }

    def decide_action(self, perception: AntPerception) -> AntAction:
        """Decide an action based on current perception"""


        # storing food relative positions if seen
        if perception.can_see_food(): # redundant check because .can_see_food() already checks the visible cells for FOOD (remove later)
            for (dx, dy), cell_type in perception.visible_cells.items():
                if cell_type == TerrainType.FOOD:
                    relative_position = (dx, dy)
                    if relative_position not in self.memory["food_relative_positions"]:
                        self.memory["food_relative_positions"].append(relative_position)

        # remove relative food positions if they disappeared (some other ant might have collected the food)

        # for food in self.memory["food_relative_positions"]:
        #     if food in perception.visible_cells.keys() and perception.visible_cells[food] != TerrainType.FOOD:
        #         self.memory["food_relative_positions"].remove(food)
        # # change for loop so it checks all the visible cells instead of checking the stored food positions

        for (dx, dy), cell_type in perception.visible_cells.items():
            if (dx, dy) in self.memory["food_relative_positions"] and cell_type != TerrainType.FOOD :
                self.memory["food_relative_positions"].remove((dx, dy))
        # -> can be added to the previous loop when we have removed "perception.can_see_food()"

        # what action to do
        if self.ant_is_on_food(): # if the ant is on a cell with food, pick up the food
            action = AntAction.PICK_UP_FOOD
            self.current_action = None
            self.action_info = None
        elif perception.has_food and self.ant_is_in_colony(perception): # if the ant has food and is in the colony, drop the food
            action = AntAction.DROP_FOOD
            self.current_action = None
            self.action_info = None
        # if the ant still has some food positions in memory, try to go to the closest one
        elif self.memory["food_relative_positions"]:
            closest_food = self.closest_food()
            self.current_action = "Goto"
            self.action_info = closest_food
        elif perception.has_food:
            # if ant has food, go to the colony
            pass
        else:
            # if no food in memory and no food carried, scatter to explore the environment
            self.action = "Scatter"
            self.action_info = None


        # action that will be done at the next step, we check before that they are valid (to be implemented)
        action = None

        # updating the colony relative position and relative food positions du to movement of the ant
        if action == AntAction.MOVE_FORWARD :
            dx, dy = Direction.get_delta(perception.direction)
            self.memory["colony_relative_position"] = (self.memory["colony_relative_position"][0] - dx, self.memory["colony_relative_position"][1] - dy)
            self.memory["food_relative_positions"] = [(food[0] - dx, food[1] - dy) for food in self.memory["food_relative_positions"]]
        if action == AntAction.TURN_LEFT :
            self.memory["colony_relative_position"] = (self.memory["colony_relative_position"][1], -self.memory["colony_relative_position"][0])
            self.memory["food_relative_positions"] = [(food[1], -food[0]) for food in self.memory["food_relative_positions"]]
        if action == AntAction.TURN_RIGHT :
            self.memory["colony_relative_position"] = (-self.memory["colony_relative_position"][1], self.memory["colony_relative_position"][0])
            self.memory["food_relative_positions"] = [(-food[1], food[0]) for food in self.memory["food_relative_positions"]]
        # check values



        
        return self._decide_movement(perception)

    def _decide_movement(self, perception: AntPerception) -> AntAction:
        """Decide which direction to move based on current state"""
        # TODO: Insert your code here

        # won't be used in the agent we implement

        random_direction = random.choice([AntAction.MOVE_FORWARD, AntAction.TURN_LEFT, AntAction.TURN_RIGHT])
        return random_direction  # Random movement for now, replace with actual logic


    def ant_is_in_colony(self, perception: AntPerception) -> bool:
        """Check if the ant is in the colony"""

        return perception.visible_cells.get((0, 0)) == TerrainType.COLONY


    def ant_is_on_food(self, perception: AntPerception) -> bool:
        """Check if the ant is on a food cell"""

        return perception.visible_cells.get((0, 0)) == TerrainType.FOOD



    def goto(self, position, destination):
        """Move towards a specific position"""

        # => voir algorithmes de pathfinding
        # -> warning : obstacles !

        # AntPerception._get_direction_from_delta()

        pass


    def scan(self):
        """Scan the surrounding area for food"""

        # take into account the cells the ant already saw to avoid scanning the same area again
        # many ways to improve that scan by storing different values ?

        # first version : simple 360° scan around the ant

        pass

    def scatter(self):
        """Randomly explore the environment when no information is available"""

        # possibility to search randomly or using a more efficient method like a spiral, zigzag, other pattern ?

        pass


    def closest_food(self):
        """Move towards the closest food source seen"""

        # On peut se souvenir de la nourriture qu'on aurait vu. Imaginons qu'on voit deux nouritures et qu'en se
        # déplaçant vers l'une on perds de vue l'autre. On peut s'en souvenir pour la rejoindre par après.
        return(min(self.memory["food_relative_positions"],
            key=lambda food: food[0] ** 2 + food[1] ** 2))  # find the closest food using the distance to the ant (0,0)

        # => attention : obstacles ! => dans une verion améliorée

        pass



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






