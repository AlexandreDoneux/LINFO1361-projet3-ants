from environment import TerrainType, AntPerception
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
        # TODO: Insert your code here

    def decide_action(self, perception: AntPerception) -> AntAction:
        """Decide an action based on current perception"""

        # TODO: Insert your code here
        
        return self._decide_movement(perception)

    def _decide_movement(self, perception: AntPerception) -> AntAction:
        """Decide which direction to move based on current state"""
        # TODO: Insert your code here

        # won't be used in the agent we implement

        random_direction = random.choice([AntAction.MOVE_FORWARD, AntAction.TURN_LEFT, AntAction.TURN_RIGHT])
        return random_direction  # Random movement for now, replace with actual logic


    def goto(self, position, destination):
        """Move towards a specific position"""

        # => voir algorithmes de pathfinding
        # -> warning : obstacles !

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






