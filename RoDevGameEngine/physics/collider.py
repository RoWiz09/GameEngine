from RoDevGameEngine.transform import transform
from RoDevGameEngine.script import script

import glm

class colliderTypes:
    normal_collider = 0
    trigger_collider = 1

class OBB(script):
    def __init__(self, parent, script_path):
        super().__init__(parent, script_path)

        self.collider_type = colliderTypes.normal_collider

        self.parent = parent
        self.__parent_transform = parent.get_transform()

        self.offset = glm.vec3(0.5, 0.5, 0.5)
        rotated_offset = glm.vec3(self.__parent_transform.rotation_matrix * glm.vec4(self.offset * self.__parent_transform.scale, 0.0))
        self.center = self.__parent_transform.pos + rotated_offset
        self.size = self.__parent_transform.scale * 0.5  # Treat size as full size, store half-extents
        self.__rotation = glm.mat3(self.__parent_transform.rotation_matrix)  # Convert to 3x3 for local axes

    def get_axes(self):
        # Return the 3 local axes of the OBB (right, up, forward)
        return [
            glm.vec3(self.__rotation[0]),  # X-axis (right)
            glm.vec3(self.__rotation[1]),  # Y-axis (up)
            glm.vec3(self.__rotation[2])   # Z-axis (forward)
        ]

    def project_onto_axis(self, axis: glm.vec3) -> float:
        """Projects this OBB onto the given axis and returns the projection radius (scalar extent)."""
        axes = self.get_axes()
        return sum(abs(glm.dot(axis, a)) * h for a, h in zip(axes, self.size))

    def is_colliding_with(self, other: 'OBB') -> tuple[bool, dict | None]:
        """Returns (True, collision_info) if colliding, otherwise (False, None)."""
        axes_a = self.get_axes()
        axes_b = other.get_axes()
        relative_center = glm.vec3(other.center) - glm.vec3(self.center)

        test_axes = axes_a + axes_b + [glm.cross(a, b) for a in axes_a for b in axes_b]

        smallest_overlap = float('inf')
        collision_axis = None

        for axis in test_axes:
            if glm.length(axis) < 1e-6:
                continue

            axis = glm.normalize(axis)
            projection_a = self.project_onto_axis(axis)
            projection_b = other.project_onto_axis(axis)
            distance = abs(glm.dot(relative_center, axis))
            overlap = (projection_a + projection_b) - distance

            if overlap < 0:
                return False, None  # Found separating axis, no collision

            if overlap < smallest_overlap:
                smallest_overlap = overlap
                collision_axis = axis

        # Determine collision normal direction
        direction = glm.dot(relative_center, collision_axis)
        if direction < 0:
            collision_axis = -collision_axis  # Make sure the axis points from self to other

        collision_info = {
            "normal": collision_axis,
            "penetration_depth": smallest_overlap,
            "contact_point_estimate": self.center + collision_axis * (projection_a - smallest_overlap * 0.5)
        }

        return True, collision_info

    def update(self, deltatime):
        offset = self.offset * self.__parent_transform.scale
        rotated_offset = glm.vec3(self.__parent_transform.rotation_matrix * glm.vec4(offset, 0.0))
        self.center = self.__parent_transform.pos + rotated_offset

        if isinstance(self.collider_type, str):
            self.collider_type = colliderTypes.__getattribute__(colliderTypes, self.collider_type)
        super().update(deltatime)  
