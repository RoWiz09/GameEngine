from RoDevGameEngine.physics.collider import OBB
from RoDevGameEngine.transform import transform
from RoDevGameEngine.sceneManager import get_all_objects
import glm

def raycast(pos: glm.vec3, distance: float, rot: glm.vec3):
    direction = glm.normalize(rot)  # Ensure it's a unit direction

    for obj in get_all_objects():
        for obb in obj.get_components(OBB):
            hit = ray_intersects_obb(pos, direction, obb, distance)
            if hit:
                return True

    return False

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
                return False  # No intersection
        else:
            # Ray is parallel to slab. No hit if origin not within slab
            if -e - half_sizes[i] > 0 or -e + half_sizes[i] < 0:
                return False

    return True
