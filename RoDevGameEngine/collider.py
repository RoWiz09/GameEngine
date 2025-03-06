import glm

class colliderTypes:
    normal_collider = 0
    trigger_collider = 1

class OBB:
    def __init__(self, transform, collider_type : colliderTypes = colliderTypes.normal_collider):
        """
        - transform: The object's transform (position, rotation, scale)
        - base_size: The unscaled size of the object
        """
        self.transform = transform  
        self.base_size = glm.vec3(1, 1, 1)
        self.offset = glm.vec3(0.5, 0.5, 0.5)  # Adjust for cubes with 0-1 vertices
        self.colliderType = collider_type

    def get_rotation_matrix(self):
        """Extract the 3x3 rotation matrix from the model matrix."""
        model_matrix = self.transform.getModelMatrix()
        return glm.mat3(model_matrix)  # Extract rotation from the model matrix

    def get_corners(self):
        """Get the 8 corners of the OBB in world space."""
        rotation_matrix = self.get_rotation_matrix()
        half_size = (self.base_size * self.transform.scale) * 0.5

        # Adjust world position using the offset
        world_position = self.transform.pos + rotation_matrix * (self.offset * self.transform.scale)

        # Generate local-space corners
        local_corners = [
            glm.vec3(x, y, z) for x in (-half_size.x, half_size.x)
                              for y in (-half_size.y, half_size.y)
                              for z in (-half_size.z, half_size.z)
        ]

        # Convert to world space
        world_corners = [world_position + rotation_matrix * corner for corner in local_corners]
        return world_corners

    def get_axes(self):
        """Get the three local axes of the OBB in world space."""
        rotation_matrix = self.get_rotation_matrix()
        return [
            glm.normalize(rotation_matrix[0]),  # X-axis
            glm.normalize(rotation_matrix[1]),  # Y-axis
            glm.normalize(rotation_matrix[2])   # Z-axis
        ]

    def project_onto_axis(self, axis):
        """Projects the OBB onto the given axis and returns min/max projections."""
        corners = self.get_corners()
        min_proj = max_proj = glm.dot(corners[0], axis)

        for corner in corners[1:]:
            projection = glm.dot(corner, axis)
            min_proj = min(min_proj, projection)
            max_proj = max(max_proj, projection)

        return min_proj, max_proj

    def intersects(self, other):
        """Checks for OBB-OBB collision using the Separating Axis Theorem (SAT)."""
        axes = self.get_axes() + other.get_axes()  # Combine both OBB axes

        # Add cross products of axes to test additional separating planes
        for i in range(3):
            for j in range(3):
                cross_product = glm.cross(axes[i], axes[j])
                if glm.length(cross_product) > 1e-6:  # Avoid degenerate cases
                    axes.append(glm.normalize(cross_product))

        # Perform SAT test
        for axis in axes:
            minA, maxA = self.project_onto_axis(axis)
            minB, maxB = other.project_onto_axis(axis)

            if maxA < minB or maxB < minA:  # Found a separating axis → no collision
                return False

        return True  # No separating axis found → collision detected
