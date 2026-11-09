import base64
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
    REMOTE_GPU = "Servidor GPU Remoto (Google Colab / MV)"


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

    def _apply_portrait_depth_blur(self, pil_img: Image.Image) -> Image.Image:
        img_np = np.array(pil_img.convert("RGB"))
        h, w, _ = img_np.shape

        mask = np.zeros((h, w), dtype=np.uint8)
        cx, cy = w // 2, int(h * 0.42)
        rx, ry = int(w * 0.28), int(h * 0.28)
        cv2.ellipse(mask, (cx, cy), (rx, ry), 0, 0, 360, 255, -1)
        cv2.ellipse(mask, (cx, int(h * 0.88)), (int(w * 0.45), int(h * 0.32)), 0, 0, 360, 255, -1)

        mask_blurred = cv2.GaussianBlur(mask, (65, 65), 0).astype(np.float32) / 255.0
        mask_3ch = np.repeat(mask_blurred[:, :, np.newaxis], 3, axis=2)

        bg_blurred = cv2.GaussianBlur(img_np, (51, 51), 0)
        composite = (img_np * mask_3ch + bg_blurred * (1.0 - mask_3ch)).astype(np.uint8)
        return Image.fromarray(composite)

    def _apply_preset_styling(
        self,
        base_img: Image.Image,
        preset: StylePreset,
    ) -> Image.Image:
        depth_img = self._apply_portrait_depth_blur(base_img)
        img = depth_img.copy()
        w, h = img.size

        if preset.id == "linkedin_black_tie":
            contrast = ImageEnhance.Contrast(img).enhance(1.25)
            sharp = ImageEnhance.Sharpness(contrast).enhance(1.3)
            overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            draw.rectangle([0, int(h * 0.65), w, h], fill=(10, 12, 16, 175))
            draw.polygon([(int(w * 0.32), int(h * 0.65)), (int(w * 0.50), int(h * 0.85)), (int(w * 0.68), int(h * 0.65))], fill=(245, 245, 250, 190))
            draw.polygon([(int(w * 0.46), int(h * 0.66)), (int(w * 0.50), int(h * 0.84)), (int(w * 0.54), int(h * 0.66))], fill=(15, 15, 20, 230))
            draw.line([(0, int(h * 0.65)), (w, int(h * 0.65))], fill=(255, 255, 255, 60), width=2)
            img = Image.alpha_composite(sharp.convert("RGBA"), overlay).convert("RGB")

        elif preset.id == "linkedin_formal":
            contrast = ImageEnhance.Contrast(img).enhance(1.18)
            sharp = ImageEnhance.Sharpness(contrast).enhance(1.25)
            r, g, b = sharp.split()
            b = b.point(lambda i: min(255, int(i * 1.06)))
            r = r.point(lambda i: int(i * 0.97))
            tinted = Image.merge("RGB", (r, g, b))
            overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            draw.rectangle([0, int(h * 0.67), w, h], fill=(16, 26, 48, 160))
            draw.polygon([(int(w * 0.34), int(h * 0.67)), (int(w * 0.50), int(h * 0.84)), (int(w * 0.66), int(h * 0.67))], fill=(240, 245, 255, 185))
            draw.polygon([(int(w * 0.47), int(h * 0.68)), (int(w * 0.50), int(h * 0.83)), (int(w * 0.53), int(h * 0.68))], fill=(18, 55, 115, 220))
            draw.line([(0, int(h * 0.67)), (w, int(h * 0.67))], fill=(56, 189, 248, 70), width=2)
            img = Image.alpha_composite(tinted.convert("RGBA"), overlay).convert("RGB")

        elif preset.id == "linkedin_business_casual":
            r, g, b = img.split()
            r = r.point(lambda i: min(255, int(i * 1.07)))
            b = b.point(lambda i: int(i * 0.93))
            warm = Image.merge("RGB", (r, g, b))
            bright = ImageEnhance.Brightness(warm).enhance(1.05)
            contrast = ImageEnhance.Contrast(bright).enhance(1.12)
            overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            draw.rectangle([0, int(h * 0.69), w, h], fill=(28, 42, 60, 135))
            draw.polygon([(int(w * 0.36), int(h * 0.69)), (int(w * 0.50), int(h * 0.82)), (int(w * 0.64), int(h * 0.69))], fill=(225, 235, 250, 170))
            img = Image.alpha_composite(contrast.convert("RGBA"), overlay).convert("RGB")

        elif preset.id == "linkedin_smart_casual":
            r, g, b = img.split()
            r = r.point(lambda i: min(255, int(i * 1.05)))
            g = g.point(lambda i: min(255, int(i * 1.02)))
            warm = Image.merge("RGB", (r, g, b))
            bright = ImageEnhance.Brightness(warm).enhance(1.04)
            contrast = ImageEnhance.Contrast(bright).enhance(1.10)
            overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            draw.rectangle([0, int(h * 0.71), w, h], fill=(42, 38, 34, 115))
            img = Image.alpha_composite(contrast.convert("RGBA"), overlay).convert("RGB")

        elif preset.id == "whatsapp_smart_casual":
            bright = ImageEnhance.Brightness(img).enhance(1.08)
            color = ImageEnhance.Color(bright).enhance(1.10)
            contrast = ImageEnhance.Contrast(color).enhance(1.07)
            img = contrast

        elif preset.id == "whatsapp_business_casual":
            bright = ImageEnhance.Brightness(img).enhance(1.04)
            contrast = ImageEnhance.Contrast(bright).enhance(1.13)
            overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            draw.rectangle([0, int(h * 0.70), w, h], fill=(32, 38, 48, 120))
            img = Image.alpha_composite(contrast.convert("RGBA"), overlay).convert("RGB")

        elif preset.id == "github_tech_casual":
            r, g, b = img.split()
            b = b.point(lambda i: min(255, int(i * 1.14)))
            r = r.point(lambda i: int(i * 0.93))
            cool = Image.merge("RGB", (r, g, b))
            contrast = ImageEnhance.Contrast(cool).enhance(1.18)
            overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            draw.rectangle([0, int(h * 0.68), w, h], fill=(15, 23, 42, 160))
            draw.line([(0, int(h * 0.68)), (w, int(h * 0.68))], fill=(56, 189, 248, 85), width=2)
            img = Image.alpha_composite(contrast.convert("RGBA"), overlay).convert("RGB")

        elif preset.id == "content_creator":
            contrast = ImageEnhance.Contrast(img).enhance(1.30)
            sharp = ImageEnhance.Sharpness(contrast).enhance(1.35)
            color = ImageEnhance.Color(sharp).enhance(1.15)
            overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            draw.rectangle([0, int(h * 0.66), w, h], fill=(22, 12, 32, 145))
            img = Image.alpha_composite(color.convert("RGBA"), overlay).convert("RGB")

        else:
            img = ImageEnhance.Contrast(img).enhance(1.10)

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

    def generate_via_remote_gpu(
        self,
        input_image: Image.Image,
        preset_ids: List[str],
        backend_url: str,
        custom_prompt: Optional[str] = None,
        num_steps: int = 25,
        guidance_scale: float = 7.5,
    ) -> Tuple[List[GeneratedVariation], SafetyCheckResult]:
        safety_result = check_prompt_safety(custom_prompt)
        if not safety_result.is_safe:
            return [], safety_result

        preprocessed = self.preprocess_face(input_image)
        buffered = io.BytesIO()
        preprocessed.save(buffered, format="PNG")
        b64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

        clean_url = backend_url.rstrip("/")
        endpoint = f"{clean_url}/generate"
        payload = {
            "image_base64": b64_image,
            "preset_ids": preset_ids,
            "custom_prompt": custom_prompt,
            "num_steps": num_steps,
            "guidance_scale": guidance_scale,
        }

        try:
            response = requests.post(endpoint, json=payload, timeout=120)
            if response.status_code == 200:
                data = response.json()
                variations: List[GeneratedVariation] = []
                for var_data in data.get("variations", []):
                    img_b64 = var_data["image_base64"]
                    if "," in img_b64:
                        img_b64 = img_b64.split(",", 1)[1]
                    img_bytes = base64.b64decode(img_b64)
                    pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                    variations.append(
                        GeneratedVariation(
                            variation_id=var_data["variation_id"],
                            preset_id=var_data["preset_id"],
                            title=var_data["title"],
                            platform=var_data["platform"],
                            formality=var_data["formality"],
                            image=pil_img,
                            prompt_used=var_data["prompt_used"],
                            negative_prompt=var_data["negative_prompt"],
                            engine_mode="Nivel Intermedio (ControlNet GPU Remoto)",
                            guidance_scale=var_data["guidance_scale"],
                            denoising_strength=var_data["denoising_strength"],
                            recommended_lighting=var_data["recommended_lighting"],
                            recommended_background=var_data["recommended_background"],
                            recommended_expression=var_data["recommended_expression"],
                            recommended_attire=var_data["recommended_attire"],
                            created_at=var_data["created_at"],
                            controlnet_edge_preview=self.extract_controlnet_edges(preprocessed),
                        )
                    )
                return variations, safety_result
            else:
                return [], SafetyCheckResult(is_safe=False, warning_message=f"El servidor GPU respondió con código {response.status_code}.")
        except Exception as exc:
            return [], SafetyCheckResult(is_safe=False, warning_message=f"Error al conectar con servidor GPU ({str(exc)}).")

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
