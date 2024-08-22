from ultralytics import YOLO, RTDETR
import cv2
import math
import base64
import pandas as pd

from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from flask import request
from unidecode import unidecode
from custom_utils import crop_image, convertIdx2Class

app = Flask(__name__)

# Set up module
classes_path = './assets/classes.txt'
ingredients_path = './assets/ingredients_name.txt'
excel_file_path = './assets/rules.xlsx'

# models object detector
model_yolov8 = YOLO('./assets/models/yolov8_best_862.pt')
model_yolov9 = YOLO('./assets/models/yolov9_best_85.pt')
model_yolov10 = YOLO('./assets/models/yolov10_best_861.pt')
model_rtdetr = RTDETR('./assets/models/rt-detr_best_865.pt')

df = pd.read_excel(excel_file_path)
classes_ingre = []

with open(classes_path, 'r', encoding='utf-8') as file:
    lines = [line.strip() for line in file]
    classes_ingre = lines


def preprocess_dataframe():
    global df
    normalized_df = df.drop(df.columns[[0, -1]], axis=1)
    
    for index, row in normalized_df.iterrows():
        for col in normalized_df.columns:
            value = row[col]
            if pd.notna(value):
                name_without_accents = unidecode(value)
                values = name_without_accents.split(', ')
                for i in range(len(values)):
                    values[i] = values[i].replace(' ', '-')
                row[col] = ', '.join(values)

    return normalized_df

normalized_df = preprocess_dataframe()
    

CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


def detect_ingredients(model, img):
    results = model(img, conf=0.3, save=False)
    names = results[0].names
    detected_cls = results[0].boxes.cls.tolist()
    boxes = results[0].boxes.xyxy.tolist()
    return names, detected_cls, boxes


def find_foodname_ver_narrow(set_detected_ingre):
    global normalized_df
    global df
    distances = []

    for index, row in normalized_df.iterrows():
        values = {}
        values["prior"] = set(row["Priorities"].split(', '))
        values["main"] = set(row["Ingredients"].split(', '))
        values["extra"] = set(row["Secondary Ingredients"].split(', ')) if pd.notna(row["Secondary Ingredients"]) else set()

        # Không khớp với ƯU TIÊN
        no_match_prior = values["prior"].difference(set_detected_ingre)

        # Không khớp với CHÍNH
        no_match_main = values["main"].difference(set_detected_ingre)

        # Khớp với PHỤ
        match_extra = values["extra"].intersection(set_detected_ingre)

        # Phần tử thuộc detect nhưng không thuộc bộ luật CHÍNH & PHỤ
        combine = values["prior"].union(values["main"])
        combine = combine.union(values["extra"])
        redundancy = set_detected_ingre.difference(combine)

        shortage_score = (len(no_match_prior) * 10) + len(no_match_main) - (len(match_extra)*0.5)
        redundancy_score = len(redundancy)
        score = shortage_score + redundancy_score
        
        # print(index, score)
        distances.append(score)

    min_value = min(distances)
    min_indices = [i for i, value in enumerate(distances) if value == min_value]

    predicted_food = []
    for min_index in min_indices:
        predicted_food.append(df.loc[min_index, "Food"])
    
    return distances, predicted_food


def crop_obj_detected(img, boxes):
    detected_images = []
    for index, box in enumerate(boxes):
        cropped_image = crop_image(img, box)

        _, encoded_image = cv2.imencode('.jpg', cropped_image)
        encoded_image = base64.b64encode(encoded_image).decode('utf-8')
        detected_images.append(encoded_image)
    return detected_images


def calculate_belief_merging_base(v8_distances, v9_distances, v10_distances, rtdetr_distances):
    max_list = []
    sum_list = []
    Gmax = []

    for index, v8_value in enumerate(v8_distances):
        v9_value = v9_distances[index]
        v10_value = v10_distances[index]
        rtdetr_value = rtdetr_distances[index]

        max_value = max(v8_value, v9_value, v10_value, rtdetr_value)
        sum_value = v8_value + v9_value + v10_value + rtdetr_value
        numbers = [math.ceil(v8_value), math.ceil(v9_value), math.ceil(v10_value), math.ceil(rtdetr_value)]
        numbers = sorted(numbers)
        gmax = ' '.join(map(str, numbers))

        max_list.append(max_value)
        sum_list.append(sum_value)
        Gmax.append(gmax)
    
    return max_list, sum_list, Gmax


