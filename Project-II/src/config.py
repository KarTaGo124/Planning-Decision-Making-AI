from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class SocialPlatform(str, Enum):
    LINKEDIN = "LinkedIn"
    WHATSAPP = "WhatsApp"
    GITHUB = "GitHub / Portafolio"
    CREATIVE = "Redes & Contenido"


class FormalityLevel(str, Enum):
    BLACK_TIE = "Black Tie"
    FORMAL = "Formal"
    BUSINESS_CASUAL = "Business Casual"
    SMART_CASUAL = "Smart Casual"
    TECH_CASUAL = "Tech Casual"
    CREATIVE_STUDIO = "Creativo de Estudio"


@dataclass
class StylePreset:
    id: str
    platform: SocialPlatform
    formality: FormalityLevel
    title: str
    description: str
    default_prompt: str
    recommended_lighting: str
    recommended_background: str
    recommended_expression: str
    recommended_attire: str
    guidance_scale: float = 7.5
    denoising_strength: float = 0.45


@dataclass
class PresetPackage:
    id: str
    name: str
    description: str
    preset_ids: List[str]


STYLE_PRESETS: Dict[str, StylePreset] = {
    "linkedin_black_tie": StylePreset(
        id="linkedin_black_tie",
        platform=SocialPlatform.LINKEDIN,
        formality=FormalityLevel.BLACK_TIE,
        title="LinkedIn - Black Tie",
        description="Máxima elegancia ejecutiva con terno de gala o vestido formal oscuro.",
        default_prompt="fotografía de retrato profesional, terno negro de tres piezas de gala, camisa blanca impecable, corbata de seda negra o pajarita, postura erguida de liderazgo, iluminación suave de estudio, fondo neutro degradado elegante, alta resolución 8k",
        recommended_lighting="Iluminación suave de estudio con luz de relleno sutil",
        recommended_background="Fondo neutro gris carbón con viñeta sutil",
        recommended_expression="Mirada directa segura y expresión sobria de liderazgo",
        recommended_attire="Terno de gala negro o vestido ejecutivo de alta costura",
        guidance_scale=8.0,
        denoising_strength=0.40,
    ),
    "linkedin_formal": StylePreset(
        id="linkedin_formal",
        platform=SocialPlatform.LINKEDIN,
        formality=FormalityLevel.FORMAL,
        title="LinkedIn - Formal Clásico",
        description="Estilo corporativo tradicional con terno oscuro, camisa blanca y corbata clásica.",
        default_prompt="fotografía corporativa profesional, terno azul marino o carbón, camisa blanca abotonada, corbata elegante, postura profesional confiada, iluminación difusa de estudio fotográfico, fondo desenfocado de oficina corporativa moderna, nitidez facial alta",
        recommended_lighting="Luz frontal difusa de tres puntos",
        recommended_background="Oficina corporativa moderna con bokeh suave",
        recommended_expression="Sonrisa sutil y cálida transmitiendo confiabilidad",
        recommended_attire="Terno oscuro (azul marino o gris) y camisa blanca",
        guidance_scale=7.5,
        denoising_strength=0.42,
    ),
    "linkedin_business_casual": StylePreset(
        id="linkedin_business_casual",
        platform=SocialPlatform.LINKEDIN,
        formality=FormalityLevel.BUSINESS_CASUAL,
        title="LinkedIn - Business Casual",
        description="Blazer refinado sin corbata o blusa ejecutiva, equilibrando seriedad y cercanía.",
        default_prompt="retrato profesional contemporáneo, blazer azul marino sin corbata sobre camisa celeste de cuello abierto, postura relajada pero profesional, iluminación natural lateral suave de ventana, fondo de espacio de coworking elegante con profundidad de campo, enfoque nítido",
        recommended_lighting="Luz natural de ventana cálida y envolvente",
        recommended_background="Espacio de trabajo colaborativo o ventanal con luz diurna",
        recommended_expression="Expresión accesible con ligera sonrisa abierta",
        recommended_attire="Blazer moderno estructurado sobre camisa sin corbata",
        guidance_scale=7.5,
        denoising_strength=0.45,
    ),
    "linkedin_smart_casual": StylePreset(
        id="linkedin_smart_casual",
        platform=SocialPlatform.LINKEDIN,
        formality=FormalityLevel.SMART_CASUAL,
        title="LinkedIn - Smart Casual",
        description="Camisa o suéter pulcro con porte distinguido para sectores innovadores.",
        default_prompt="retrato profesional moderno de negocios, camisa de lino de cuello mao o suéter ligero de cuello redondo pulcro, postura cómoda y dinámica, iluminación cálida de estudio ambiental, fondo arquitectónico neutro desenfocado, textura de piel realista",
        recommended_lighting="Iluminación ambiental cálida con contraste moderado",
        recommended_background="Pared arquitectónica de concreto pulido o madera clara desenfocada",
        recommended_expression="Sonrisa genuina y expresión atenta",
        recommended_attire="Camisa sport elegante o suéter de punto fino pulcro",
        guidance_scale=7.0,
        denoising_strength=0.48,
    ),
    "whatsapp_smart_casual": StylePreset(
        id="whatsapp_smart_casual",
        platform=SocialPlatform.WHATSAPP,
        formality=FormalityLevel.SMART_CASUAL,
        title="WhatsApp - Smart Casual Cercano",
        description="Fotografía amigable y nítida para mensajería profesional y networking directo.",
        default_prompt="foto de perfil clara y accesible, polo camisero o blusa casual pulcra, iluminación diurna brillante y limpia, fondo luminoso neutro ligeramente desenfocado, encuadre cerrado centrado en rostro, expresión afable y profesional",
        recommended_lighting="Luz diurna frontal limpia y sin sombras duras",
        recommended_background="Fondo luminoso y limpio con colores claros",
        recommended_expression="Sonrisa amplia y cordial comunicando apertura",
        recommended_attire="Camisa sport clara o polo camisero presentable",
        guidance_scale=7.0,
        denoising_strength=0.45,
    ),
    "whatsapp_business_casual": StylePreset(
        id="whatsapp_business_casual",
        platform=SocialPlatform.WHATSAPP,
        formality=FormalityLevel.BUSINESS_CASUAL,
        title="WhatsApp - Business Casual",
        description="Presencia corporativa ágil para canales de mensajería empresarial y clientes.",
        default_prompt="foto de perfil ejecutiva para mensajería de negocios, blazer casual sobre camiseta lisa pulcra o blusa ejecutiva, iluminación suave de oficina moderna, fondo neutro con desenfoque suave, composición centrada de alta definición",
        recommended_lighting="Luz suave de oficina con balance de blancos neutro",
        recommended_background="Entorno de oficina neutro minimalista",
        recommended_expression="Mirada confiable y media sonrisa atenta",
        recommended_attire="Blazer liviano sobre prenda lisa básica",
        guidance_scale=7.2,
        denoising_strength=0.43,
    ),
    "github_tech_casual": StylePreset(
        id="github_tech_casual",
        platform=SocialPlatform.GITHUB,
        formality=FormalityLevel.TECH_CASUAL,
        title="GitHub - Tech Casual",
        description="Estilo contemporáneo para desarrolladores e ingenieros de software.",
        default_prompt="retrato profesional para perfil tecnológico de software engineering, hoodie limpio de diseño minimalista o camiseta técnica de alta calidad, iluminación tenue de estudio tecnológico con sutil luz de acento fría, fondo moderno con monitores o estación de trabajo difuminada, detalle nítido",
        recommended_lighting="Luz balanceada con un tenue toque de retroiluminación azul o neutra",
        recommended_background="Estación de desarrollo o setup tecnológico con bokeh profundo",
        recommended_expression="Expresión perspicaz, concentrada y amable",
        recommended_attire="Hoodie minimalista monocromático o camiseta ejecutiva tech",
        guidance_scale=7.5,
        denoising_strength=0.46,
    ),
    "content_creator": StylePreset(
        id="content_creator",
        platform=SocialPlatform.CREATIVE,
        formality=FormalityLevel.CREATIVE_STUDIO,
        title="Redes & Contenido - Creativo de Estudio",
        description="Retrato editorial con iluminación estilizada para perfiles de alto impacto visual.",
        default_prompt="retrato fotográfico editorial para creador de contenido y medios digitales, chaqueta de corte moderno o vestimenta estilizada contemporánea, iluminación dramática de estudio con luz de recorte cinematográfica, fondo con gradiente texturizado oscuro, detalle hiperrealista",
        recommended_lighting="Iluminación cinematográfica de recorte y contraste selectivo",
        recommended_background="Fondo de estudio texturizado con luz de recorte estilizada",
        recommended_expression="Mirada magnética y carismática",
        recommended_attire="Chaqueta moderna o atuendo creativo contemporáneo",
        guidance_scale=8.0,
        denoising_strength=0.50,
    ),
}


