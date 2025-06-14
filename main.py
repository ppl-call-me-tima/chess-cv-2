from ultralytics import YOLO
import cv2
import torch
import numpy as np

from perspective_transform import PerspectiveTransformer

model = YOLO(r"runs3\content\runs\segment\train3\weights\best.pt")
image = cv2.imread(r"C:\Users\2648a\Downloads\WhatsApp Image 2025-06-14 at 17.19.24.jpeg")
result = model.predict(image, conf=0.5, device=0)

result[0].show()
    
def create_binary_mask_from_ultralytics(results, original_image):
    """
    Extracts the largest mask from Ultralytics results, resizes it,
    and converts it to a binary NumPy array (0s and 255s).

    Args:
        results: The output from an Ultralytics segmentation model (e.g., model.predict(source)[0]).
        original_image: The original image the prediction was run on. This is needed
                        to get the correct output dimensions.

    Returns:
        A binary NumPy array (uint8) of the same size as the original image,
        or None if no masks are found.
    """
    # --- 1. Check if any masks were detected ---
    if results.masks is None:
        print("Warning: No masks found in the prediction results.")
        return None

    # --- 2. Extract mask data and find the largest one ---
    # The mask data is usually a tensor of shape [N, H, W] where N is the number of instances.
    masks_data = results.masks.data
    
    # Find the mask with the largest area by summing up the pixel values.
    # We move the tensor to CPU for numpy conversion.
    mask_areas = torch.sum(masks_data, dim=(1, 2))
    largest_mask_idx = torch.argmax(mask_areas)
    
    # Select the largest mask and convert to a NumPy array
    chessboard_mask = masks_data[largest_mask_idx].cpu().numpy()

    # --- 3. Resize the mask to match the original image's dimensions ---
    original_h, original_w = original_image.shape[:2]
    resized_mask = cv2.resize(
        chessboard_mask, 
        (original_w, original_h), 
        interpolation=cv2.INTER_LINEAR # INTER_LINEAR is good for up-sampling
    )

    # --- 4. Threshold and convert to binary format (0 and 255) ---
    # The resized mask still has float values (0.0 to 1.0).
    # We threshold it to create a strict binary mask.
    binary_mask = (resized_mask > 0.5).astype(np.uint8) * 255
    
    return binary_mask


def find_corners(binary_mask):
    """
    Finds the four extreme corners of the largest contour in a binary mask.

    Args:
        binary_mask: A NumPy array where the chessboard is 255 and background is 0.

    Returns:
        A NumPy array of shape (4, 1, 2) containing the four corner points,
        or None if no contour is found.
    """
    # Find all contours in the binary mask
    # cv2.RETR_EXTERNAL retrieves only the extreme outer contours.
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        print("Warning: No contours found in the mask.")
        return None

    # Assume the largest contour corresponds to the chessboard
    chessboard_contour = max(contours, key=cv2.contourArea)

    # Determine the extreme points along the contour
    # The contour is a list of (x, y) points
    leftmost = tuple(chessboard_contour[chessboard_contour[:, :, 0].argmin()][0])
    rightmost = tuple(chessboard_contour[chessboard_contour[:, :, 0].argmax()][0])
    topmost = tuple(chessboard_contour[chessboard_contour[:, :, 1].argmin()][0])
    bottommost = tuple(chessboard_contour[chessboard_contour[:, :, 1].argmax()][0])

    # Note: For a non-rotated rectangle, these points are mid-sides.
    # For a rotated rectangle, these points are the corners.
    # We will use a different method to find corners for a general polygon.
    
    # A more robust way for a general convex shape is to find corners
    # from the bounding box or by approximation (see next sections).
    # For this simple method, let's just return these points for demonstration.
    corners = np.array([[leftmost], [rightmost], [topmost], [bottommost]], dtype="int32")
    
    # Let's find the corners by another logic from the contour points
    # Argmin/max of sum/diff of coordinates
    s = chessboard_contour.sum(axis=2)
    top_left = tuple(chessboard_contour[s.argmin()][0])
    bottom_right = tuple(chessboard_contour[s.argmax()][0])
    
    diff = np.diff(chessboard_contour, axis=2)
    top_right = tuple(chessboard_contour[diff.argmin()][0])
    bottom_left = tuple(chessboard_contour[diff.argmax()][0])

    corners = np.array([top_left, top_right, bottom_right, bottom_left], dtype="float32")
    
    return corners


binary_mask = create_binary_mask_from_ultralytics(result[0], image)

BOARD_POINTS = np.array([
    (0, 0),
    (0, 800),
    (800, 800),
    (800, 0)
])

pieces_xy = np.array([
    (832, 133)
])

if binary_mask is not None:
    # Now you can use any function from the guide.
    # For example, using find_corners_with_approxpoly:
    corners = find_corners(binary_mask)
    
    transformer = PerspectiveTransformer(corners, BOARD_POINTS)
    transformed_points = transformer.transform_points(pieces_xy)
    
    print(transformed_points)
    
    if corners is not None:
        print("Successfully found 4 corners!")
        # Proceed with your logic (e.g., drawing the corners)
        viz_image = image.copy()
        print("CORNERS: ", corners)
        for corner in corners:
            cv2.circle(viz_image, tuple(corner.astype(int)), 10, (0, 255, 0), -1)        
        cv2.imshow("Final Corners", viz_image)
        cv2.waitKey(0)
    else:
        print("Could not approximate to a 4-sided polygon.")
else:
    print("Could not create a binary mask from the model output.")
