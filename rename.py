# import os

# for cnt, filename in enumerate(os.listdir('new/valid/images')):
#     tmp = filename.split('.')
#     sub = tmp[0].split('-')
#     new_name = f"{sub[0]}_{sub[1]}.{tmp[3]}"
#     old_file = os.path.join('new/valid/images', filename)
#     new_file = os.path.join('new/valid/images', new_name)
#     os.rename(old_file, new_file)
#     print(old_file, new_file)


import os
from PIL import Image

# Đường dẫn đến thư mục chứa các file hình ảnh
folder_path = 'E:/Phuccc/choi-ga'

# Tạo thư mục đầu ra nếu chưa có
output_folder = "E:/Phuccc/b"
os.makedirs(output_folder, exist_ok=True)

# Đếm số lượng file để đặt tên
file_count = 1

# Duyệt qua từng file trong thư mục
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    
    # Mở hình ảnh
    with Image.open(file_path) as img:
        # Chuyển đổi định dạng sang JPG
        new_filename = f"choi-ga_{file_count:04d}.jpg"
        new_file_path = os.path.join(output_folder, new_filename)
        
        # Lưu hình ảnh với định dạng JPG
        img.convert('RGB').save(new_file_path, 'JPEG')
        
        file_count += 1

print(f"Đã chuyển đổi {file_count - 1} file hình ảnh sang định dạng JPG và đổi tên thành công.")

