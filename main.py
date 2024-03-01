from ErrorFile.Detection.FileInspector import FileInspector


file_path = r'D:\Code\Python Work\ErrorFile\TestFiles\TOM_损坏.jpg'
image_mode = 'precise'  # 或 'fast'
result = FileInspector(file_path, image_mode).inspect()
print(result)
