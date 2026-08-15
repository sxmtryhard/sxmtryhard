from PIL import Image, ImageFont, ImageDraw
import random
import os


# ============================================================
# CONFIGURACIÓN
# ============================================================

INPUT_IMAGE = "persona.png"
OUTPUT_GIF = "profile.gif"

WIDTH = 180

CHARS = " .,:;*+=?%#@"

FONT_SIZE = 6
CHAR_WIDTH = 3.6
LINE_HEIGHT = 6

FRAMES = 30
FRAME_DURATION = 80
FINAL_DURATION = 3000

PADDING = 40

random.seed(42)


# ============================================================
# FUENTE
# ============================================================

font_paths = [
    r"C:\Windows\Fonts\consola.ttf",
    r"C:\Windows\Fonts\cour.ttf",
    r"C:\Windows\Fonts\lucon.ttf",
]

font = None

for path in font_paths:
    if os.path.exists(path):
        font = ImageFont.truetype(path, FONT_SIZE)
        break

if font is None:
    print("⚠️ No se encontró una fuente monoespaciada.")
    font = ImageFont.load_default()


# ============================================================
# CARGAR IMAGEN
# ============================================================

print("📷 Cargando persona.png...")

image = Image.open(INPUT_IMAGE).convert("RGBA")


# ============================================================
# RECORTAR TRANSPARENCIA
# ============================================================

alpha = image.getchannel("A")
bbox = alpha.getbbox()

if bbox:
    image = image.crop(bbox)


# ============================================================
# MARGEN TRANSPARENTE
# ============================================================

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
# REDIMENSIONAR
# ============================================================

aspect_ratio = image.height / image.width

height = int(
    WIDTH *
    aspect_ratio *
    0.5
)

image = image.resize(
    (WIDTH, height),
    Image.Resampling.LANCZOS
)


# ============================================================
# CREAR CARACTERES
# ============================================================

print("🔤 Analizando píxeles...")

characters = []

for y in range(height):

    for x in range(WIDTH):

        r, g, b, alpha = image.getpixel((x, y))

        # Transparencia
        if alpha < 50:
            continue

        brightness = int(
            0.299 * r +
            0.587 * g +
            0.114 * b
        )

        index = int(
            (255 - brightness)
            / 255
            * (len(CHARS) - 1)
        )

        char = CHARS[index]

        if char == " ":
            continue

        characters.append(
            (x, y, char)
        )


# ============================================================
# ORDEN ALEATORIO
# ============================================================

print("🎲 Preparando animación...")

random.shuffle(characters)


# ============================================================
# DIMENSIONES
# ============================================================

gif_width = int(
    WIDTH *
    CHAR_WIDTH
)

gif_height = int(
    height *
    LINE_HEIGHT
)


# ============================================================
# CREAR FRAMES RGBA
# ============================================================

frames = []

total = len(characters)

print(
    f"🎞️ Generando {FRAMES} frames..."
)


for frame_number in range(FRAMES):

    progress = (
        frame_number + 1
    ) / FRAMES

    visible = int(
        total *
        progress
    )

    # IMPORTANTE:
    # Frame completamente transparente
    frame = Image.new(
        "RGBA",
        (
            gif_width,
            gif_height
        ),
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(frame)

    for i in range(visible):

        x, y, char = characters[i]

        draw.text(
            (
                int(x * CHAR_WIDTH),
                int(y * LINE_HEIGHT)
            ),
            char,
            font=font,
            fill=(255, 255, 255, 255)
        )

    frames.append(frame)

    print(
        f"   Frame {frame_number + 1}/{FRAMES}"
    )


# ============================================================
# FRAME FINAL
# ============================================================

final_frame = frames[-1].copy()

frames.append(final_frame)


# ============================================================
# CONVERTIR RGBA → GIF CON TRANSPARENCIA REAL
# ============================================================

print("🎨 Preparando transparencia del GIF...")


gif_frames = []


for frame in frames:

    # Crear una copia RGB
    rgb = Image.new(
        "RGB",
        frame.size,
        (0, 0, 0)
    )

    # Máscara alpha
    alpha = frame.getchannel("A")

    # Componer sobre negro temporalmente
    rgb.paste(
        frame,
        mask=alpha
    )

    # Convertir a paleta
    palette_frame = rgb.quantize(
        colors=255,
        method=Image.Quantize.MEDIANCUT
    )

    # Obtener píxeles alpha
    alpha_data = alpha.load()
    palette_data = palette_frame.load()

    # Crear color transparente
    transparent_index = 255

    # Cambiar todos los píxeles transparentes
    # al índice transparente
    for y in range(frame.height):

        for x in range(frame.width):

            if alpha_data[x, y] < 128:

                palette_data[x, y] = transparent_index

    # Crear paleta con 256 colores
    palette = palette_frame.getpalette()

    if palette is None:
        palette = []

    palette = list(palette)

    while len(palette) < 768:
        palette.append(0)

    # El índice 255 será transparente
    palette[transparent_index * 3] = 0
    palette[transparent_index * 3 + 1] = 0
    palette[transparent_index * 3 + 2] = 0

    palette_frame.putpalette(palette)

    palette_frame.info["transparency"] = transparent_index

    gif_frames.append(
        palette_frame
    )


# ============================================================
# DURACIONES
# ============================================================

durations = [
    FRAME_DURATION
] * (len(gif_frames) - 1)

durations.append(
    FINAL_DURATION
)


# ============================================================
# GUARDAR GIF
# ============================================================

print("💾 Guardando profile.gif...")


gif_frames[0].save(
    OUTPUT_GIF,
    save_all=True,
    append_images=gif_frames[1:],
    duration=durations,

    # SOLO UNA VEZ
    loop=1,

    transparency=255,

    disposal=2,

    optimize=False
)


# ============================================================
# FINAL
# ============================================================

print()
print("========================================")
print("       ✅ GIF CREADO CORRECTAMENTE")
print("========================================")
print(f"📁 Archivo: {OUTPUT_GIF}")
print(f"🎞️ Frames: {len(gif_frames)}")
print(f"📐 Tamaño: {gif_width} × {gif_height}")
print("🎨 Fondo: TRANSPARENTE")
print("🔁 Animación: UNA SOLA VEZ")
print("========================================")