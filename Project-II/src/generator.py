import os
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

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

    def _apply_lighting_and_tone(
        self,
        base_img: Image.Image,
        lighting_style: str,
        denoising_strength: float,
    ) -> Image.Image:
        img = base_img.copy()

        if "estudio" in lighting_style.lower() or "cinematográfica" in lighting_style.lower():
            enhancer_contrast = ImageEnhance.Contrast(img)
            img = enhancer_contrast.enhance(1.15)
            enhancer_sharp = ImageEnhance.Sharpness(img)
            img = enhancer_sharp.enhance(1.2)
        elif "cálida" in lighting_style.lower() or "natural" in lighting_style.lower():
            r, g, b = img.split()
            r = r.point(lambda i: min(255, int(i * 1.06)))
            b = b.point(lambda i: int(i * 0.94))
            img = Image.merge("RGB", (r, g, b))
            enhancer_bright = ImageEnhance.Brightness(img)
            img = enhancer_bright.enhance(1.04)
        elif "balanceada" in lighting_style.lower() or "azul" in lighting_style.lower():
            r, g, b = img.split()
            b = b.point(lambda i: min(255, int(i * 1.08)))
            r = r.point(lambda i: int(i * 0.96))
            img = Image.merge("RGB", (r, g, b))
            enhancer_contrast = ImageEnhance.Contrast(img)
            img = enhancer_contrast.enhance(1.08)

        if denoising_strength > 0.45:
            enhancer_color = ImageEnhance.Color(img)
            img = enhancer_color.enhance(1.05)

        return img

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
            transformed = self._apply_lighting_and_tone(
                preprocessed_img,
                preset.recommended_lighting,
                preset.denoising_strength,
            )
        else:
            transformed = self._apply_lighting_and_tone(
                preprocessed_img,
                preset.recommended_lighting,
                0.35,
            )

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
