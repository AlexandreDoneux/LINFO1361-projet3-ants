from environment import TerrainType, AntPerception
from ant import AntAction, AntStrategy

import random

class CooperativeStrategy(AntStrategy):
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



    # Cooperative strategy :

     # Si on utilise des phéromones ils doivent decay à chaque pas fait. Sinon on ne peut pas prévoir la direction de la
    # piste. DOnc ce serait une itération/pas par action.


    # Répartir des rôles au sein de la colonie ? -> non, toutes les fourmis peuvent trouver/ramener de la nourriture
    # Quelques fourmis qui s'occupent de garder un chemin de phéromones intact ? -> idem, n'importe quelle fourmi qui récupères de la nourriture peut faire les deux chemins de phéromones

