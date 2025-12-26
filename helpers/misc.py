import cv2
import numpy as np

def corners_not_detected():
    text = "Corners\nNot\nDetected"
    font = cv2.FONT_HERSHEY_COMPLEX
    scale = 2
    thickness = 2
    color = (255, 255, 255)
    
    text_size, _ = cv2.getTextSize(text, font, scale, thickness)
    
    x, y0 = (0, 50)
    line_height = text_size[1] + 5
    
    img = np.zeros((350, 350), np.uint8)
    
    for i, line in enumerate(text.split("\n")):
        y = y0 + i * line_height
        cv2.putText(img, line, (x, y), font, scale, color, thickness)
    
    return img

def cv2pygame(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.transpose(image)
    # image = cv2.flip(image, 0)
    return image
