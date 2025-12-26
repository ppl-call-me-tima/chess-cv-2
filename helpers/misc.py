import cv2

def cv2pygame(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.transpose(image)
    return image
