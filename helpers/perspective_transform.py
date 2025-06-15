import cv2
import numpy as np

class PerspectiveTransformer:
    """
    A class to perform perspective transformations on 2D points using a homography matrix.

    This class calculates a homography matrix from a set of source and target points
    and then provides a method to transform other points according to this perspective.
    """

    def __init__(
        self,
        source: np.ndarray[np.float32],
        target: np.ndarray[np.float32]
    ):
        """
        Initializes the PerspectiveTransformer by calculating the homography matrix.

        Args:
            source (np.ndarray[np.float32]): A NumPy array of shape (4, 2)
                                              containing inferred corner points (x, y)
                                              in the original board perspective.
            target (np.ndarray[np.float32]): A NumPy array of shape (4, 2)
                                              containing corresponding target corner points (x, y)
                                              in the new square perspective.

        Raises:
            ValueError: If source and target shapes do not match,
                        if points are not 2D coordinates,
                        if more or less than 4 points are provided, or
                        if the homography matrix cannot be calculated.
        """
        if source.shape[1] != 2 or target.shape[1] != 2:
            raise ValueError("Source and target points must be 2D coordinates with shape (N, 2).")

        if source.shape != target.shape:
            raise ValueError(f"Source and target must be of same shape. Got source: {source.shape}, target: {target.shape}")

        if source.shape[0] != 4:
            raise ValueError(
                f"At least 4 points are required for homography calculation. Got {source.shape[0]} points."
            )

        source = source.astype(np.float32)
        target = target.astype(np.float32)

        self.m, _ = cv2.findHomography(source, target, cv2.RANSAC, 5.0) # Added RANSAC for robustness
        
        if self.m is None:
            raise ValueError(
                "Homography matrix could not be calculated. This might be due to "
                "collinear points or insufficient variation in the input points."
            )

    def transform_points(
        self,
        points: np.ndarray[np.float32]
    ) -> np.ndarray[np.float32]:
        """
        Transforms a set of 2D points using the calculated homography matrix.

        Args:
            points (np.ndarray[np.float32]): A NumPy array of shape (N, 2)
                                              containing N points (x, y) to be transformed.

        Returns:
            np.ndarray[np.float32]: A NumPy array of shape (N, 2)
                                    containing the transformed points (x', y').

        Raises:
            ValueError: If points are not 2D coordinates.
        """
        if points.size == 0:
            return points

        if points.shape[1] != 2:
            raise ValueError("Input points must be 2D coordinates with shape (M, 2).")

        reshaped_points = points.reshape(-1, 1, 2).astype(np.float32)
        transformed_points = cv2.perspectiveTransform(reshaped_points, self.m)
        return transformed_points.reshape(-1, 2).astype(np.float32)

    def warped_image(
        self,
        img: np.ndarray[np.float32],
        N: int
    ) -> np.ndarray[np.float32]:
        
        warped_image = cv2.warpPerspective(img, self.m, (N, N))
        return warped_image
