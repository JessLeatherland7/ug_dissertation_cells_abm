# -*- coding: utf-8 -*-

import numpy as np

CUBE_ROOT_2 = 1.259921
TAN_10_DEGREES = 0.176327

def rand_unit_vec():
    """Returns a random 3D unit vector"""
    rand_direction = np.random.uniform(-1, 1, [3])
    return (rand_direction / np.linalg.norm(rand_direction))

def get_all_subclasses(parent_class):
    """Returns all direct and indirect subclasses of the given parent class."""
    subclasses = []
    classes_to_check = [parent_class]
    while classes_to_check:
        parent = classes_to_check.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                subclasses.append(child)
                classes_to_check.append(child)
    return subclasses