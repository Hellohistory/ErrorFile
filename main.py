from ErrorFile.Detection.FileInspector import FileInspector


file_path = 'TestFiles/test.pdf'
image_mode = 'precise'  # 或 'fast'
result = FileInspector(file_path, image_mode).inspect()
print(result)
