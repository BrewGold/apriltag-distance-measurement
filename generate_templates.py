"""
Generador de plantilla de AprilTag para impresión
Crea una plantilla Charuco y deja indicaciones para AprilTag
"""

import subprocess
import sys
from pathlib import Path
from system_config import (
    DEFAULT_CHARUCO_BOARD_SIZE,
    DEFAULT_CHARUCO_MARKER_SIZE_M,
    DEFAULT_CHARUCO_SQUARE_SIZE_M,
)

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


def create_charuco_pattern():
    """Crea un patrón Charuco para calibración"""
    
    try:
        import cv2
    except ImportError:
        print("Instalando dependencias...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "opencv-contrib-python"])
        import cv2
    
    board_size = DEFAULT_CHARUCO_BOARD_SIZE
    square_size_px = 200
    image_size = (board_size[0] * square_size_px, board_size[1] * square_size_px)
    board_width_mm = board_size[0] * DEFAULT_CHARUCO_SQUARE_SIZE_M * 1000
    board_height_mm = board_size[1] * DEFAULT_CHARUCO_SQUARE_SIZE_M * 1000

    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    if hasattr(cv2.aruco, "CharucoBoard"):
        board = cv2.aruco.CharucoBoard(
            board_size,
            DEFAULT_CHARUCO_SQUARE_SIZE_M,
            DEFAULT_CHARUCO_MARKER_SIZE_M,
            dictionary
        )
    else:
        board = cv2.aruco.CharucoBoard_create(
            board_size[0],
            board_size[1],
            DEFAULT_CHARUCO_SQUARE_SIZE_M,
            DEFAULT_CHARUCO_MARKER_SIZE_M,
            dictionary
        )

    if hasattr(board, "generateImage"):
        img = board.generateImage(image_size)
    else:
        img = board.draw(image_size)

    output_path = Path(f"charuco_{board_size[0]}x{board_size[1]}.png")
    cv2.imwrite(str(output_path), img)
    print(f"✓ Tablero Charuco guardado en: {output_path}")
    print(f"  Tamaño: {image_size[0]}x{image_size[1]} píxeles")
    print(f"  Tamaño físico objetivo: {board_width_mm:.0f} mm x {board_height_mm:.0f} mm")
    print("  Imprime sin reescalado y verifica que el tamaño físico final coincida con esas medidas")


if __name__ == "__main__":
    print("Generador de Plantillas para AprilTag")
    print("="*40)
    
    create_charuco_pattern()
    print("\nPara generar AprilTags:")
    print("1. Descarga desde: https://github.com/AprilRobotics/apriltag-imgs")
    print("2. O usa: apt-get install apriltag")
