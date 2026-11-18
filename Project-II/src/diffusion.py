import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import cv2
import numpy as np
from PIL import Image

BASE_MODEL_ID = "stable-diffusion-v1-5/stable-diffusion-v1-5"
CONTROLNET_MODEL_ID = "lllyasviel/control_v11p_sd15_canny"
LORA_REPO_ID = "OedoSoldier/detail-tweaker-lora"
LORA_WEIGHT_NAME = "add_detail.safetensors"
LORA_ADAPTER_NAME = "detail_tweaker"
LORA_SCALE = 0.6

METHOD_CONTROLNET = "controlnet_img2img"
METHOD_BASIC = "img2img"
SUPPORTED_METHODS = (METHOD_CONTROLNET, METHOD_BASIC)

IMAGE_SIZE = 512
CONTROLNET_CONDITIONING_SCALE = 0.85
CANNY_LOW_THRESHOLD = 100
CANNY_HIGH_THRESHOLD = 200
MAX_ERROR_LENGTH = 300

DIFFUSION_QUALITY_SUFFIX = "professional headshot photo, sharp focus on face, realistic skin, 85mm lens"
DIFFUSION_NEGATIVE_PROMPT = (
    "deformed face, distorted eyes, extra fingers, blurry, low quality, cartoon, illustration, painting, "
    "watermark, text, nudity, oversaturated, plastic skin"
)
DEFAULT_DIFFUSION_PROMPT = "person in neat business attire, soft studio lighting, neutral background"
DIFFUSION_PROMPTS: Dict[str, str] = {
    "linkedin_black_tie": "person wearing a black tuxedo, white dress shirt, black bow tie, soft studio lighting, dark gray gradient backdrop",
    "linkedin_formal": "person wearing a navy blue business suit, white shirt, tie, diffused studio lighting, blurred modern corporate office background",
    "linkedin_business_casual": "person wearing a navy blazer over a light blue open collar shirt, no tie, soft window light, blurred coworking space background",
    "linkedin_smart_casual": "person wearing a neat crew neck sweater, warm ambient lighting, blurred light wood architectural background",
    "whatsapp_smart_casual": "person wearing a clean light polo shirt, bright daylight, plain light background, friendly smile, close-up",
    "whatsapp_business_casual": "person wearing a casual blazer over a plain t-shirt, soft office lighting, minimal neutral office background",
    "github_tech_casual": "person wearing a plain dark hoodie, dim lighting with cool blue accent light, blurred desk with computer monitors background",
    "content_creator": "person wearing a modern tailored jacket, dramatic cinematic rim lighting, dark textured studio backdrop",
}


def build_diffusion_prompt(preset_id: str, custom_prompt: Optional[str] = None) -> str:
    parts = []
    if custom_prompt and custom_prompt.strip():
        parts.append(custom_prompt.strip())
    parts.append(DIFFUSION_PROMPTS.get(preset_id, DEFAULT_DIFFUSION_PROMPT))
    parts.append(DIFFUSION_QUALITY_SUFFIX)
    return ", ".join(parts)


def _short_error(exc: Exception) -> str:
    return f"{type(exc).__name__}: {exc}"[:MAX_ERROR_LENGTH]


@dataclass
class DiffusionResult:
    image: Image.Image
    method: str
    strength: float
    guidance_scale: float
    num_steps: int
    seed: int
    lora_active: bool
    nsfw_flagged: bool
    elapsed_seconds: float


def prepare_init_image(pil_image: Image.Image) -> Image.Image:
    return pil_image.convert("RGB").resize((IMAGE_SIZE, IMAGE_SIZE), Image.Resampling.LANCZOS)


def extract_canny_edges(
    pil_image: Image.Image,
    low_threshold: int = CANNY_LOW_THRESHOLD,
    high_threshold: int = CANNY_HIGH_THRESHOLD,
) -> Image.Image:
    image_np = np.array(prepare_init_image(pil_image))
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(blurred, low_threshold, high_threshold)
    return Image.fromarray(np.stack([edges] * 3, axis=-1))


