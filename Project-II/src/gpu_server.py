import base64
import io
import os
import sys
import time
from typing import Any, Dict, List, Optional

import cv2
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import get_preset, build_composite_prompt, NEGATIVE_PROMPT
from src.safety import check_prompt_safety

app = FastAPI(title="ControlNet Portrait Generation GPU Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline_instance = None
pipeline_device = "cpu"


class GenerationRequest(BaseModel):
    image_base64: str
    preset_ids: List[str]
    custom_prompt: Optional[str] = None
    num_steps: int = 25
    guidance_scale: float = 7.5


class VariationResponse(BaseModel):
    variation_id: str
    preset_id: str
    title: str
    platform: str
    formality: str
    image_base64: str
    prompt_used: str
    negative_prompt: str
    guidance_scale: float
    denoising_strength: float
    recommended_lighting: str
    recommended_background: str
    recommended_expression: str
    recommended_attire: str
    created_at: float


class GenerationResponse(BaseModel):
    success: bool
    variations: List[VariationResponse]
    device: str
    elapsed_seconds: float
    message: Optional[str] = None


def get_or_load_pipeline():
    global pipeline_instance, pipeline_device
    if pipeline_instance is not None:
        return pipeline_instance

    try:
        import torch
        from diffusers import StableDiffusionControlNetPipeline, ControlNetModel, UniPCMultistepScheduler

        if torch.cuda.is_available():
            pipeline_device = f"cuda:{torch.cuda.get_device_name(0)}"
            dtype = torch.float16
        else:
            pipeline_device = "cpu"
            dtype = torch.float32

        controlnet = ControlNetModel.from_pretrained(
            "lllyasviel/control_v11p_sd15_canny",
            torch_dtype=dtype,
        )
        pipe = StableDiffusionControlNetPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            controlnet=controlnet,
            torch_dtype=dtype,
            safety_checker=None,
        )
        pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
        if torch.cuda.is_available():
            pipe.enable_model_cpu_offload()

        pipeline_instance = pipe
        return pipeline_instance
    except Exception as exc:
        pipeline_device = f"error: {str(exc)}"
        return None


def decode_base64_to_image(b64_string: str) -> Image.Image:
    if "," in b64_string:
        b64_string = b64_string.split(",", 1)[1]
    image_data = base64.b64decode(b64_string)
    return Image.open(io.BytesIO(image_data)).convert("RGB")


def encode_image_to_base64(image: Image.Image) -> str:
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def extract_canny_edges(pil_image: Image.Image, low_threshold: int = 100, high_threshold: int = 200) -> Image.Image:
    image_np = np.array(pil_image.resize((512, 512)))
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(blurred, low_threshold, high_threshold)
    edges_3ch = np.stack([edges] * 3, axis=-1)
    return Image.fromarray(edges_3ch)


@app.get("/health")
def health_check():
    import torch
    cuda_available = torch.cuda.is_available()
    device_name = torch.cuda.get_device_name(0) if cuda_available else "CPU (No GPU)"
    return {
        "status": "online",
        "cuda_available": cuda_available,
        "device_name": device_name,
        "pipeline_loaded": (pipeline_instance is not None),
        "timestamp": time.time(),
    }


@app.post("/generate", response_model=GenerationResponse)
def generate_portraits(request: GenerationRequest):
    start_time = time.time()

    safety_result = check_prompt_safety(request.custom_prompt)
    if not safety_result.is_safe:
        raise HTTPException(
            status_code=400,
            detail=safety_result.warning_message or "Prompt violates safety guidelines.",
        )

    try:
        input_image = decode_base64_to_image(request.image_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 image data.")

    canny_image = extract_canny_edges(input_image)
    pipe = get_or_load_pipeline()
    variations: List[VariationResponse] = []

    for pid in request.preset_ids:
        preset = get_preset(pid)
        if not preset:
            continue

        full_prompt = build_composite_prompt(preset.id, request.custom_prompt)
        var_id = f"gpu_var_{preset.id}_{int(time.time() * 1000) % 100000}"

        if pipe is not None:
            try:
                generated_img = pipe(
                    prompt=full_prompt,
                    negative_prompt=NEGATIVE_PROMPT,
                    image=canny_image,
                    num_inference_steps=request.num_steps,
                    guidance_scale=request.guidance_scale or preset.guidance_scale,
                    controlnet_conditioning_scale=0.85,
                ).images[0]
            except Exception:
                generated_img = canny_image
        else:
            generated_img = canny_image

        b64_output = encode_image_to_base64(generated_img)
        variations.append(
            VariationResponse(
                variation_id=var_id,
                preset_id=preset.id,
                title=preset.title,
                platform=preset.platform.value,
                formality=preset.formality.value,
                image_base64=b64_output,
                prompt_used=full_prompt,
                negative_prompt=NEGATIVE_PROMPT,
                guidance_scale=preset.guidance_scale,
                denoising_strength=preset.denoising_strength,
                recommended_lighting=preset.recommended_lighting,
                recommended_background=preset.recommended_background,
                recommended_expression=preset.recommended_expression,
                recommended_attire=preset.recommended_attire,
                created_at=time.time(),
            )
        )

    elapsed = time.time() - start_time
    return GenerationResponse(
        success=True,
        variations=variations,
        device=pipeline_device,
        elapsed_seconds=round(elapsed, 2),
        message=f"Generated {len(variations)} variations on {pipeline_device}.",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
