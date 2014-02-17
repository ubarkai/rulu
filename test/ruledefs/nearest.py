from rulu import *

class Point(Class):
    X = NumberField()
    Y = NumberField()

class Node(Fact):
    point = InstanceField(Point)
    index = IntegerField()
    
@NumberRuleFunc
def calc_dist(p1, p2):
    return float((p1.X-p2.X)**2 + (p1.Y-p2.Y)**2) ** .5

import nearest_distance_rules
Distance = nearest_distance_rules.make_rule(Node)

Nearest = RuleDef(
    foreach(Distance),
    fields(index1=int, index2=int, point1=Point, point2=Point, distance=float)
)

@Nearest._groupby(Distance.index1)
def find_nearest(distances, assert_, index1):
    assert_(**min(distances, key=lambda d:d.distance)._as_dict()) 