class DiffusionEngine:
    def __init__(self) -> None:
        self.controlnet_pipe: Any = None
        self.basic_pipe: Any = None
        self.device = "cpu"
        self.device_name = "CPU"
        self.lora_loaded = False
        self.lora_error = ""
        self.load_error = ""

    @property
    def is_loaded(self) -> bool:
        return self.controlnet_pipe is not None and self.basic_pipe is not None

    def load(self, use_lora: bool = True) -> bool:
        if self.is_loaded:
            return True

        try:
            import torch
            from diffusers import (
                ControlNetModel,
                StableDiffusionControlNetImg2ImgPipeline,
                StableDiffusionImg2ImgPipeline,
                UniPCMultistepScheduler,
            )

            if torch.cuda.is_available():
                self.device = "cuda"
                self.device_name = torch.cuda.get_device_name(0)
                dtype = torch.float16
            else:
                self.device = "cpu"
                self.device_name = "CPU"
                dtype = torch.float32

            controlnet = ControlNetModel.from_pretrained(CONTROLNET_MODEL_ID, torch_dtype=dtype)
            controlnet_pipe = StableDiffusionControlNetImg2ImgPipeline.from_pretrained(
                BASE_MODEL_ID,
                controlnet=controlnet,
                torch_dtype=dtype,
            )
            controlnet_pipe.scheduler = UniPCMultistepScheduler.from_config(controlnet_pipe.scheduler.config)
            controlnet_pipe = controlnet_pipe.to(self.device)
            controlnet_pipe.set_progress_bar_config(disable=True)

            basic_pipe = StableDiffusionImg2ImgPipeline(
                vae=controlnet_pipe.vae,
                text_encoder=controlnet_pipe.text_encoder,
                tokenizer=controlnet_pipe.tokenizer,
                unet=controlnet_pipe.unet,
                scheduler=UniPCMultistepScheduler.from_config(controlnet_pipe.scheduler.config),
                safety_checker=controlnet_pipe.safety_checker,
                feature_extractor=controlnet_pipe.feature_extractor,
            )
            basic_pipe.set_progress_bar_config(disable=True)

            self.controlnet_pipe = controlnet_pipe
            self.basic_pipe = basic_pipe
            self.load_error = ""
        except Exception as exc:
            self.controlnet_pipe = None
            self.basic_pipe = None
            self.load_error = _short_error(exc)
            return False

        if use_lora:
            self._load_lora()
        return True

    def _load_lora(self) -> None:
        try:
            self.controlnet_pipe.load_lora_weights(
                LORA_REPO_ID,
                weight_name=LORA_WEIGHT_NAME,
                adapter_name=LORA_ADAPTER_NAME,
            )
            self.controlnet_pipe.set_adapters([LORA_ADAPTER_NAME], adapter_weights=[LORA_SCALE])
            self.lora_loaded = True
            self.lora_error = ""
        except Exception as exc:
            self.lora_loaded = False
            self.lora_error = _short_error(exc)
            try:
                self.controlnet_pipe.unload_lora_weights()
            except Exception:
                pass

    def _set_lora_active(self, active: bool) -> bool:
        if not self.lora_loaded:
            return False
        if active:
            self.controlnet_pipe.enable_lora()
        else:
            self.controlnet_pipe.disable_lora()
        return active

    def describe(self) -> Dict[str, Any]:
        return {
            "pipeline_loaded": self.is_loaded,
            "load_error": self.load_error,
            "device": self.device,
            "device_name": self.device_name,
            "base_model": BASE_MODEL_ID,
            "controlnet_model": CONTROLNET_MODEL_ID,
            "lora_repo": LORA_REPO_ID,
            "lora_weight_name": LORA_WEIGHT_NAME,
            "lora_scale": LORA_SCALE,
            "lora_loaded": self.lora_loaded,
            "lora_error": self.lora_error,
            "methods": list(SUPPORTED_METHODS),
        }

    def generate(
        self,
        init_image: Image.Image,
        prompt: str,
        negative_prompt: str,
        method: str,
        strength: float,
        guidance_scale: float,
        num_steps: int,
        seed: int,
        use_lora: bool = True,
        control_image: Optional[Image.Image] = None,
    ) -> DiffusionResult:
        import torch

        if method not in SUPPORTED_METHODS:
            raise ValueError(f"Unsupported generation method: {method}")
        if not self.is_loaded:
            raise RuntimeError(self.load_error or "Diffusion pipelines are not loaded.")

        init = prepare_init_image(init_image)
        generator = torch.Generator(device="cpu").manual_seed(seed)
        lora_active = self._set_lora_active(use_lora)

        start_time = time.time()
        if method == METHOD_CONTROLNET:
            output = self.controlnet_pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                image=init,
                control_image=control_image or extract_canny_edges(init),
                strength=strength,
                guidance_scale=guidance_scale,
                num_inference_steps=num_steps,
                controlnet_conditioning_scale=CONTROLNET_CONDITIONING_SCALE,
                generator=generator,
            )
        else:
            output = self.basic_pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                image=init,
                strength=strength,
                guidance_scale=guidance_scale,
                num_inference_steps=num_steps,
                generator=generator,
            )
        elapsed = time.time() - start_time

        flags = getattr(output, "nsfw_content_detected", None) or [False]
        return DiffusionResult(
            image=output.images[0],
            method=method,
            strength=strength,
            guidance_scale=guidance_scale,
            num_steps=num_steps,
            seed=seed,
            lora_active=lora_active,
            nsfw_flagged=bool(flags[0]),
            elapsed_seconds=round(elapsed, 3),
        )
