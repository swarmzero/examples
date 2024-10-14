from livepeer_ai import Livepeer
from dotenv import load_dotenv
import os

load_dotenv()

livepeer_api_key= os.getenv("LIVEPEER_API_KEY")

text2img_model_list = [
    'SG161222/RealVisXL_V4.0_Lightning',
    'ByteDance/SDXL-Lightning',
    'SG161222/Realistic_Vision_V6.0_B1_noVAE',
    'stabilityai/stable-diffusion-xl-base-1.0',
    'runwayml/stable-diffusion-v1-5',
    'prompthero/openjourney-v4',
    'SG161222/RealVisXL_V4.0',
    'stabilityai/sd-turbo',
    'stabilityai/sdxl-turbo',
    'stabilityai/stable-diffusion-3-medium-diffusers'
]

img2video_model_list = [
    'stable-video-diffusion-img2vid-xt',
    'stabilityai/stable-video-diffusion-img2vid-xt-1-1',   
]

img2img_model_list = [
    'timbrooks/instruct-pix2pix',
    'ByteDance/SDXL-Lightning',
    'SG161222/RealVisXL_V4.0',
    'SG161222/RealVisXL_V4.0_Lightning',
    'stabilityai/sd-turbo',
    'stabilityai/sdxl-turbo'
]

segment_model_list = [
"facebook/sam2-hiera-large"
"facebook/sam2-hiera-base-plus",
"facebook/sam2-hiera-small",
"facebook/sam2-hiera-tiny"
]

def text_to_image(prompt: str, model_id: str = text2img_model_list[1]):
    """
    This function generates an image from a text prompt using the Livepeer AI API.

    Args:
        prompt (str): The text prompt to guide image generation.
        
    Returns:
        str: The URL of the generated image.
    """
    s = Livepeer(http_bearer=livepeer_api_key)

    res = s.generate.text_to_image(request={
        "prompt": prompt,
        "model_id": model_id,
        # Optional fields
        # "loras": { "latent-consistency/lcm-lora-sdxl": 1.0, "nerijs/pixel-art-xl": 1.2 },  # Low-Rank Adaptation models and weights
        # "height": 1080,                              # Height of the generated image in pixels
        # "width": 1920,                               # Width of the generated image in pixels
        # "guidance_scale": 7.5,                       # Degree to which the model follows the prompt (higher values = closer to prompt)
        # "negative_prompt": "bad quality",            # Text prompt to exclude from image generation
        # "safety_check": True,                        # Perform a safety check to filter offensive content
        # "seed": 42,                                  # Set seed for reproducibility
        # "num_inference_steps": 50,                   # Number of denoising steps for improved quality
        # "num_images_per_prompt": 1                   # Number of images generated per prompt
    })
    
    print(res)
    
    if res.image_response is not None and res.image_response.images:
        generated_image_url = res.image_response.images[0].url
        return generated_image_url
    else:
        return None
    
def image_to_video(image_path: str, model_id: str = img2video_model_list[1]):
    """
    This function generates a video from an image using the Livepeer AI API.

    Args:
        image_path (str): The path to the image to be used for video generation.
        
    Returns:
        str: The URL of the generated video.
    """
    s = Livepeer(http_bearer=livepeer_api_key)

    with open(image_path, "rb") as image_file:
        image_content = image_file.read()

    res = s.generate.image_to_video(request={
        "image": {
            "file_name": image_path.split('/')[-1],
            "content": image_content,
        },
        "model_id": model_id,
        # Optional fields
        # "height": 1080,                             # Height of the generated video in pixels
        # "width": 1920,                              # Width of the generated video in pixels
        #"fps": 24,                                  # Frames per second for the generated video
        # "motion_bucket_id": 5,                      # Conditions motion amount (higher values = more motion)
        # "noise_aug_strength": 0.5,                  # Amount of noise added, reduces resemblance to original image and increases motion
        # "safety_check": True,                       # Enable safety checks to filter harmful content
        # "seed": 42,                                 # Set seed for reproducibility
        # "num_inference_steps": 50                   # Number of denoising steps for better quality
    })
    
    print(res)
    
    if res.video_response is not None and res.video_response.images:
        generated_video_url = res.video_response.images[0].url
        return generated_video_url
    else:
        return None
    
