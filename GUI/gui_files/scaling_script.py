import os
import re

class GUIFileScaler:
    def __init__(self, scale_factor=1.2):
        self.scale_factor = scale_factor

    def scale_value(self, match):
        # Extracts the matched property name (key) and its numerical value
        prop, value = match.group(1), float(match.group(2))
        scaled_value = round(value * self.scale_factor)
        return f'{prop} = {scaled_value}'

    def process_content(self, content):
        # Regex pattern to match x, y, maxWidth, maxHeight props followed by their numerical values
        pattern = r'(\bx\b|\by\b|maxWidth|maxHeight) *= *(-?\d+(?:\.\d+)?)'
        return re.sub(pattern, self.scale_value, content)

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def write_file(file_path, content):
    with open(file_path, 'w') as file:
        file.write(content)

def process_files(directory):
    scaler = GUIFileScaler()
    for filename in os.listdir(directory):
        if filename.endswith('.gui'):  # Ensure it's a GUI file
            file_path = os.path.join(directory, filename)
            content = read_file(file_path)
            updated_content = scaler.process_content(content)
            if content != updated_content:  # Check if any changes were made
                write_file(file_path, updated_content)
            else:
                print(f"No changes have been made to {filename}.")  # Debugging print

if __name__ == "__main__":
    directory = os.path.dirname(os.path.abspath(__file__))
    process_files(directory)