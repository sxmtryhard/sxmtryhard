from PIL import Image
from html import escape


# ============================================================
# CONFIGURACIÓN
# ============================================================

INPUT_IMAGE = "persona.png"
OUTPUT_SVG = "profile.svg"

# Cantidad de caracteres horizontales
WIDTH = 180

# Caracteres utilizados para representar la imagen
# claro → oscuro
CHARS = " .,:;*+=?%#@"

# Tamaño de los caracteres
FONT_SIZE = 6

# Separación horizontal y vertical
CHAR_WIDTH = 3.6
LINE_HEIGHT = 6

# Colores
TEXT_COLOR = "#ffffff"
BACKGROUND_COLOR = "#000000"

# Margen alrededor de la persona
PADDING = 40


# ============================================================
# CARGAR IMAGEN
# ============================================================

print("📷 Cargando imagen...")

image = Image.open(INPUT_IMAGE).convert("RGBA")


# ============================================================
# RECORTAR TRANSPARENCIA
# ============================================================

print("✂️ Recortando espacio transparente...")

alpha = image.getchannel("A")

bbox = alpha.getbbox()

if bbox:
    image = image.crop(bbox)
else:
    print("⚠️ No se encontró transparencia.")


# ============================================================
# AÑADIR MARGEN
# ============================================================

print("📐 Añadiendo margen...")

new_width = image.width + PADDING * 2
new_height = image.height + PADDING * 2

canvas = Image.new(
    "RGBA",
    (new_width, new_height),
    (0, 0, 0, 0)
)

canvas.paste(
    image,
    (PADDING, PADDING),
    image
)

image = canvas


# ============================================================
# CALCULAR PROPORCIÓN
# ============================================================

aspect_ratio = image.height / image.width

height = int(
    WIDTH * aspect_ratio * 0.5
)


# ============================================================
# REDIMENSIONAR
# ============================================================

print("🔍 Redimensionando...")

image = image.resize(
    (WIDTH, height),
    Image.Resampling.LANCZOS
)


# ============================================================
# CREAR SVG
# ============================================================

svg_width = int(WIDTH * CHAR_WIDTH)
svg_height = int(height * LINE_HEIGHT)

svg = []

svg.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" '
    f'viewBox="0 0 {svg_width} {svg_height}" '
    f'width="{svg_width}" '
    f'height="{svg_height}">'
)


# ============================================================
# FONDO
# ============================================================

svg.append(
    f'<rect '
    f'width="100%" '
    f'height="100%" '
    f'fill="{BACKGROUND_COLOR}"/>'
)


# ============================================================
# GRUPO DE TEXTO
# ============================================================

svg.append(
    f'<g '
    f'fill="{TEXT_COLOR}" '
    f'font-family="monospace" '
    f'font-size="{FONT_SIZE}px" '
    f'text-anchor="start">'
)


# ============================================================
# CONVERTIR IMAGEN A ASCII
# ============================================================

print("🔤 Convirtiendo imagen a ASCII...")

for y in range(height):

    for x in range(WIDTH):

        r, g, b, alpha = image.getpixel((x, y))


        # ----------------------------------------------------
        # TRANSPARENCIA
        # ----------------------------------------------------

        if alpha < 50:
            continue


        # ----------------------------------------------------
        # CALCULAR BRILLO
        # ----------------------------------------------------

        brightness = int(
            0.299 * r +
            0.587 * g +
            0.114 * b
        )


        # ----------------------------------------------------
        # BRILLO → CARÁCTER
        # ----------------------------------------------------

        index = int(
            (255 - brightness)
            / 255
            * (len(CHARS) - 1)
        )

        char = CHARS[index]


        # No dibujar espacios
        if char == " ":
            continue


        # ----------------------------------------------------
        # AÑADIR CARÁCTER AL SVG
        # ----------------------------------------------------

        svg.append(
            f'<text '
            f'x="{x * CHAR_WIDTH:.2f}" '
            f'y="{(y + 1) * LINE_HEIGHT:.2f}">'
            f'{escape(char)}'
            f'</text>'
        )


# ============================================================
# FINALIZAR SVG
# ============================================================

svg.append("</g>")
svg.append("</svg>")


# ============================================================
# GUARDAR ARCHIVO
# ============================================================

print("💾 Guardando SVG...")

with open(
    OUTPUT_SVG,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "\n".join(svg)
    )


# ============================================================
# INFORMACIÓN FINAL
# ============================================================

print()
print("========================================")
print("       ✅ SVG GENERADO CORRECTAMENTE")
print("========================================")
print(f"📁 Archivo: {OUTPUT_SVG}")
print(f"📐 Ancho ASCII: {WIDTH} caracteres")
print(f"🔤 Caracteres utilizados: {len(CHARS)}")
print(f"📦 Tamaño SVG: {svg_width} × {svg_height}")
print("========================================")