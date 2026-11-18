import base64
import io
import os
import sys
import time
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import get_preset
from src.diffusion import (
    DIFFUSION_NEGATIVE_PROMPT,
    METHOD_CONTROLNET,
    SUPPORTED_METHODS,
    DiffusionEngine,
    build_diffusion_prompt,
)
from src.safety import check_prompt_safety

BASE_SEED = 1234

engine = DiffusionEngine()


@asynccontextmanager
async def lifespan(_: FastAPI):
    engine.load()
    yield


app = FastAPI(title="ControlNet Portrait Generation GPU Backend", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerationRequest(BaseModel):
    image_base64: str
    preset_ids: List[str]
    custom_prompt: Optional[str] = None
    method: str = METHOD_CONTROLNET
    num_steps: int = 25
    guidance_scale: Optional[float] = None
    strength: Optional[float] = None
    seed: Optional[int] = None
    use_lora: bool = True


class VariationResponse(BaseModel):
    variation_id: str
    preset_id: str
    title: str
    platform: str
    formality: str
    image_base64: str
    prompt_used: str
    negative_prompt: str
    method: str
    guidance_scale: float
    denoising_strength: float
    seed: int
    lora_active: bool
    nsfw_flagged: bool
    elapsed_seconds: float
    recommended_lighting: str
    recommended_background: str
    recommended_expression: str
    recommended_attire: str
    created_at: float


class GenerationResponse(BaseModel):
    success: bool
    variations: List[VariationResponse]
    device: str
    method: str
    elapsed_seconds: float
    message: Optional[str] = None


def decode_base64_to_image(b64_string: str) -> Image.Image:
    if "," in b64_string:
        b64_string = b64_string.split(",", 1)[1]
    image_data = base64.b64decode(b64_string)
    return Image.open(io.BytesIO(image_data)).convert("RGB")


def encode_image_to_base64(image: Image.Image) -> str:
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


@app.get("/health")
def health_check():
    status = engine.describe()
    status.update(
        {
            "status": "online",
            "cuda_available": engine.device == "cuda",
            "timestamp": time.time(),
        }
    )
    return status


@app.post("/generate", response_model=GenerationResponse)
def generate_portraits(request: GenerationRequest):
    start_time = time.time()

    safety_result = check_prompt_safety(request.custom_prompt)
    if not safety_result.is_safe:
        raise HTTPException(
            status_code=400,
            detail=safety_result.warning_message or "Prompt violates safety guidelines.",
        )

    if request.method not in SUPPORTED_METHODS:
        raise HTTPException(status_code=400, detail=f"Unsupported method. Use one of: {', '.join(SUPPORTED_METHODS)}.")

    try:
        input_image = decode_base64_to_image(request.image_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 image data.")

    if not engine.load():
        raise HTTPException(status_code=503, detail=f"Diffusion pipeline unavailable ({engine.load_error}).")

    variations: List[VariationResponse] = []

    for index, pid in enumerate(request.preset_ids):
        preset = get_preset(pid)
        if not preset:
            continue

        full_prompt = build_diffusion_prompt(preset.id, request.custom_prompt)
        seed = (request.seed if request.seed is not None else BASE_SEED) + index

        try:
            result = engine.generate(
                init_image=input_image,
                prompt=full_prompt,
                negative_prompt=DIFFUSION_NEGATIVE_PROMPT,
                method=request.method,
                strength=request.strength if request.strength is not None else preset.denoising_strength,
                guidance_scale=request.guidance_scale if request.guidance_scale is not None else preset.guidance_scale,
                num_steps=request.num_steps,
                seed=seed,
                use_lora=request.use_lora,
            )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Generation failed for preset '{preset.id}' ({type(exc).__name__}: {exc}).")

        variations.append(
            VariationResponse(
                variation_id=f"gpu_var_{preset.id}_{int(time.time() * 1000) % 100000}",
                preset_id=preset.id,
                title=preset.title,
                platform=preset.platform.value,
                formality=preset.formality.value,
                image_base64=encode_image_to_base64(result.image),
                prompt_used=full_prompt,
                negative_prompt=DIFFUSION_NEGATIVE_PROMPT,
                method=result.method,
                guidance_scale=result.guidance_scale,
                denoising_strength=result.strength,
                seed=result.seed,
                lora_active=result.lora_active,
                nsfw_flagged=result.nsfw_flagged,
                elapsed_seconds=result.elapsed_seconds,
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
        device=engine.device_name,
        method=request.method,
        elapsed_seconds=round(elapsed, 2),
        message=f"Generated {len(variations)} variations with {request.method} on {engine.device_name}.",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
