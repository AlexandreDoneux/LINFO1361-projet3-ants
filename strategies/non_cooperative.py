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


    # doit-on utiliser _decide_movement() ? non, c'est une méthode privée et est utilisée que dans decide_action()

    # WARNING : un pas est défini par une action (decide_action).
    # Est-ce qu'on peut faire un goto() ou radar() au niveau de notre stratégie sans trigger decide_action à chaque pas ?
    # Est-ce qu'à chaque action (déplacement, rotation, récupération, dépot, ect.) decide_action() sera appelé ?
    # Ou bien est-ce qu'un appel à decide_action() correspond à une décision, une itération ?

    # radius de vision : 3, pas 4 !

    # Étapes
    # - stocker la position de la colonie
    # - implémenter radar() et récupération de la nouriture trouvée
    # - implémenter closest_food() pour trouver la nouriture la plus proche (pour optimiser le déplacement vers celle-ci)
    # - implémenter goto() pour se déplacer vers un endroit précis (colonie ou nouriture)
    # - améliorer radar() pour si il trouve de la nouriture commencer à regarder autour (déplacement autour de la zone ananlysée/où la nourriture est trouvée)
    # - implémenter scatter() pour faire une recherche aléatoire à partir d'un endroit (colonie ou zone de nouriture trouvée).
    # - implémenter decide_action() pour définir le comportement de la fourmi
    # - stocker la nourriture trouvée avec des zones de libres à proximité (disons une zone de 2 fois son radius de vision)
    # - Prendre en compte les obstacles dans goto(), scatter(), closest_food()
    #
    # => voir après



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




