from ErrorFile import inspect_file


file_path = r"tests/files/TOM_损坏.jpg"
is_ok, message = inspect_file(file_path, mode="precise")
print(f"File: {file_path}\nOK: {is_ok}\nMessage: {message}")
