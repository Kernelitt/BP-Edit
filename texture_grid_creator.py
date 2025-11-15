from PIL import Image
import os
import math

def create_texture_grid(folder_path):
    # Supported image extensions
    extensions = ('.png', '.jpg', '.jpeg')
    
    # Get all image files in the folder
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(extensions)]
    
    if not image_files:
        print("No image files found in the folder.")
        return
    
    # Load images and check sizes (assume all are the same)
    images = []
    for file in image_files:
        img_path = os.path.join(folder_path, file)
        img = Image.open(img_path)
        images.append(img)
    
    # Assume all images are the same size
    if not images:
        return
    img_width, img_height = images[0].size
    
    # Calculate grid dimensions (aim for square)
    num_images = len(images)
    grid_size = math.ceil(math.sqrt(num_images))
    grid_width = grid_size * img_width
    grid_height = grid_size * img_height
    
    # Create a new blank image for the grid
    grid = Image.new('RGBA', (grid_width, grid_height), (0, 0, 0, 0))  # Transparent background
    
    # Place images in the grid
    for i, img in enumerate(images):
        row = i // grid_size
        col = i % grid_size
        x = col * img_width
        y = row * img_height
        grid.paste(img, (x, y))
    
    # Save the grid
    output_path = os.path.join(folder_path, 'texture_grid.png')
    grid.save(output_path)
    print(f"Texture grid saved as {output_path}")

# Main execution
if __name__ == "__main__":
    folder_path = input("Enter the path to the folder with textures: ").strip()
    if os.path.isdir(folder_path):
        create_texture_grid(folder_path)
    else:
        print("Invalid folder path.")
