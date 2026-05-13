from environment import TerrainType, AntPerception, Direction
from ant import AntAction, AntStrategy
import random
import math

class SmartStrategy(AntStrategy):
    def __init__(self):
        self.ants = {}
        self.pheromone_timers = {}

    def decide_action(self, perception: AntPerception) -> AntAction:
        ant_id = perception.ant_id
        if ant_id not in self.ants:
            # Mémoire : position, cases de nourriture connues, et cible d'exploration
            self.ants[ant_id] = {"pos": (0, 0), "food": set(), "target": None}
            self.pheromone_timers[ant_id] = 0

        mem = self.ants[ant_id]
        ax, ay = mem["pos"]

        on_colony = perception.visible_cells.get((0, 0)) == TerrainType.COLONY
        on_food   = perception.visible_cells.get((0, 0)) == TerrainType.FOOD

        # --- 1. ACTIONS IMMÉDIATES ---
        if on_food and not perception.has_food: return AntAction.PICK_UP_FOOD
        if on_colony and perception.has_food: return AntAction.DROP_FOOD

        # --- 2. MISE À JOUR DE LA MÉMOIRE ---
        for (cx, cy), terrain in perception.visible_cells.items():
            abs_pos = (ax + cx, ay + cy)
            if terrain == TerrainType.FOOD:
                mem["food"].add(abs_pos)
            elif abs_pos in mem["food"]:
                mem["food"].remove(abs_pos) # Oublie la source si elle est vidée !

        # --- 3. DÉPÔT DE PHÉROMONES ---
        if perception.has_food and not on_food:
            self.pheromone_timers[ant_id] += 1
            if self.pheromone_timers[ant_id] >= 3:
                self.pheromone_timers[ant_id] = 0
                return AntAction.DEPOSIT_FOOD_PHEROMONE

        # --- 4. CHOIX DE LA DIRECTION ---
        action = self._move(perception, mem, ax, ay)

        if action == AntAction.MOVE_FORWARD:
            try:
                dx, dy = Direction.get_delta(perception.direction)
            except Exception:
                mem["target"] = None
                return random.choice([AntAction.TURN_LEFT, AntAction.TURN_RIGHT])

            cell_ahead = perception.visible_cells.get((dx, dy))

            # 1) pas de cellule visible -> obstacle/bord
            if cell_ahead is None:
                mem["target"] = None
                return random.choice([AntAction.TURN_LEFT, AntAction.TURN_RIGHT])

            # 2) test robuste pour obstacle : on n'accède pas à TerrainType.OBSTACLE
            #    on inspecte plutôt le nom ou la représentation de la valeur retournée
            name = getattr(cell_ahead, "name", None) or str(cell_ahead)
            name_up = name.upper()
            if "OBSTACLE" in name_up or "WALL" in name_up or "BLOCK" in name_up or "ROCK" in name_up:
                mem["target"] = None
                return random.choice([AntAction.TURN_LEFT, AntAction.TURN_RIGHT])

            # 3) sinon on avance et on met à jour la position estimée
            mem["pos"] = (ax + dx, ay + dy)


        return action

    def _move(self, perception, mem, ax, ay):
        # CAS A : On rentre à la base
        if perception.has_food:
            return self._go_to_absolute(perception, ax, ay, (0, 0))
            
        # CAS B : On cherche à manger
        else:
            # Priorité 1 : La vue directe
            for (dx, dy), terrain in perception.visible_cells.items():
                if terrain == TerrainType.FOOD:
                    return self._go_to_relative(perception.direction, (dx, dy))

            # Priorité 2 : Le GPS (Mémoire)
            if mem["food"]:
                closest = min(mem["food"], key=lambda f: (f[0]-ax)**2 + (f[1]-ay)**2)
                return self._go_to_absolute(perception, ax, ay, closest)

            # Priorité 3 : Suivre les Phéromones (Seulement si mémoire vide !)
            target_pher = self._best_pheromone(perception)
            if target_pher:
                mem["target"] = None # Coupe l'exploration au hasard pour suivre la piste
                return self._go_to_relative(perception.direction, target_pher)

            # Priorité 4 : Scatter (Exploration GPS aléatoire)
            if not mem["target"] or mem["target"] == (ax, ay):
                mem["target"] = (ax + random.randint(-20, 20), ay + random.randint(-20, 20))
                
            return self._go_to_absolute(perception, ax, ay, mem["target"])

    # ==========================================
    # OUTILS MATHÉMATIQUES ET DE DÉPLACEMENT
    # ==========================================

    def _go_to_absolute(self, perception, ax, ay, target_abs):
        if not target_abs: return AntAction.MOVE_FORWARD
        rel_pos = (target_abs[0] - ax, target_abs[1] - ay)
        if rel_pos == (0, 0): return random.choice([AntAction.TURN_LEFT, AntAction.TURN_RIGHT])
        return self._go_to_relative(perception.direction, rel_pos)

    def _go_to_relative(self, current_dir, rel_pos):
        cx, cy = rel_pos
        all_dirs = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
        
        def alignment(delta):
            l = math.sqrt(delta[0]**2 + delta[1]**2)
            return (delta[0]*cx + delta[1]*cy)/l if l > 0 else 0
            
        target_idx, _ = max(enumerate(all_dirs), key=lambda d: alignment(d[1]))
        c_idx = current_dir.value if hasattr(current_dir, 'value') else int(current_dir)

        if c_idx == target_idx: return AntAction.MOVE_FORWARD
        if (target_idx - c_idx) % 8 <= (c_idx - target_idx) % 8: return AntAction.TURN_RIGHT
        return AntAction.TURN_LEFT

    def _best_pheromone(self, perception):
        data = getattr(perception, 'food_pheromone', {})
        if callable(data): data = data()
        if not isinstance(data, dict): return None
        
        best, best_lvl = None, 0
        c_idx = perception.direction.value if hasattr(perception.direction, 'value') else int(perception.direction)
        all_dirs = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]

        for (dx, dy), lvl in data.items():
            if lvl > 0 and (dx, dy) != (0, 0):
                def alignment(delta):
                    l = math.sqrt(delta[0]**2 + delta[1]**2)
                    return (delta[0]*dx + delta[1]*dy)/l if l > 0 else 0
                
                target_idx, _ = max(enumerate(all_dirs), key=lambda item: alignment(item[1]))
                
                # Pénalité anti-retour
                diff = (target_idx - c_idx) % 8
                if diff == 4: lvl *= 0.05
                elif diff in [3, 5]: lvl *= 0.2
                
                if lvl > best_lvl:
                    best_lvl, best = lvl, (dx, dy)
        return best
