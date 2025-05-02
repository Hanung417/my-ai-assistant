from fastapi import APIRouter
from pydantic import BaseModel
from diffusers import StableDiffusionPipeline
import torch
from PIL import Image
import base64
from io import BytesIO
import os

# ✅ CPU 멀티스레드 최적화 설정
torch.set_num_threads(10)
os.environ["OMP_NUM_THREADS"] = "10"

router = APIRouter()

model_id = "hakurei/waifu-diffusion"

pipe = StableDiffusionPipeline.from_pretrained(model_id, safety_checker=None)
pipe.to("cpu")

class ImageRequest(BaseModel):
    prompt: str

@router.post("/generate-character-image")
def generate_character_image(req: ImageRequest):
    try:
        image: Image.Image = pipe(
            req.prompt,
            height=768,  # 세로 해상도
            width=512,   # 가로 해상도
            num_inference_steps=20
        ).images[0]

        buffered = BytesIO()
        image.save(buffered, format="PNG")
        image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return {"image_base64": image_base64}
    except Exception as e:
        return {"error": str(e)}