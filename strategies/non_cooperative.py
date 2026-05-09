from environment import TerrainType, AntPerception
from ant import AntAction, AntStrategy

import random


class NonCooperativeStrategy(AntStrategy):
    """
    # TODO: Insert your code here
    """

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

        random_direction = random.choice([AntAction.MOVE_FORWARD, AntAction.TURN_LEFT, AntAction.TURN_RIGHT])
        return random_direction  # Random movement for now, replace with actual logic


    # Non-cooperative strategy:
    # aucun partage d'information mais on a une mémoire

    # mémoire :
    # - position de la colonie
    # - position de la nouriture vue mais pas encore récupérée. Le temps de s'y déplacer et la récupérer.
    #       => lors de la récupération peut potentiellement se souvenir de la position d'ancienne nouriturre avec encore des endroits possibles
    #      => quand enlever ces positions-là de la mémoire ?
    # - stocker les endroits où on a trouvé de la nourriture et où il y a des espaces encore pour chercher. Si une position
    #  de nouriture n'a pas d'espace innexploré à proximité on peut l'oublier.
    # - Les cellules déjà "vues" pour favoriser la recherche à d'autres endoroits (mais rien n'empêche une nouriture d'avoir été redéplacé vers un endorit déjà vu.)

    # ATTENTION :
    # Une fourmi peut porter autant de nouriture qu'elle veut. Il ne semble pas y avoir de limite. Mieux vaut chercher
    # dans une zone le maximum de nouriture avant de l'apporter à la colonie.

    # Il n'est pas possible qu'un nouriture soit mis à un autre endroit que la colonie. Il n'y aura donc jamais de nouriture à un ednroit où il n'y en avait pas jusque là.


    # A-t-on une info du nombre de nouriture totale sur le terrain ? Quand est-ce que le jeu s'arete-t-il ?
    # temps et nombre de pas limités. Si 90% de la nouriture a été trouvée dans ce temps là on considére que la stratégie réussis.


    # SI on peut changer le comportement de l'agent

    # goto()
    # -> ordonner à une fourmi d'aller à un endroit précis
    # => voir algorithmes de pathfinding
    # -> warning : obstacles !

    # scatter()
    # -> stratégie de recherche lorsqu'on a aucune info
    # => pour chercher de la nouriture ou des phéromones dans les agents 2 et 3


    # closest_food()
    # -> si on se souvient de nouriture on doit trouver la nouriture la plus proche.
    # -> attention : obstacles ! => dans une verion améliorée


    # radar()
    # -> recherche de la nouriture ou des phéromones autour de soi
    # -> avec simple tour 360° autour de la fourmi ?
    # -> avec recherche un peu plus éfficace ? intensification (rechercher dans la même zone) ou diversification (scatter) selon certaines probabilités ?