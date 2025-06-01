from RoDevGameEngine.physics.collider import OBB
from RoDevGameEngine import sceneManager
from RoDevGameEngine.gizmos.line import Line
from RoDevGameEngine.transform import transform
from RoDevGameEngine.sceneManager import get_all_objects
import glm

class RaycastHit:
    def __init__(self, hit_pos, hit_object):
        self.pos = hit_pos
        self.hit = hit_object

def raycast(pos: glm.vec3, distance: float, rot: glm.vec3, ignored_obbs:list[OBB]=None):
    direction = glm.normalize(rot)  # Ensure it's a unit direction
    end_point = pos + direction * distance

    for obj in get_all_objects():
        for obb in obj.get_components(OBB):
            if obb not in ignored_obbs:
                hit = ray_intersects_obb(pos, direction, obb, distance)
                if hit:
                    sceneManager.sceneManager.line_renderer.add_line(Line(pos, hit.pos, glm.vec4(1, 1, 0, 1)))
                    return hit

    sceneManager.sceneManager.line_renderer.add_line(Line(pos, end_point, glm.vec4(1, 0, 0, 1)))
    return None

def ray_intersects_obb(ray_origin, ray_dir, obb, max_distance):
    center = obb.center
    axes = obb.get_axes()
    half_sizes = obb.size

    p = center - ray_origin
    t_min = 0.0
    t_max = max_distance

    for i in range(3):  # X, Y, Z axes
        axis = glm.normalize(axes[i])
        e = glm.dot(axis, p)
        f = glm.dot(ray_dir, axis)

        if abs(f) > 1e-6:
            t1 = (e + half_sizes[i]) / f
            t2 = (e - half_sizes[i]) / f
            t1, t2 = min(t1, t2), max(t1, t2)

            t_min = max(t_min, t1)
            t_max = min(t_max, t2)

            if t_min > t_max:
                return None  # No intersection
        else:
            if -e - half_sizes[i] > 0 or -e + half_sizes[i] < 0:
                return None  # Ray is parallel and outside the slab

    hit_distance = t_min if t_min >= 0 else t_max
    if 0 <= hit_distance <= max_distance:
        hit_point = ray_origin + ray_dir * hit_distance
        return RaycastHit(hit_point, obb.parent)

    return None