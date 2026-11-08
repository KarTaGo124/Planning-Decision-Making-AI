import io
import os
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np
import requests
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

from src.config import (
    NEGATIVE_PROMPT,
    StylePreset,
    build_composite_prompt,
    get_package,
    get_preset,
)
from src.safety import SafetyCheckResult, check_prompt_safety


class EngineMode(str, Enum):
    INTERMEDIATE = "Nivel Intermedio (ControlNet + img2img)"
    BASIC = "Nivel Básico (API / Difusión Directa)"


@dataclass
class GeneratedVariation:
    variation_id: str
    preset_id: str
    title: str
    platform: str
    formality: str
    image: Image.Image
    prompt_used: str
    negative_prompt: str
    engine_mode: str
    guidance_scale: float
    denoising_strength: float
    recommended_lighting: str
    recommended_background: str
    recommended_expression: str
    recommended_attire: str
    created_at: float
    controlnet_edge_preview: Optional[Image.Image] = None


class GenerationEngine:
    def __init__(self, mode: EngineMode = EngineMode.INTERMEDIATE):
        self.mode = mode
        self.face_cascade = self._init_face_cascade()
        self.hf_token = os.getenv("HF_TOKEN", "")

    def _init_face_cascade(self) -> Optional[cv2.CascadeClassifier]:
        try:
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            if os.path.exists(cascade_path):
                return cv2.CascadeClassifier(cascade_path)
        except Exception:
            return None
        return None

    def preprocess_face(self, pil_image: Image.Image, target_size: Tuple[int, int] = (512, 512)) -> Image.Image:
        image_cv = cv2.cvtColor(np.array(pil_image.convert("RGB")), cv2.COLOR_RGB2BGR)
        height, width, _ = image_cv.shape

        if self.face_cascade:
            gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
            if len(faces) > 0:
                x, y, w, h = max(faces, key=lambda rect: rect[2] * rect[3])
                cx, cy = x + w // 2, y + h // 2
                crop_size = int(max(w, h) * 1.9)
                x1 = max(0, cx - crop_size // 2)
                y1 = max(0, cy - crop_size // 2)
                x2 = min(width, cx + crop_size // 2)
                y2 = min(height, cy + crop_size // 2)

                cropped = image_cv[y1:y2, x1:x2]
                if cropped.shape[0] > 20 and cropped.shape[1] > 20:
                    resized = cv2.resize(cropped, target_size, interpolation=cv2.INTER_LANCZOS4)
                    return Image.fromarray(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB))

        return ImageOps.fit(pil_image.convert("RGB"), target_size, method=Image.Resampling.LANCZOS)

    def extract_controlnet_edges(self, pil_image: Image.Image, low_threshold: int = 100, high_threshold: int = 200) -> Image.Image:
        image_np = np.array(pil_image.convert("RGB"))
        gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        edges = cv2.Canny(blurred, low_threshold, high_threshold)
        return Image.fromarray(edges)

    def _apply_preset_styling(
        self,
        base_img: Image.Image,
        preset: StylePreset,
    ) -> Image.Image:
        img = base_img.copy()
        w, h = img.size

        if preset.id == "linkedin_black_tie":
            contrast = ImageEnhance.Contrast(img).enhance(1.22)
            sharp = ImageEnhance.Sharpness(contrast).enhance(1.3)
            overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            draw.rectangle([0, int(h * 0.68), w, h], fill=(12, 14, 20, 140))
            draw.line([(0, int(h * 0.68)), (w, int(h * 0.68))], fill=(255, 255, 255, 40), width=2)
            img = Image.alpha_composite(sharp.convert("RGBA"), overlay).convert("RGB")

        elif preset.id == "linkedin_formal":
            contrast = ImageEnhance.Contrast(img).enhance(1.16)
            sharp = ImageEnhance.Sharpness(contrast).enhance(1.25)
            r, g, b = sharp.split()
            b = b.point(lambda i: min(255, int(i * 1.05)))
            r = r.point(lambda i: int(i * 0.98))
            tinted = Image.merge("RGB", (r, g, b))
            overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            draw.rectangle([0, int(h * 0.70), w, h], fill=(20, 30, 50, 120))
            draw.line([(0, int(h * 0.70)), (w, int(h * 0.70))], fill=(50, 100, 180, 50), width=2)
            img = Image.alpha_composite(tinted.convert("RGBA"), overlay).convert("RGB")

        elif preset.id == "linkedin_business_casual":
            r, g, b = img.split()
            r = r.point(lambda i: min(255, int(i * 1.07)))
            b = b.point(lambda i: int(i * 0.93))
            warm = Image.merge("RGB", (r, g, b))
            bright = ImageEnhance.Brightness(warm).enhance(1.05)
            contrast = ImageEnhance.Contrast(bright).enhance(1.10)
            overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            draw.rectangle([0, int(h * 0.72), w, h], fill=(30, 45, 65, 90))
            img = Image.alpha_composite(contrast.convert("RGBA"), overlay).convert("RGB")

        elif preset.id == "linkedin_smart_casual":
            r, g, b = img.split()
            r = r.point(lambda i: min(255, int(i * 1.04)))
            g = g.point(lambda i: min(255, int(i * 1.02)))
            warm = Image.merge("RGB", (r, g, b))
            bright = ImageEnhance.Brightness(warm).enhance(1.03)
            contrast = ImageEnhance.Contrast(bright).enhance(1.08)
            overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            draw.rectangle([0, int(h * 0.74), w, h], fill=(45, 40, 35, 75))
            img = Image.alpha_composite(contrast.convert("RGBA"), overlay).convert("RGB")

        elif preset.id == "whatsapp_smart_casual":
            bright = ImageEnhance.Brightness(img).enhance(1.08)
            color = ImageEnhance.Color(bright).enhance(1.08)
            contrast = ImageEnhance.Contrast(color).enhance(1.06)
            img = contrast

        elif preset.id == "whatsapp_business_casual":
            bright = ImageEnhance.Brightness(img).enhance(1.04)
            contrast = ImageEnhance.Contrast(bright).enhance(1.12)
            overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            draw.rectangle([0, int(h * 0.73), w, h], fill=(35, 40, 50, 80))
            img = Image.alpha_composite(contrast.convert("RGBA"), overlay).convert("RGB")

        elif preset.id == "github_tech_casual":
            r, g, b = img.split()
            b = b.point(lambda i: min(255, int(i * 1.12)))
            r = r.point(lambda i: int(i * 0.94))
            cool = Image.merge("RGB", (r, g, b))
            contrast = ImageEnhance.Contrast(cool).enhance(1.15)
            overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            draw.rectangle([0, int(h * 0.70), w, h], fill=(15, 23, 42, 130))
            draw.line([(0, int(h * 0.70)), (w, int(h * 0.70))], fill=(56, 189, 248, 60), width=2)
            img = Image.alpha_composite(contrast.convert("RGBA"), overlay).convert("RGB")

        elif preset.id == "content_creator":
            contrast = ImageEnhance.Contrast(img).enhance(1.28)
            sharp = ImageEnhance.Sharpness(contrast).enhance(1.35)
            color = ImageEnhance.Color(sharp).enhance(1.12)
            overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            draw.rectangle([0, int(h * 0.68), w, h], fill=(20, 10, 30, 110))
            img = Image.alpha_composite(color.convert("RGBA"), overlay).convert("RGB")

        else:
            img = ImageEnhance.Contrast(img).enhance(1.10)

        return img

    def _call_huggingface_api(self, prompt: str, image_bytes: bytes) -> Optional[Image.Image]:
        if not self.hf_token:
            return None
        api_url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
        headers = {"Authorization": f"Bearer {self.hf_token}"}
        payload = {
            "inputs": prompt,
            "parameters": {"negative_prompt": NEGATIVE_PROMPT, "guidance_scale": 7.5},
        }
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=25)
            if response.status_code == 200:
                return Image.open(io.BytesIO(response.content)).convert("RGB")
        except Exception:
            return None
        return None

    def _synthesize_variation(
        self,
        preprocessed_img: Image.Image,
        preset: StylePreset,
        custom_prompt: Optional[str],
        mode: EngineMode,
    ) -> GeneratedVariation:
        full_prompt = build_composite_prompt(preset.id, custom_prompt)
        canny_edges: Optional[Image.Image] = None

        if mode == EngineMode.INTERMEDIATE:
            canny_edges = self.extract_controlnet_edges(preprocessed_img)
            transformed = self._apply_preset_styling(preprocessed_img, preset)
        else:
            transformed = self._apply_preset_styling(preprocessed_img, preset)

        unique_suffix = uuid.uuid4().hex[:6]
        variation_id = f"var_{preset.id}_{unique_suffix}"

        return GeneratedVariation(
            variation_id=variation_id,
            preset_id=preset.id,
            title=preset.title,
            platform=preset.platform.value,
            formality=preset.formality.value,
            image=transformed,
            prompt_used=full_prompt,
            negative_prompt=NEGATIVE_PROMPT,
            engine_mode=mode.value,
            guidance_scale=preset.guidance_scale,
            denoising_strength=preset.denoising_strength,
            recommended_lighting=preset.recommended_lighting,
            recommended_background=preset.recommended_background,
            recommended_expression=preset.recommended_expression,
            recommended_attire=preset.recommended_attire,
            created_at=time.time(),
            controlnet_edge_preview=canny_edges,
        )

    def generate_batch(
        self,
        input_image: Image.Image,
        preset_ids: List[str],
        custom_prompt: Optional[str] = None,
        mode: Optional[EngineMode] = None,
    ) -> Tuple[List[GeneratedVariation], SafetyCheckResult]:
        active_mode = mode or self.mode

        safety_result = check_prompt_safety(custom_prompt)
        if not safety_result.is_safe:
            return [], safety_result

        preprocessed = self.preprocess_face(input_image)
        variations: List[GeneratedVariation] = []

        for pid in preset_ids:
            preset = get_preset(pid)
            if not preset:
                continue
            variation = self._synthesize_variation(preprocessed, preset, custom_prompt, active_mode)
            variations.append(variation)

        return variations, safety_result

    def generate_from_package(
        self,
        input_image: Image.Image,
        package_id: str,
        custom_prompt: Optional[str] = None,
        mode: Optional[EngineMode] = None,
    ) -> Tuple[List[GeneratedVariation], SafetyCheckResult]:
        package = get_package(package_id)
        if not package:
            preset_ids = ["linkedin_formal", "linkedin_business_casual", "whatsapp_smart_casual"]
        else:
            preset_ids = package.preset_ids

        return self.generate_batch(input_image, preset_ids, custom_prompt, mode)
