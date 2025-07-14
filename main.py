from ErrorFile.Detection.FileInspector import FileInspector


file_path = r'tests/files/TOM_损坏.jpg'
image_mode = 'fast'  # 或 'fast'
result = FileInspector(file_path, image_mode).inspect()
print(result)
