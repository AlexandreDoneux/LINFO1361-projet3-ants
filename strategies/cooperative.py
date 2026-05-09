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

    # On pourrait utiliser les phéromones pour indiquer qu'il n'y ait plus de nourriture si on fait en sorte de
    # récupérer un max de nouriture dans la zone avant de revenir. Mais en même temps, ces phéromones peuvent permettre
    # de demander de l'aide à d'autres fourmis. SI il y a de la nouriture par tas c'est clairement plus intéressant.

    # Mieux vaut revenir directement à la colonie dès qu'on a eu une info de nouriture vu qu'on peut communiquer cette info à d'autres via les phéromones