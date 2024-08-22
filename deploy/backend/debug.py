from ultralytics import YOLO, RTDETR
import cv2
import math
import pandas as pd
from unidecode import unidecode
import numpy as np
import os

# Đọc file cấu hình
classes_path = './assets/classes.txt'
excel_file_path = './assets/rules.xlsx'

# Tải các mô hình
model_yolov8 = YOLO('./assets/models/yolov8_best_862.pt')
model_yolov9 = YOLO('./assets/models/yolov9_best_85.pt')
model_rtdetr = RTDETR('./assets/models/rt-detr_best_865.pt')

df = pd.read_excel(excel_file_path)
classes_ingre = []

with open(classes_path, 'r', encoding='utf-8') as file:
    lines = [line.strip() for line in file]
    classes_ingre = lines

def convertIdx2Class(set_index, classes):
    result_set = {classes[item] for item in set_index}
    return result_set

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
        
        distances.append(score)

    min_value = min(distances)
    min_indices = [i for i, value in enumerate(distances) if value == min_value]

    predicted_food = []
    for min_index in min_indices:
        predicted_food.append(df.loc[min_index, "Food"])
    
    return distances, predicted_food

def calculate_belief_merging_base(v8_distances, v9_distances, rtdetr_distances):
    max_list = []
    sum_list = []
    Gmax = []

    for index, v8_value in enumerate(v8_distances):
        v9_value = v9_distances[index]
        rtdetr_value = rtdetr_distances[index]

        max_value = max(v8_value, v9_value, rtdetr_value)
        sum_value = v8_value + v9_value + rtdetr_value
        numbers = [math.ceil(v8_value), math.ceil(v9_value), math.ceil(rtdetr_value)]
        numbers = sorted(numbers, reverse=True)
        gmax = ' '.join(map(str, numbers))

        max_list.append(max_value)
        sum_list.append(sum_value)
        Gmax.append(gmax)
    
    return max_list, sum_list, Gmax

def belief_merging_find_foodname(max_list, sum, Gmax):
    # global normalized_df
    global df
    
    min_value_of_maxlist = min(max_list)
    indices_of_maxlist = [index for index, value in enumerate(max_list) if value == min_value_of_maxlist]

    min_value_of_sum = min(sum)
    indices_of_sum = [index for index, value in enumerate(sum) if value == min_value_of_sum]

    food_of_max = []
    for min_index in indices_of_maxlist:
        food_of_max.append(df.loc[min_index, "Food"])

    food_of_sum = []
    for min_index in indices_of_sum:
        food_of_sum.append(df.loc[min_index, "Food"])
    
    gmax_values = [
        list(map(int, item.split())) for item in Gmax
    ]
    avg_values = [np.mean(values) for values in gmax_values]
    min_value_of_gmax = np.min(avg_values)
    indices_of_gmax = [index for index, value in enumerate(avg_values) if value == min_value_of_gmax]
    food_of_gmax = []
    for min_index in indices_of_gmax:
        food_of_gmax.append(df.loc[min_index, "Food"])

    # return food_of_max, food_of_sum, food_of_gmax
    return indices_of_maxlist[0], indices_of_sum[0], indices_of_gmax[0]

predicted_max_belief_merging = []

def recognize_food(image_path):
    global predicted_max_belief_merging

    img = cv2.imread(image_path)
    yolov8_names, yolov8_detected_cls, yolov8_boxes = detect_ingredients(model_yolov8, img)
    yolov9_names, yolov9_detected_cls, yolov9_boxes = detect_ingredients(model_yolov9, img)
    rtdetr_names, rtdetr_detected_cls, rtdetr_boxes = detect_ingredients(model_rtdetr, img)

    v8_rm_duplicates = set(yolov8_detected_cls)
    v8_rm_duplicates = [int(number) for number in v8_rm_duplicates]
    yolov8_detected_cls = list(v8_rm_duplicates)
    v8_rm_duplicates = convertIdx2Class(v8_rm_duplicates, classes_ingre)

    v9_rm_duplicates = set(yolov9_detected_cls)
    v9_rm_duplicates = [int(number) for number in v9_rm_duplicates]
    yolov9_detected_cls = list(v9_rm_duplicates)
    v9_rm_duplicates = convertIdx2Class(v9_rm_duplicates, classes_ingre)

    rtdetr_rm_duplicates = set(rtdetr_detected_cls)
    rtdetr_rm_duplicates = [int(number) for number in rtdetr_rm_duplicates]
    rtdetr_detected_cls = list(rtdetr_rm_duplicates)
    rtdetr_rm_duplicates = convertIdx2Class(rtdetr_rm_duplicates, classes_ingre)

    v8_distances, v8_predicted_food = find_foodname_ver_narrow(v8_rm_duplicates)
    v9_distances, v9_predicted_food = find_foodname_ver_narrow(v9_rm_duplicates)
    rtdetr_distances, rtdetr_predicted_food = find_foodname_ver_narrow(rtdetr_rm_duplicates)

    max_list, sum_list, Gmax = calculate_belief_merging_base(v8_distances, v9_distances, rtdetr_distances)

    max_predicted_food, sum_predicted_food, gmax_predicted_food = belief_merging_find_foodname(max_list, sum_list, Gmax)

    # Kết quả
    # print("Detected Classes YOLOv8:", yolov8_detected_cls)
    # print("Detected Classes YOLOv9:", yolov9_detected_cls)
    # print("Detected Classes RTDETR:", rtdetr_detected_cls)
    # print("Predicted Food YOLOv8:", v8_predicted_food)
    # print("Predicted Food YOLOv9:", v9_predicted_food)
    # print("Predicted Food RTDETR:", rtdetr_predicted_food)
    # print("Max List:", max_list)
    # print("Sum List:", sum_list)
    # print("Gmax:", Gmax)
    # print("Max of Belief Merging Predicted Food:", max_predicted_food)
    # print("Sum of Belief Merging Predicted Food:", sum_predicted_food)
    # print("Gmax of Belief Merging Predicted Food:", gmax_predicted_food)
    
    predicted_max_belief_merging.append(max_predicted_food)


if __name__ == '__main__':
    images = []# tấm hình
    labels = []# nhãn
    imagePaths = []
    folders = ['bun-ca', 'hu-tieu-my-tho', 'bun-nuoc-leo', 'com-tam-long-xuyen', 'bun-hai-san-be-be',
               'banh-hoi-heo-quay', 'com-ga', 'cao-lau', 'mi-quang', 'bun-bo-hue', 'pho-ha-noi',
               'bun-muc', 'bun-moc', 'bun-dau-mam-tom']
    
    for k, category in enumerate(folders):
        for f in os.listdir('data_test/'+category):
            imagePaths.append(['data_test/' + category+'/'+f, k]) 
    
    for imagePath in imagePaths:
        data = imagePath[0]
        label = imagePath[1]

        images.append(data)
        labels.append(label)
    
    for img in images:
        recognize_food(images[0])
    
    print(predicted_max_belief_merging)