PRESET_PACKAGES: Dict[str, PresetPackage] = {
    "package_corporate_mix": PresetPackage(
        id="package_corporate_mix",
        name="Paquete Corporativo Multiplataforma (5 Variaciones)",
        description="Cubre los principales niveles formales para LinkedIn y mensajería profesional ejecutiva.",
        preset_ids=[
            "linkedin_formal",
            "linkedin_business_casual",
            "linkedin_smart_casual",
            "whatsapp_business_casual",
            "whatsapp_smart_casual",
        ],
    ),
    "package_tech_professional": PresetPackage(
        id="package_tech_professional",
        name="Paquete Tech & Networking (5 Variaciones)",
        description="Optimizado para ingenieros, desarrolladores y líderes de tecnología en LinkedIn, GitHub y mensajería.",
        preset_ids=[
            "github_tech_casual",
            "linkedin_business_casual",
            "linkedin_smart_casual",
            "whatsapp_smart_casual",
            "content_creator",
        ],
    ),
    "package_executive_full": PresetPackage(
        id="package_executive_full",
        name="Paquete Ejecutivo Integral (7 Variaciones)",
        description="Conjunto completo de alta formalidad que cubre desde Black Tie hasta Smart Casual y perfiles tech.",
        preset_ids=[
            "linkedin_black_tie",
            "linkedin_formal",
            "linkedin_business_casual",
            "linkedin_smart_casual",
            "whatsapp_business_casual",
            "whatsapp_smart_casual",
            "github_tech_casual",
        ],
    ),
}


NEGATIVE_PROMPT: str = (
    "desnudez, nsfw, sin ropa, ropa reveladora, deformidad facial, ojos asimétricos, "
    "artefactos digitales, baja resolución, sobreexposición, subexposición, rostro borroso, "
    "anatomía incorrecta, dedos adicionales, textura plástica artificial, marcas de agua, texto"
)


def get_preset(preset_id: str) -> Optional[StylePreset]:
    return STYLE_PRESETS.get(preset_id)


def get_all_presets() -> List[StylePreset]:
    return list(STYLE_PRESETS.values())


def get_package(package_id: str) -> Optional[PresetPackage]:
    return PRESET_PACKAGES.get(package_id)


def get_all_packages() -> List[PresetPackage]:
    return list(PRESET_PACKAGES.values())


def build_composite_prompt(preset_id: str, custom_prompt: Optional[str] = None) -> str:
    preset = get_preset(preset_id)
    if not preset:
        base_prompt = "retrato fotográfico profesional de negocios de alta calidad"
    else:
        base_prompt = preset.default_prompt

    if custom_prompt and custom_prompt.strip():
        sanitized_custom = custom_prompt.strip()
        return f"{base_prompt}, personalización solicitada: {sanitized_custom}"

    return base_prompt