def upscale_image(prompt: str, image_path: str, model_id: str = 'stabilityai/stable-diffusion-x4-upscaler'):
    """
    This function upscales an image using the Livepeer AI API.

    Args:
        prompt (str): The text prompt to guide the upscaled image generation.
        image_path (str): The path to the image to be upscaled.
        
    Returns:
        str: The URL of the upscaled image.
    """
    s = Livepeer(http_bearer=livepeer_api_key)

    with open(image_path, "rb") as image_file:
        image_content = image_file.read()

    res = s.generate.upscale(request={
        "prompt": prompt,
        "image": {
            "file_name": image_path.split('/')[-1],
            "content": image_content,
        },
        "model_id": model_id,
        # Optional fields
        # "safety_check": True,   # Perform a safety check to filter offensive content
        # "seed": 42,             # Set seed for reproducible results
        # "num_inference_steps": 50,  # Number of denoising steps (higher = better quality but slower)
    })
    
    print(res)
    
    if res.image_response is not None and res.image_response.images:
        upscaled_image_url = res.image_response.images[0].url
        return upscaled_image_url
    else:
        return None
    
def image_to_image(prompt: str, image_path: str, model_id: str = img2img_model_list[0]):
    """
    This function transforms an image based on a text prompt using the Livepeer AI API.

    Args:
        prompt (str): The text prompt to guide image generation.
        image_path (str): The path to the image to be modified.
        
    Returns:
        str: The URL of the transformed image.
    """
    s = Livepeer(http_bearer=livepeer_api_key)

    with open(image_path, "rb") as image_file:
        image_content = image_file.read()

    res = s.generate.image_to_image(request={
        "prompt": prompt,
        "image": {
            "file_name": image_path.split('/')[-1],
            "content": image_content,
        },
        "model_id": model_id,
        # Optional fields
        # "loras": { "latent-consistency/lcm-lora-sdxl": 1.0, "nerijs/pixel-art-xl": 1.2 },  # Low-Rank Adaptation models and weights
        # "strength": 0.75,                             # Degree of transformation (0 to 1)
        # "guidance_scale": 7.5,                        # Pushes model towards text prompt (higher values = closer to text prompt)
        # "image_guidance_scale": 1.0,                  # Degree to which generated image is influenced by the original image
        # "negative_prompt": "bad quality",             # What to exclude from image generation
        # "safety_check": True,                         # Enable safety checks to filter out harmful content
        # "seed": 42,                                   # Set a seed for reproducible results
        # "num_inference_steps": 50,                    # Number of denoising steps for better quality
        # "num_images_per_prompt": 1                    # Number of images generated per prompt
    })
    
    print(res)
    
    if res.image_response is not None and res.image_response.images:
        generated_image_url = res.image_response.images[0].url
        return generated_image_url
    else:
        return None
    
def segment_anything(image_path: str, model_id: str = segment_model_list[0]):
    """
    This function segments an image using the Livepeer AI API.

    Args:
        image_path (str): The path to the image to be segmented.
        
    Returns:
        dict: The segmentation response including masks or other segmentation outputs.
    """
    s = Livepeer(http_bearer=livepeer_api_key)

    with open(image_path, "rb") as image_file:
        image_content = image_file.read()

    res = s.generate.segment_anything2(request={
        "image": {
            "file_name": image_path.split('/')[-1],
            "content": image_content,
        },
        "model_id": model_id,
        # Optional fields
        # "point_coords": [[100, 200], [300, 400]],  # Nx2 array for point prompts in (X, Y) pixel format
        # "point_labels": [1, 0],                   # Labels for points (1 = foreground, 0 = background)
        # "box": [50, 50, 300, 300],                # Box prompt in XYXY format
        # "mask_input": "previous_mask_data",       # Low-res mask from a previous iteration (1xHxW)
        # "multimask_output": True,                 # If true, returns multiple masks for ambiguous prompts
        # "return_logits": True,                    # If true, returns un-thresholded mask logits
        # "normalize_coords": True                  # If true, normalizes point coordinates to [0,1] range
    })
    
    print(res)
    
    if res.masks_response is not None:
        return res.masks_response.masks
    else:
        return None
    
def audio_to_text(audio_path: str, model_id: str = "openai/whisper-large-v3"):
    """
    This function transcribes an audio file using the Livepeer AI API.

    Args:
        audio_path (str): The path to the audio file to be transcribed.        
    Returns:
        str: The transcribed text from the audio file.
    """
    s = Livepeer(http_bearer=livepeer_api_key)

    with open(audio_path, "rb") as audio_file:
        audio_content = audio_file.read()

    res = s.generate.audio_to_text(request={
        "audio": {
            "file_name": audio_path.split('/')[-1],
            "content": audio_content,
        },
        "model_id": model_id,
    })
    
    print(res)
    
    if res.text_response is not None:
        return res.text_response.text
    else:
        return None