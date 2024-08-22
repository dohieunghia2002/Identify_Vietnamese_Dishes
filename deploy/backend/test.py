# import pandas as pd
# from ultralytics import YOLO
# import cv2
# import os
# from custom_utils import convertIdx2Class
# from unidecode import unidecode

# excel_file_path = './assets/Chi_Tiet_Mon_An_New.xlsx'
# folder_path = 'E:/Yolo_detect/data/com-tam-long-xuyen'
# NAME = "Cơm tấm Long Xuyên"
# model_yolov8 = YOLO('./assets/models/yolov8_best_862.pt')
# classes_path = './assets/classes.txt'

# classes_ingre = []
# with open(classes_path, 'r', encoding='utf-8') as file:
#     lines = [line.strip() for line in file]
#     classes_ingre = lines

# df = pd.read_excel(excel_file_path)

# def preprocess_dataframe():
#     global df
#     normalized_df = df.drop(df.columns[[0, -1]], axis=1)
    
#     for index, row in normalized_df.iterrows():
#         for col in normalized_df.columns:
#             value = row[col]
#             if pd.notna(value):
#                 name_without_accents = unidecode(value)
#                 values = name_without_accents.split(', ')
#                 for i in range(len(values)):
#                     values[i] = values[i].replace(' ', '-')
#                 row[col] = ', '.join(values)

#     return normalized_df

# normalized_df = preprocess_dataframe()


# def find_foodname_ver_narrow(set_detected_ingre):
#     global normalized_df
#     global df
#     distances = []

#     for index, row in normalized_df.iterrows():
#         values = {}
#         values["prior"] = set(row["Priorities"].split(', '))
#         values["main"] = set(row["Ingredients"].split(', '))
#         values["extra"] = set(row["Secondary Ingredients"].split(', ')) if pd.notna(row["Secondary Ingredients"]) else set()

#         # Không khớp với ƯU TIÊN
#         no_match_prior = values["prior"].difference(set_detected_ingre)

#         # Không khớp với CHÍNH
#         no_match_main = values["main"].difference(set_detected_ingre)

#         # Khớp với PHỤ
#         match_extra = values["extra"].intersection(set_detected_ingre)

#         # Phần tử thuộc detect nhưng không thuộc bộ luật CHÍNH & PHỤ
#         combine = values["prior"].union(values["main"])
#         combine = combine.union(values["extra"])
#         redundancy = set_detected_ingre.difference(combine)

#         shortage_score = (len(no_match_prior) * 10) + len(no_match_main) - (len(match_extra)*0.5)
#         redundancy_score = len(redundancy)
#         score = shortage_score + redundancy_score
        
#         # print(index, score)
#         distances.append(score)

#     min_value = min(distances)
#     min_indices = [i for i, value in enumerate(distances) if value == min_value]

#     predicted_food = []
#     for min_index in min_indices:
#         predicted_food.append(df.loc[min_index, "Food"])
    
#     return predicted_food


# def find_foodname_ver_lengthen(set_detected_ingre):
#     global normalized_df
#     global df
#     distances = []

#     for index, row in normalized_df.iterrows():
#         values = {}
#         values["prior"] = set(row["Priorities"].split(', '))
#         values["main"] = set(row["Ingredients"].split(', '))
#         values["extra"] = set(row["Secondary Ingredients"].split(', ')) if pd.notna(row["Secondary Ingredients"]) else set()

#         # Không khớp với ƯU TIÊN
#         no_match_prior = values["prior"].difference(set_detected_ingre)

#         # Không khớp với CHÍNH
#         no_match_main = values["main"].difference(set_detected_ingre)
        
#         # Không khớp với PHỤ
#         no_match_extra = values["extra"].difference(set_detected_ingre)

#         # Phần tử thuộc detect nhưng không thuộc bộ luật CHÍNH & PHỤ
#         combine = values["prior"].union(values["main"])
#         combine = combine.union(values["extra"])
#         redundancy = set_detected_ingre.difference(combine)

#         shortage_score = (len(no_match_prior) * 10) + len(no_match_main) + (len(no_match_extra)*0.5)
#         redundancy_score = len(redundancy)
#         score = shortage_score + redundancy_score
        
#         distances.append(score)

#     min_value = min(distances)
#     min_indices = [i for i, value in enumerate(distances) if value == min_value]

#     predicted_food = []
#     for min_index in min_indices:
#         predicted_food.append(df.loc[min_index, "Food"])
    
#     return predicted_food


# def recognize_food():
#     global classes_ingre
#     global folder_path
#     global model_yolov8
#     global NAME

#     true_label = 0
#     temp = []

#     for f in os.listdir(folder_path):
#         filename = os.path.join(folder_path, f)
#         img = cv2.imread(filename)

#         results = model_yolov8(img, conf=0.3, save=False)
#         yolov8_detected_cls = results[0].boxes.cls.tolist()
#         v8_rm_duplicates = set(yolov8_detected_cls)
#         v8_rm_duplicates = [int(number) for number in v8_rm_duplicates]
#         v8_rm_duplicates = convertIdx2Class(v8_rm_duplicates, classes_ingre)

#         v8_predicted_food = find_foodname_ver_lengthen(v8_rm_duplicates)
        
#         if NAME in v8_predicted_food:
#             true_label += 1
#         else:
#             temp.append(filename)

#     print(true_label)

# recognize_food()

from unidecode import unidecode
from ultralytics import YOLO, RTDETR
import cv2

model_yolov9 = YOLO('assets/models/yolov9_best_85.pt')

def detect_ingredients(model, img):
    results = model(img, conf=0.3, save=False)
    names = results[0].names
    detected_cls = results[0].boxes.cls.tolist()
    boxes = results[0].boxes.xyxy.tolist()
    return names, detected_cls, boxes

img = cv2.imread("bbh_test_1.jpg")
yolov9_names, yolov9_detected_cls, yolov9_boxes = detect_ingredients(model_yolov9, img)
# print(yolov9_names)
# print(yolov9_detected_cls)
# print(yolov9_boxes)