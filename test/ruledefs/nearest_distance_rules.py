from rulu import *

def calc_dist(p1, p2):
    return ((p1.X-p2.X)**2 + (p1.Y-p2.Y)**2) ** .5

@NumberRuleFunc
def calc_dist_python(p1, p2):
    return float((p1.X-p2.X)**2 + (p1.Y-p2.Y)**2) ** .5

def python_free_distance_rule(Node, calc_dist=calc_dist):
    return RuleDef(
        condition(Node[0].index != Node[1].index),
        action(Assert(index1=Node[0].index, index2=Node[1].index, 
                      point1=Node[0].point, point2=Node[1].point, 
                      distance=calc_dist(Node[0].point, Node[1].point)))
    )
    
def python_func_distance_rule(Node):
    return python_free_distance_rule(Node, calc_dist=calc_dist_python)

def python_distance_rule(Node):
    Point = Node._fields['point']._type
    rule = RuleDef(
        fields(index1=int, index2=int, point1=Point, point2=Point, distance=float),
        foreach(Node[0], Node[1])
    )
    @rule._python_action
    def action(Node, assert_):
        if Node[0].index != Node[1].index:
            assert_(index1=Node[0].index, index2=Node[1].index, 
                    point1=Node[0].point, point2=Node[1].point, 
                    distance=calc_dist(Node[0].point, Node[1].point))
    return rule

make_rule = None
