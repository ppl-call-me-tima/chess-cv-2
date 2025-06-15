import numpy as np

def sort_points_by_angle(pts):
    # Calculate centroid
    center = pts.mean(axis=0)

    # Calculate angles
    angles = np.arctan2(pts[:, 1] - center[1], pts[:, 0] - center[0])

    sorted_indices = np.argsort(angles)
    return pts[sorted_indices]
