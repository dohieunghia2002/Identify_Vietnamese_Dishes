import matplotlib.pyplot as plt
import cv2


def crop_image(image, coordinates):
    # coordinates of bounding box yolo x1, y1, x2, y2
    x1, y1, x2, y2 = map(int, coordinates)

    cropped_image = image[y1:y2, x1:x2]
    return cropped_image

def convertIdx2Class(set_index, classes):
    result_set = {classes[item] for item in set_index}
    return result_set

def draw_bouding_box(image, boxes, detected_cls, names):
    for index, (box, cls) in enumerate(zip(boxes, detected_cls)):
        x1, y1, x2, y2 = box

        color = (255, 0, 0)
        left, top, right, bottom = int(x1), int(y1), int(x2), int(y2)
        label = names.get(int(cls))

        cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 1)
        text_color = (255, 255, 255) # white color
        bg_color = (0, 255, 0)
        image[top - 15:top, left:right, :] = bg_color
        cv2.putText(image, label, (left, top - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
    
    return image

def show_img(img):
    # Convert BGR to RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    plt.imshow(img)
    plt.title("Detected Objects")
    plt.show()