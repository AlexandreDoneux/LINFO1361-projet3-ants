from environment import TerrainType, AntPerception, Direction
from ant import AntAction, AntStrategy
import random
import math

class CooperativeStrategy(AntStrategy):
    def __init__(self):
        self.pheromone_timers = {}

    def decide_action(self, perception: AntPerception) -> AntAction:
        ant_id = perception.ant_id
        if ant_id not in self.pheromone_timers:
            self.pheromone_timers[ant_id] = 0

        on_colony = perception.visible_cells.get((0, 0)) == TerrainType.COLONY
        on_food   = perception.visible_cells.get((0, 0)) == TerrainType.FOOD

        # 1. Ramasser la nourriture
        if on_food and not perception.has_food:
            return AntAction.PICK_UP_FOOD

        # 2. Déposer la nourriture
        if on_colony and perception.has_food:
            return AntAction.DROP_FOOD

        # 3. Déposer des phéromones
        self.pheromone_timers[ant_id] += 1
        
        if perception.has_food and not on_food:
            if self.pheromone_timers[ant_id] >= 3:
                self.pheromone_timers[ant_id] = 0
                return AntAction.DEPOSIT_FOOD_PHEROMONE
            
        elif not perception.has_food:
            if self.pheromone_timers[ant_id] >= 2:
                self.pheromone_timers[ant_id] = 0
                return AntAction.DEPOSIT_HOME_PHEROMONE

        # 4. Décider du déplacement
        action = self._move(perception)
        
        # --- 5. BOUCLIER ANTI-MUR ULTRA COMPACT (3 LIGNES) ---
        c = perception.direction.value if hasattr(perception.direction, 'value') else int(perception.direction)
        dx, dy = [(0,-1), (1,-1), (1,0), (1,1), (0,1), (-1,1), (-1,0), (-1,-1)][c % 8]
        if action == AntAction.MOVE_FORWARD and perception.visible_cells.get((dx, dy)) is None:
            return AntAction.TURN_LEFT
            
        return action

    def _move(self, perception: AntPerception) -> AntAction:
        if perception.has_food:
            target = self._find_terrain(perception, TerrainType.COLONY)
            if target:
                return self._go_to(perception.direction, target)
                
            # Mouvement random "tous les 5 pas en moyenne" (20% de chance)
            if random.random() < 0.20:
                return random.choice([AntAction.TURN_LEFT, AntAction.TURN_RIGHT])
                
            target = self._best_pheromone(perception, 'home_pheromone')
            if target:
                return self._go_to(perception.direction, target)
        else:
            target = self._find_terrain(perception, TerrainType.FOOD)
            if target:
                return self._go_to(perception.direction, target)
                
            # Mouvement random "tous les 5 pas en moyenne" (20% de chance)
            if random.random() < 0.20:
                return random.choice([AntAction.TURN_LEFT, AntAction.TURN_RIGHT])
                
            target = self._best_pheromone(perception, 'food_pheromone')
            if target:
                return self._go_to(perception.direction, target)

        return random.choices(
            [AntAction.MOVE_FORWARD, AntAction.TURN_LEFT, AntAction.TURN_RIGHT],
            weights=[70, 15, 15]
        )[0]

    def _find_terrain(self, perception, terrain_type):
        best, best_dist = None, float('inf')
        for (dx, dy), terrain in perception.visible_cells.items():
            if terrain == terrain_type:
                dist = math.sqrt(dx**2 + dy**2)
                if dist < best_dist:
                    best_dist, best = dist, (dx, dy)
        return best

    def _best_pheromone(self, perception, attr):
        data = getattr(perception, attr, {})
        if callable(data): data = data()
        if not isinstance(data, dict): return None
        best, best_level = None, 0
        for (dx, dy), level in data.items():
            if level > best_level and (dx, dy) != (0, 0):
                best_level, best = level, (dx, dy)
        return best

    def _go_to(self, current_dir, rel_pos) -> AntAction:
        cx, cy = rel_pos
        all_directions = [
            (Direction.NORTH,     ( 0, -1)),
            (Direction.NORTHEAST, ( 1, -1)),
            (Direction.EAST,      ( 1,  0)),
            (Direction.SOUTHEAST, ( 1,  1)),
            (Direction.SOUTH,     ( 0,  1)),
            (Direction.SOUTHWEST, (-1,  1)),
            (Direction.WEST,      (-1,  0)),
            (Direction.NORTHWEST, (-1, -1)),
        ]
        def alignment(delta):
            dx, dy = delta
            length = math.sqrt(dx**2 + dy**2)
            if length == 0: return 0
            return (dx * cx + dy * cy) / length

        target_dir, _ = max(all_directions, key=lambda d: alignment(d[1]))

        def to_int(d):
            if hasattr(d, 'value'): return d.value
            if isinstance(d, int): return d
            return 0

        c = to_int(current_dir)
        t = to_int(target_dir)

        if c == t:
            return AntAction.MOVE_FORWARD

        if (t - c) % 8 <= (c - t) % 8:
            return AntAction.TURN_RIGHT
        else:
            return AntAction.TURN_LEFT