@app.route('/api/predict', methods=['POST'])
@cross_origin(origins='*')
def recognize_food():
    global classes_ingre
    global model_yolov8
    global model_yolov9
    global model_yolov10
    global model_rtdetr

    file = request.files['file']
    img = cv2.imread(file)
    yolov8_names, yolov8_detected_cls, yolov8_boxes = detect_ingredients(model_yolov8, img)
    yolov9_names, yolov9_detected_cls, yolov9_boxes = detect_ingredients(model_yolov9, img)
    yolov10_names, yolov10_detected_cls, yolov10_boxes = detect_ingredients(model_yolov10, img)
    rtdetr_names, rtdetr_detected_cls, rtdetr_boxes = detect_ingredients(model_rtdetr, img)

    v8_rm_duplicates = set(yolov8_detected_cls)
    v8_rm_duplicates = [int(number) for number in v8_rm_duplicates]
    yolov8_detected_cls = list(v8_rm_duplicates)
    v8_rm_duplicates = convertIdx2Class(v8_rm_duplicates, classes_ingre)

    v9_rm_duplicates = set(yolov9_detected_cls)
    v9_rm_duplicates = [int(number) for number in v9_rm_duplicates]
    yolov9_detected_cls = list(v9_rm_duplicates)
    v9_rm_duplicates = convertIdx2Class(v9_rm_duplicates, classes_ingre)

    v10_rm_duplicates = set(yolov10_detected_cls)
    v10_rm_duplicates = [int(number) for number in v10_rm_duplicates]
    yolov10_detected_cls = list(v10_rm_duplicates)
    v10_rm_duplicates = convertIdx2Class(v10_rm_duplicates, classes_ingre)

    rtdetr_rm_duplicates = set(rtdetr_detected_cls)
    rtdetr_rm_duplicates = [int(number) for number in rtdetr_rm_duplicates]
    rtdetr_detected_cls = list(rtdetr_rm_duplicates)
    rtdetr_rm_duplicates = convertIdx2Class(rtdetr_rm_duplicates, classes_ingre)

    v8_distances, v8_predicted_food = find_foodname_ver_narrow(v8_rm_duplicates)
    v9_distances, v9_predicted_food = find_foodname_ver_narrow(v9_rm_duplicates)
    v10_distances, v10_predicted_food = find_foodname_ver_narrow(v10_rm_duplicates)
    rtdetr_distances, rtdetr_predicted_food = find_foodname_ver_narrow(rtdetr_rm_duplicates)

    max_list, sum_list, Gmax = calculate_belief_merging_base(v8_distances, v9_distances, v10_distances, rtdetr_distances)

    v8_detected_img = crop_obj_detected(img, yolov8_boxes)
    v9_detected_img = crop_obj_detected(img, yolov9_boxes)
    v10_detected_img = crop_obj_detected(img, yolov10_boxes)
    rtdetr_detected_img = crop_obj_detected(img, rtdetr_boxes)

    return jsonify({
        'yolov8_detected_cls': yolov8_detected_cls,
        'yolov9_detected_cls': yolov9_detected_cls,
        'yolov10_detected_cls': yolov10_detected_cls,
        'rtdetr_detected_cls': rtdetr_detected_cls,

        'v8_distances': v8_distances,
        'v9_distances': v9_distances,
        'v10_distances': v10_distances,
        'rtdetr_distances': rtdetr_distances,

        'max_list': max_list,
        'sum_list': sum_list,
        'Gmax': Gmax,

        'v8_predicted_food': v8_predicted_food,
        'v9_predicted_food': v9_predicted_food,
        'v10_predicted_food': v10_predicted_food,
        'rtdetr_predicted_food': rtdetr_predicted_food,

        'v8_detected_img': v8_detected_img,
        'v9_detected_img': v9_detected_img,
        'v10_detected_img': v10_detected_img,
        'rtdetr_detected_img': rtdetr_detected_img
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='9999')