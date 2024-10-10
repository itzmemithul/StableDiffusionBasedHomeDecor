import os
import torch
import gradio as gr
from diffusers import DiffusionPipeline, StableDiffusionImg2ImgPipeline
from huggingface_hub import HfApi
from openai import OpenAI
from PIL import Image
from io import BytesIO
import requests

from dotenv import load_dotenv
load_dotenv()

huggingfaceApKey = os.getenv("HUGGINGFACE_API_KEY")
hugging_face_user = os.getenv("HUGGING_FACE_USERNAME")
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

ikea_models = []
sd1point5_base_model = "stable-diffusion-v1-5/stable-diffusion-v1-5"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def getHuggingfaceModels():    
    api = HfApi()
    models = api.list_models(author=hugging_face_user, use_auth_token=huggingfaceApKey)

    prefix = hugging_face_user + "/" + "ikea_room_designs_sd"

    for model in models:
        if model.modelId.startswith(prefix):
            model_name = model.modelId.replace(hugging_face_user + "/", "")
            ikea_models.append(model_name)
    ikea_models.append(sd1point5_base_model)        
    return ikea_models

def improve_prompt(prompt):
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            max_tokens=77,
            messages=[
                {"role": "system", "content": "You are a room interior designer"},
                {"role": "user", "content": f"Generate a description for a room based on the following input. Keep it under 3 sentences: {prompt}"}
            ]
        )
        ai_generated_prompt = completion.choices[0].message.content
        print('AI Generated Prompt: ', ai_generated_prompt)
        return ai_generated_prompt
    except Exception as e:
        return f"Error generating AI prompt: {str(e)}"

def generate_ai_prompt(prompt, use_ai_prompt):
    if use_ai_prompt and prompt.strip() != "":
        prompt = improve_prompt(prompt)
        return prompt
    else:
        return ""

def generate_image(user_prompt, use_ai_prompt, ai_generated_prompt, selected_model, cfg, num_inference_steps, input_image=None):
    # If AI prompt is used, prefer that over user prompt
    if use_ai_prompt and user_prompt.strip() != "" and ai_generated_prompt.strip() != "":
        prompt = ai_generated_prompt
    else:
        prompt = user_prompt

    # If an image is provided, use img2img pipeline for image refinement
    if input_image is not None:
        # Resize the input image
        init_image = input_image.resize((768, 512))

        # Use img2img pipeline to refine the image based on the prompt
        pipe = StableDiffusionImg2ImgPipeline.from_pretrained("runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16)
        pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")

        refined_image = pipe(prompt=prompt, image=init_image, strength=0.75, guidance_scale=cfg).images[0]
        output_path = "output/refined_image.png"
        refined_image.save(output_path)

        return refined_image, prompt

    # If no image is provided, use the normal text-to-image generation
    if selected_model.startswith(sd1point5_base_model):
        model = selected_model
    else:
        model = hugging_face_user + "/" + selected_model
       
    if "lora" in selected_model:
        pipe = DiffusionPipeline.from_pretrained("stable-diffusion-v1-5/stable-diffusion-v1-5")
        pipe.load_lora_weights(model)
    else:
        pipe = DiffusionPipeline.from_pretrained(model)
    
    pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")

    image = pipe(prompt, num_inference_steps=num_inference_steps, cfg=cfg).images[0]
    output_path = "output/ai_generated_image.png"
    image.save(output_path)

    return image, prompt


# Gradio interface
models = getHuggingfaceModels()
logo_path = "Picture2.png"

# Custom CSS and theme
custom_css = """
    #component-0 {
        background-color: #003333 !important;
    }04d
    .logo {
        position: fixed;
        top: 10px;
        right: 10px;
        width: 50px;
        height: auto;
        z-index: 1000;
    }
"""

custom_theme = gr.themes.Default().set(
    body_background_fill="#003333",
    body_background_fill_dark="#003333",
    body_text_color="white",
    body_text_color_dark="white",
    block_background_fill="#005a5a",
    block_background_fill_dark="#005a5a",
    block_label_background_fill="#006666",
    block_label_background_fill_dark="#006666",
    input_background_fill="#003333",
    input_background_fill_dark="#003333",
    button_primary_background_fill="#008080",
    button_primary_background_fill_dark="#008080",
)

with gr.Blocks(theme=custom_theme, css=custom_css) as demo:
    gr.HTML(f"<img src='file={logo_path}' class='logo' alt='Logo'>")
    gr.Markdown("# DiffuseCraft - Refurbish Your Space with AI!")
    
    with gr.Row():
        with gr.Column():
            model_list = gr.Dropdown(models, value=ikea_models[0], label="Select Model", info="Choose the Image generation model you want to try!")
        with gr.Column():
            use_ai_prompt = gr.Checkbox(value=True, label="Use AI to generate detailed prompt", info="Check this box to generate a detailed prompt from AI based on your input")

    with gr.Row():
        with gr.Column():
            user_prompt = gr.Textbox(label="Enter your prompt", placeholder="Enter a room description or theme...")
            examples = gr.Examples(
                examples=["Modern living room with sofa and coffee table", "Cozy bedroom with ample of sunlight"],
                inputs=[user_prompt],
            )
        with gr.Column():
            image_input = gr.Image(label="Upload Image (Optional)", type="pil")  # Added image input
            ai_generated_prompt = gr.Textbox(label="AI generated detailed prompt", placeholder="AI generated prompt will appear here...", interactive=False)
        
    with gr.Row():
        with gr.Column():
            cfg = gr.Slider(1, 20, value=7.5, label="Guidance Scale", info="Choose between 1 and 20")
            num_inference_steps = gr.Slider(10, 100, value=20, label="Inference Steps", info="Choose between 10 and 100")

            generate_image_button = gr.Button(value="Generate Image")
        with gr.Column():    
            generated_image_output = gr.Image(label="Generated Image", width=512, height=512, type="pil")

    # with gr.Row():
    #     with gr.Column():
    #         refine_image = gr.Button(value="Refine Image")
    #     with gr.Column():
    #         refine_image_output = gr.Image(label="Refined Image", width=512, height=512)

    # Update submission logic to handle both image and prompt
    user_prompt.submit(fn=generate_ai_prompt, inputs=[user_prompt, use_ai_prompt], outputs=[ai_generated_prompt])
    generate_image_button.click(fn=generate_image, inputs=[user_prompt, use_ai_prompt, ai_generated_prompt, model_list, cfg, num_inference_steps, image_input], outputs=[generated_image_output, ai_generated_prompt])
    # refine_image.click(fn=generate_image, inputs=[user_prompt, use_ai_prompt, ai_generated_prompt, model_list, cfg, num_inference_steps, image_input], outputs=[refine_image_output])


if __name__ == "__main__":
    demo.launch()
