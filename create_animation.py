from PIL import Image, ImageFont
import random
import os


# ============================================================
# CONFIGURACIÓN
# ============================================================

INPUT_IMAGE = "persona.png"
OUTPUT_GIF = "profile.gif"

# Resolución ASCII
WIDTH = 180

# Caracteres: claro → oscuro
CHARS = " .,:;*+=?%#@"

# Tamaño visual
FONT_SIZE = 6
CHAR_WIDTH = 3.6
LINE_HEIGHT = 6

# Animación
FRAMES = 30
FRAME_DURATION = 80       # milisegundos entre frames

# Tiempo que permanece la imagen final
FINAL_DURATION = 1800

# Fondo
BACKGROUND = (0, 0, 0)

# Semilla para que el patrón sea siempre igual
random.seed(42)


# ============================================================
# CARGAR FUENTE
# ============================================================

font_paths = [
    r"C:\Windows\Fonts\consola.ttf",
    r"C:\Windows\Fonts\cour.ttf",
    r"C:\Windows\Fonts\lucon.ttf",
]

font = None

for path in font_paths:

    if os.path.exists(path):

        font = ImageFont.truetype(
            path,
            FONT_SIZE
        )

        break


if font is None:

    print("⚠️ No se encontró una fuente monoespaciada.")
    print("Usando fuente predeterminada.")

    font = ImageFont.load_default()


# ============================================================
# CARGAR PERSONA
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
# AÑADIR MARGEN
# ============================================================

PADDING = 40

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
    WIDTH * aspect_ratio * 0.5
)

image = image.resize(
    (WIDTH, height),
    Image.Resampling.LANCZOS
)


# ============================================================
# PREPARAR CARACTERES
# ============================================================

print("🔤 Analizando píxeles...")

characters = []


for y in range(height):

    for x in range(WIDTH):

        r, g, b, alpha = image.getpixel(
            (x, y)
        )

        # Transparente → nada
        if alpha < 50:

            continue


        # Brillo
        brightness = int(
            0.299 * r +
            0.587 * g +
            0.114 * b
        )


        # Brillo → carácter
        index = int(
            (255 - brightness)
            / 255
            * (len(CHARS) - 1)
        )

        char = CHARS[index]


        if char == " ":

            continue


        characters.append(
            (
                x,
                y,
                char
            )
        )


# ============================================================
# ORDEN ALEATORIO DE APARICIÓN
# ============================================================

print("🎲 Preparando animación...")

random.shuffle(characters)


# ============================================================
# DIMENSIONES
# ============================================================

gif_width = int(
    WIDTH * CHAR_WIDTH
)

gif_height = int(
    height * LINE_HEIGHT
)


# ============================================================
# GENERAR FRAMES
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
        total * progress
    )


    # Crear frame negro
    frame = Image.new(
        "RGB",
        (
            gif_width,
            gif_height
        ),
        BACKGROUND
    )


    # Dibujar caracteres
    draw = Image.ImageDraw if False else None

    from PIL import ImageDraw

    draw = ImageDraw.Draw(frame)


    for i in range(visible):

        x, y, char = characters[i]


        draw.text(
            (
                x * CHAR_WIDTH,
                y * LINE_HEIGHT
            ),
            char,
            font=font,
            fill=(255, 255, 255)
        )


    frames.append(frame)


    print(
        f"   Frame {frame_number + 1}/{FRAMES}"
    )


# ============================================================
# AÑADIR FRAME FINAL
# ============================================================

final_frame = frames[-1].copy()

frames.append(final_frame)


# ============================================================
# GUARDAR GIF
# ============================================================

print("💾 Guardando profile.gif...")


durations = [
    FRAME_DURATION
] * (len(frames) - 1)

durations.append(
    FINAL_DURATION
)


frames[0].save(
    OUTPUT_GIF,
    save_all=True,
    append_images=frames[1:],
    duration=durations,
    loop=0,
    optimize=True
)


# ============================================================
# FINAL
# ============================================================

print()
print("========================================")
print("       ✅ GIF CREADO CORRECTAMENTE")
print("========================================")
print(f"📁 Archivo: {OUTPUT_GIF}")
print(f"🎞️ Frames: {len(frames)}")
print(f"📐 Tamaño: {gif_width} × {gif_height}")
print("🔁 Loop: infinito")
print("========================================")