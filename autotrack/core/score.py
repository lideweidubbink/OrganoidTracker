from typing import List, Set, Optional, Iterable, Dict

from autotrack.core import TimePoint
from autotrack.core.particles import Particle


class Score:
    """Represents some abstract score, calculated from the individual elements. Usage:

        score = Score()
        score.foo = 4
        score.bar = 3.1
        # Results in score.total() == 7.1
    """

    def __init__(self, **kwargs):
        self.__dict__["scores"] = kwargs.copy()

    def __setattr__(self, key, value):
        self.__dict__["scores"][key] = value

    def __getattr__(self, item):
        return self.__dict__["scores"][item]

    def __delattr__(self, item):
        del self.__dict__["scores"][item]

    def total(self):
        score = 0
        for name, value in self.__dict__["scores"].items():
            score += value
        return score

    def keys(self) -> List[str]:
        keylist = list(self.__dict__["scores"].keys())
        keylist.sort()
        return keylist

    def get(self, key: str) -> float:
        """Gets the specified score, or 0 if it does not exist"""
        try:
            return self.__dict__["scores"][key]
        except KeyError:
            return 0.0

    def dict(self) -> Dict[str, float]:
        """Gets the underlying score dictionary"""
        return self.__dict__["scores"]

    def is_likely_mother(self):
        """Uses a simple threshold to check whether it is likely that this mother is a mother cell."""
        return self.total() > 3

    def is_unlikely_mother(self):
        """Uses a simple threshold to check whether it is likely that this mother is a mother cell."""
        return self.total() < 2

    def __str__(self):
        return str(self.total()) + " (based on " + str(self.__dict__["scores"]) + ")"

    def __repr__(self):
        return "Score(**" + repr(self.__dict__["scores"]) + ")"


class Family:
    """A mother cell with two daughter cells."""
    mother: Particle
    daughters: Set[Particle]  # Size of two, ensured by constructor.

    def __init__(self, mother: Particle, daughter1: Particle, daughter2: Particle):
        """Creates a new family. daughter1 and daughter2 can be swapped without consequences."""
        self.mother = mother
        self.daughters = {daughter1, daughter2}

    @staticmethod
    def _pos_str(particle: Particle) -> str:
        return "(" + ("%.2f" % particle.x) + ", " + ("%.2f" % particle.y) + ", " + ("%.0f" % particle.z) + ")"

    def __str__(self):
        return self._pos_str(self.mother) + " " + str(self.mother.time_point_number()) + "---> " \
               + " and ".join([self._pos_str(daughter) for daughter in self.daughters])

    def __repr__(self):
        return "Family(" + repr(self.mother) + ", " +  ", ".join([repr(daughter) for daughter in self.daughters]) + ")"

    def __hash__(self):
        hash_code = hash(self.mother)
        for daughter in self.daughters:
            hash_code += hash(daughter)
        return hash_code

    def __eq__(self, other):
        return isinstance(other, self.__class__) \
            and other.mother == self.mother \
            and other.daughters == self.daughters


class ScoredFamily:
    """A family with a score attached. The higher the score, the higher the chance that this family is a "real" family,
    and not just some artifact."""
    family: Family
    score: Score

    def __init__(self, family: Family, score: Score):
        self.family = family
        self.score = score

    def __repr__(self):
        return "<" + str(self.family) + " scored " + str(self.score) + ">"


class _ScoresOfTimePoint:
    _mother_scores: Dict[Family, Score]

    def __init__(self):
        self._mother_scores = dict()

    def mother_score(self, family: Family, score: Optional[Score] = None) -> Score:
        """Gets or sets the mother score of the given particle. Raises KeyError if no score has been set for this
         particle. Raises ValueError if you're looking in the wrong time point.
         """
        if score is not None:
            self._mother_scores[family] = score
            return score
        return self._mother_scores[family]

    def mother_scores(self, mother: Optional[Particle] = None) -> Iterable[ScoredFamily]:
        """Gets all mother scores of either all putative mothers, or just the given mother (if any)."""
        for family, score in self._mother_scores.items():
            if mother is not None:
                if family.mother != mother:
                    continue
            yield ScoredFamily(family, score)

class ScoresCollection:
    _all_scores: Dict[int, _ScoresOfTimePoint]

    def __init__(self):
        self._all_scores = dict()

    def set_family_score(self, family: Family, score: Score):
        """Sets the score of the given family to the given value."""
        scores_of_time_point = self._all_scores.get(family.mother.time_point_number())
        if scores_of_time_point is None:
            scores_of_time_point = _ScoresOfTimePoint()
            self._all_scores[family.mother.time_point_number()] = scores_of_time_point
        scores_of_time_point.mother_score(family, score)

    def of_time_point(self, time_point: TimePoint) -> Iterable[ScoredFamily]:
        """Gets the scores of all mother cells in a time point."""
        scores_of_time_point = self._all_scores.get(time_point.time_point_number())
        if scores_of_time_point is None:
            return []
        return scores_of_time_point.mother_scores()

    def of_mother(self, particle: Particle) -> Iterable[ScoredFamily]:
        """Gets all scores registered for the given mother."""
        scores_of_time_point = self._all_scores.get(particle.time_point_number())
        if scores_of_time_point is None:
            return []
        return scores_of_time_point.mother_scores(particle)

