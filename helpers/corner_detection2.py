import cv2
import numpy as np

def get_chessboard_corners(result, image):
    # result[0].show()
    
    if result.masks is None:
        return None, "No chessboard detected"
    
    mask = result.masks.data[0].cpu().numpy()
    mask = (mask * 255).astype(np.uint8)
    
    # Resize to match original image
    if mask.shape != image.shape[:2]:
        mask = cv2.resize(mask, (image.shape[1], image.shape[0]))
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None, "No contours found in mask"
    
    # Get largest contour
    largest_contour = max(contours, key=cv2.contourArea)
    
    # Approximate to quadrilateral
    epsilon = 0.02 * cv2.arcLength(largest_contour, True)
    approx = cv2.approxPolyDP(largest_contour, epsilon, True)
    
    # Ensure we have 4 corners
    if len(approx) == 4:
        corners = approx.reshape(-1, 2)
    else:
        # Fallback: get convex hull and find 4 extreme points
        hull = cv2.convexHull(largest_contour)
        corners = get_four_corners_from_hull(hull)
    
    return corners.astype(int)

def get_four_corners_from_hull(hull):
    """Extract 4 corner points from convex hull"""
    hull = hull.reshape(-1, 2)
    
    # Find extreme points
    top_left = hull[np.argmin(hull.sum(axis=1))]
    bottom_right = hull[np.argmax(hull.sum(axis=1))]
    top_right = hull[np.argmin(hull[:, 1] - hull[:, 0])]
    bottom_left = hull[np.argmax(hull[:, 1] - hull[:, 0])]
    
    return np.array([top_left, top_right, bottom_right, bottom_left])
