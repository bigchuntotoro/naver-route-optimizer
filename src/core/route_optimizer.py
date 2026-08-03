import itertools
from typing import List, Dict, Tuple, Optional, Any


class RouteOptimizer:
    """최적 이동 경로 계산기"""

    def __init__(self, places: List[str], duration_matrix: Dict[Tuple[str, str], float]):
        self.places = places
        self.duration_matrix = duration_matrix

    def solve(self, start_place: str, end_place: Optional[str] = None) -> Tuple[List[str], float]:
        """
        완전 탐색(Brute-force)으로 최적 경로를 산출합니다.
        """
        waypoints = [p for p in self.places if p != start_place and p != end_place]
        
        best_route = []
        min_duration = float("inf")

        for perm in itertools.permutations(waypoints):
            current_route = [start_place] + list(perm)
            if end_place:
                current_route.append(end_place)

            total_duration = 0.0
            for i in range(len(current_route) - 1):
                o, d = current_route[i], current_route[i + 1]
                total_duration += self.duration_matrix.get((o, d), float("inf"))

            if total_duration < min_duration:
                min_duration = total_duration
                best_route = current_route

        return best_route, round(min_duration, 1)