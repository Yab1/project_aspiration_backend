import cv2
import numpy as np


class RootSIFT:
    def __init__(self):
        self.extractor = cv2.SIFT_create()

    def compute(self, image, keypoints, eps=1e-7):
        # Compute SIFT descriptors
        keypoints, descriptors = self.extractor.compute(image, keypoints)

        # Check if descriptors are None
        if len(keypoints) == 0 or descriptors is None:
            return keypoints, None

        # Apply the Hellinger kernel by first L1-normalizing and taking the square-root
        descriptors /= descriptors.sum(axis=1, keepdims=True) + eps
        descriptors = np.sqrt(descriptors)

        # Return the RootSIFT descriptors
        return keypoints, descriptors


def compare_images(image1_path, image2_path):
    # Load the images in grayscale
    image1 = cv2.imread(image1_path, cv2.IMREAD_GRAYSCALE)
    image2 = cv2.imread(image2_path, cv2.IMREAD_GRAYSCALE)

    # Initialize SIFT detector
    sift = cv2.SIFT_create()
    rootSIFT = RootSIFT()  # noqa: N806

    # Detect keypoints and compute RootSIFT descriptors
    keypoints1 = sift.detect(image1)
    keypoints2 = sift.detect(image2)

    keypoints1, descriptors1 = rootSIFT.compute(image1, keypoints1)
    keypoints2, descriptors2 = rootSIFT.compute(image2, keypoints2)

    # If there are no descriptors, return 0% similarity
    if descriptors1 is None or descriptors2 is None:
        return 0.0

    # Use BFMatcher to find matches
    matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
    matches = matcher.match(descriptors1, descriptors2)

    # Compute the similarity score
    if len(matches) == 0:
        return 0.0

    # Compute the distances
    distances = [m.distance for m in matches]
    average_distance = np.mean(distances)

    # Normalize the score to a percentage (0-100)
    max_distance = max(distances)
    min_distance = min(distances)

    if max_distance == min_distance:
        return 100.0

    return 100 * (1 - (average_distance - min_distance) / (max_distance - min_distance))
