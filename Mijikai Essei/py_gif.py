from PIL import Image
import os
import json

def extract_frames_with_duration(gif_path):
    # Open the GIF file
    gif = Image.open(gif_path)
    
    # Create the output directory if it doesn't exist
    output_dir = os.path.splitext(gif_path)[0]
    os.makedirs(output_dir, exist_ok=True)
    
    frame = 0
    durations = []
    
    while True:
        # Save the current frame as PNG
        frame_path = os.path.join(output_dir, f"{os.path.basename(output_dir)}_{frame:03d}.png")
        gif.save(frame_path, format="PNG")
        
        # Store the duration of the current frame
        durations.append(gif.info['duration'])
        
        frame += 1
        
        try:
            # Move to the next frame
            gif.seek(frame)
        except EOFError:
            # Exit the loop when there are no more frames
            break

    # Save the durations to a JSON file
    with open(os.path.join(output_dir, "durations.json"), 'w') as f:
        json.dump(durations, f)

    print(f"Extracted {frame} frames with durations to {output_dir}")

# sample
extract_frames_with_duration("0240724_121630_16245.gif")

def regenerate_gif(output_dir):
    # Load the durations
    with open(os.path.join(output_dir, "durations.json"), 'r') as f:
        durations = json.load(f)
    
    # Collect the frames
    frames = []
    for i in range(len(durations)):
        frame_path = os.path.join(output_dir, f"{os.path.basename(output_dir)}_{i:03d}.png")
        frames.append(Image.open(frame_path))
    
    # Save the frames as a new GIF with the original durations
    gif_path = os.path.join(output_dir, "new_gif.gif")
    frames[0].save(gif_path, save_all=True, append_images=frames[1:], duration=durations, loop=0)

    print(f"Regenerated GIF saved to {gif_path}")

# sample
regenerate_gif("new_0240724_121630_16245.gif")
