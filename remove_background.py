from rembg import remove

INPUT_IMAGE = "fotogithub2.png"
OUTPUT_IMAGE = "persona.png"

with open(INPUT_IMAGE, "rb") as input_file:
    input_data = input_file.read()

output_data = remove(input_data)

with open(OUTPUT_IMAGE, "wb") as output_file:
    output_file.write(output_data)

print("✅ Fondo eliminado correctamente.")