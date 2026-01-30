from PIL import Image
import os

def convert_to_ico():
    input_path = 'assets/icon.png'
    output_path = 'assets/icon.ico'
    
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    img = Image.open(input_path)
    img.save(output_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print(f"Converted {input_path} to {output_path}")

if __name__ == "__main__":
    convert_to_ico()
