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
    INTERMEDIATE = "Nivel Intermedio (ControlNet Canny + img2img, GPU)"
    BASIC = "Nivel Básico (Stable Diffusion img2img, GPU)"
    LOCAL = "Contingencia local (filtro OpenCV, sin modelo generativo)"


FACE_CASCADE_FILES = ("haarcascade_frontalface_alt2.xml", "haarcascade_frontalface_default.xml")
FACE_DETECTION_SIDE = 640
FACE_CROP_FACTOR = 1.9
FACE_VERTICAL_OFFSET = 0.15
HEAD_TOP_MARGIN = 0.25


REMOTE_METHOD_BY_MODE = {
    EngineMode.INTERMEDIATE: "controlnet_img2img",
    EngineMode.BASIC: "img2img",
}


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
    def __init__(self, mode: EngineMode = EngineMode.LOCAL):
        self.mode = mode
        self.face_cascades = self._init_face_cascades()
        self.last_face_box: Optional[Tuple[int, int, int, int]] = None
        self.hf_token = os.getenv("HF_TOKEN", "")

    def _init_face_cascades(self) -> List[cv2.CascadeClassifier]:
        cascades = []
        for name in FACE_CASCADE_FILES:
            try:
                path = cv2.data.haarcascades + name
                if os.path.exists(path):
                    cascade = cv2.CascadeClassifier(path)
                    if not cascade.empty():
                        cascades.append(cascade)
            except Exception:
                continue
        return cascades

    def detect_face(self, image_rgb: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
        scale = min(1.0, FACE_DETECTION_SIDE / max(gray.shape))
        if scale < 1.0:
            gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        gray = cv2.equalizeHist(gray)

        for cascade in self.face_cascades:
            faces = cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=5, minSize=(40, 40))
            if len(faces) > 0:
                x, y, w, h = max(faces, key=lambda rect: rect[2] * rect[3])
                return tuple(int(round(value / scale)) for value in (x, y, w, h))
        return None

    def preprocess_face(self, pil_image: Image.Image, target_size: Tuple[int, int] = (512, 512)) -> Image.Image:
        image_rgb = np.array(pil_image.convert("RGB"))
        height, width, _ = image_rgb.shape
        face = self.detect_face(image_rgb)
        self.last_face_box = face

        if face is None:
            return ImageOps.fit(pil_image.convert("RGB"), target_size, method=Image.Resampling.LANCZOS)

        x, y, w, h = face
        crop_size = min(int(max(w, h) * FACE_CROP_FACTOR), width, height)
        center_x = x + w // 2
        center_y = y + h // 2 + int(h * FACE_VERTICAL_OFFSET)

        x1 = center_x - crop_size // 2
        y1 = center_y - crop_size // 2
        y1 = min(y1, y - int(h * HEAD_TOP_MARGIN))
        x1 = min(max(0, x1), width - crop_size)
        y1 = min(max(0, y1), height - crop_size)

        cropped = image_rgb[y1:y1 + crop_size, x1:x1 + crop_size]
        interpolation = cv2.INTER_AREA if crop_size > target_size[0] else cv2.INTER_CUBIC
        resized = cv2.resize(cropped, target_size, interpolation=interpolation)
        return Image.fromarray(resized)

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
    ) -> GeneratedVariation:
        full_prompt = build_composite_prompt(preset.id, custom_prompt)
        canny_edges = self.extract_controlnet_edges(preprocessed_img)
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
            engine_mode=EngineMode.LOCAL.value,
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
    ) -> Tuple[List[GeneratedVariation], SafetyCheckResult]:
        safety_result = check_prompt_safety(custom_prompt)
        if not safety_result.is_safe:
            return [], safety_result

        preprocessed = self.preprocess_face(input_image)
        variations: List[GeneratedVariation] = []

        for pid in preset_ids:
            preset = get_preset(pid)
            if not preset:
                continue
            variation = self._synthesize_variation(preprocessed, preset, custom_prompt)
            variations.append(variation)

        return variations, safety_result

    def generate_via_remote_gpu(
        self,
        input_image: Image.Image,
        preset_ids: List[str],
        backend_url: str,
        custom_prompt: Optional[str] = None,
        mode: EngineMode = EngineMode.INTERMEDIATE,
        num_steps: int = 25,
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
            "method": REMOTE_METHOD_BY_MODE.get(mode, "controlnet_img2img"),
            "num_steps": num_steps,
        }

        try:
            try:
                response = requests.post(endpoint, json=payload, timeout=300)
            except requests.ConnectionError:
                time.sleep(2)
                response = requests.post(endpoint, json=payload, timeout=300)
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
                            engine_mode=mode.value,
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
                try:
                    detail = response.json().get("detail", "")
                except Exception:
                    detail = ""
                return [], SafetyCheckResult(
                    is_safe=False,
                    warning_message=f"El servidor GPU respondió con código {response.status_code}. {detail}".strip(),
                )
        except Exception as exc:
            return [], SafetyCheckResult(
                is_safe=False,
                warning_message=(
                    "No se pudo conectar con el servidor GPU. Verifique que la URL sea la que muestra "
                    f"la última celda del notebook y que esa celda siga en ejecución. Detalle: {type(exc).__name__}."
                ),
            )

    def generate_from_package(
        self,
        input_image: Image.Image,
        package_id: str,
        custom_prompt: Optional[str] = None,
    ) -> Tuple[List[GeneratedVariation], SafetyCheckResult]:
        package = get_package(package_id)
        if not package:
            preset_ids = ["linkedin_formal", "linkedin_business_casual", "whatsapp_smart_casual"]
        else:
            preset_ids = package.preset_ids

        return self.generate_batch(input_image, preset_ids, custom_prompt)
