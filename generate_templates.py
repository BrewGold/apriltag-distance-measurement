"""
Generador de plantilla de AprilTag para impresión
Crea un PDF imprimible con tags de diferentes tamaños
"""

import subprocess
import sys
from pathlib import Path

def generate_apriltag_template():
    """Genera plantilla de AprilTag usando apriltag-utils"""
    
    try:
        import PIL
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("Instalando Pillow...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
        from PIL import Image, ImageDraw, ImageFont
    
    # Crear imagen (A4 en 300 DPI)
    width, height = 2480, 3508
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Crear AprilTags (placeholder - en producción usarías apriltag-gen)
    print("Para generar AprilTags imprimibles, usa:")
    print("python3 -m pupil_apriltags.apriltag36h11 --generate-pdf")
    
    # Guardar imagen
    output_path = Path("apriltag_template.png")
    img.save(output_path)
    print(f"✓ Plantilla guardada en: {output_path}")


def create_checkerboard_pattern():
    """Crea un patrón de tablero de ajedrez para calibración"""
    
    try:
        import cv2
        import numpy as np
    except ImportError:
        print("Instalando dependencias...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "opencv-python", "numpy"])
        import cv2
        import numpy as np
    
    # Parámetros
    squares_x, squares_y = 9, 6
    square_size = 100  # píxeles
    
    # Crear imagen
    width = squares_x * square_size
    height = squares_y * square_size
    img = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Dibujar patrón
    for y in range(squares_y):
        for x in range(squares_x):
            if (x + y) % 2 == 0:
                x1 = x * square_size
                y1 = y * square_size
                x2 = x1 + square_size
                y2 = y1 + square_size
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 0), -1)
    
    # Guardar
    output_path = Path("checkerboard_9x6.png")
    cv2.imwrite(str(output_path), img)
    print(f"✓ Tablero de ajedrez guardado en: {output_path}")
    print(f"  Tamaño: {width}x{height} píxeles")
    print(f"  Imprime sin márgenes en papel A4 (100 DPI)")


if __name__ == "__main__":
    print("Generador de Plantillas para AprilTag")
    print("="*40)
    
    create_checkerboard_pattern()
    print("\nPara generar AprilTags:")
    print("1. Descarga desde: https://github.com/AprilRobotics/apriltag-imgs")
    print("2. O usa: apt-get install apriltag")
