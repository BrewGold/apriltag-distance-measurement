"""
Calibración de cámara con Charuco para el sistema estéreo.
Generador de matriz intrínseca y distorsión.
"""

import cv2
import numpy as np
import json
from pathlib import Path
from system_config import (
    DEFAULT_CHARUCO_BOARD_SIZE,
    DEFAULT_CHARUCO_MARKER_SIZE_M,
    DEFAULT_CHARUCO_SQUARE_SIZE_M,
)

class CameraCalibration:
    """Calibración de cámara con tablero Charuco."""
    
    def __init__(
        self,
        board_size=DEFAULT_CHARUCO_BOARD_SIZE,
        square_size=DEFAULT_CHARUCO_SQUARE_SIZE_M,
        marker_size=DEFAULT_CHARUCO_MARKER_SIZE_M
    ):
        """
        Args:
            board_size: (width, height) número de cuadros del tablero Charuco
            square_size: tamaño del cuadrado en metros
            marker_size: tamaño del marcador ArUco en metros
        """
        self.board_size = board_size
        self.square_size = square_size
        self.marker_size = marker_size
        self.charuco_corners = []
        self.charuco_ids = []
        self.calibration_data = {}
        self.dictionary = self._get_aruco_dictionary()
        self.board = self._create_charuco_board()
        
    def _get_aruco_dictionary(self):
        """Obtiene el diccionario ArUco usado por Charuco."""
        return cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

    def _create_charuco_board(self):
        """Crea el tablero Charuco compatible con la versión de OpenCV."""
        if hasattr(cv2.aruco, "CharucoBoard"):
            return cv2.aruco.CharucoBoard(
                self.board_size,
                self.square_size,
                self.marker_size,
                self.dictionary
            )
        return cv2.aruco.CharucoBoard_create(
            self.board_size[0],
            self.board_size[1],
            self.square_size,
            self.marker_size,
            self.dictionary
        )

    def _calibrate_charuco(self, image_shape):
        """Ejecuta la calibración Charuco con compatibilidad entre versiones."""
        if hasattr(cv2.aruco, "calibrateCameraCharucoExtended"):
            calibration = cv2.aruco.calibrateCameraCharucoExtended(
                self.charuco_corners,
                self.charuco_ids,
                self.board,
                image_shape[::-1],
                None,
                None
            )
            return {
                'success': True,
                'reprojection_error': float(calibration[0]),
                'camera_matrix': calibration[1],
                'distortion_coefficients': calibration[2],
                'rvecs': calibration[3],
                'tvecs': calibration[4],
            }

        reprojection_error, mtx, dist, rvecs, tvecs = cv2.aruco.calibrateCameraCharuco(
            self.charuco_corners,
            self.charuco_ids,
            self.board,
            image_shape[::-1],
            None,
            None
        )
        return {
            'success': mtx is not None and dist is not None,
            'reprojection_error': float(reprojection_error),
            'camera_matrix': mtx,
            'distortion_coefficients': dist,
            'rvecs': rvecs,
            'tvecs': tvecs,
        }

    def capture_calibration_images(self, camera_id=0, num_images=20):
        """
        Captura imágenes para calibración
        
        Args:
            camera_id: ID de la cámara (0 para la principal)
            num_images: Número de imágenes a capturar
        """
        cap = cv2.VideoCapture(camera_id)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        calibration_dir = Path("calibration_images")
        calibration_dir.mkdir(exist_ok=True)
        
        captured = 0
        print(f"Capturando {num_images} imágenes de calibración Charuco...")
        print("Presiona 'SPACE' para capturar, 'ESC' para salir")
        
        while captured < num_images:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            marker_corners, marker_ids, _ = cv2.aruco.detectMarkers(gray, self.dictionary)
            
            display_frame = frame.copy()
            
            charuco_detected = False
            charuco_corners = None
            charuco_ids = None

            if marker_ids is not None and len(marker_ids) > 0:
                cv2.aruco.drawDetectedMarkers(display_frame, marker_corners, marker_ids)
                response, charuco_corners, charuco_ids = cv2.aruco.interpolateCornersCharuco(
                    marker_corners,
                    marker_ids,
                    gray,
                    self.board
                )

                if response is not None and response >= 4:
                    charuco_detected = True
                    cv2.aruco.drawDetectedCornersCharuco(
                        display_frame,
                        charuco_corners,
                        charuco_ids
                    )
                    cv2.putText(display_frame, f"Charuco detectado. SPACE para capturar ({captured}/{num_images})",
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                else:
                    cv2.putText(display_frame,
                               f"Marcadores detectados, faltan esquinas Charuco ({captured}/{num_images})",
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 2)
            else:
                cv2.putText(display_frame, f"No se detecta tablero Charuco ({captured}/{num_images})",
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            cv2.imshow("Calibration - Press SPACE to capture, ESC to exit", display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break
            elif key == 32 and charuco_detected:  # SPACE
                self.charuco_corners.append(charuco_corners)
                self.charuco_ids.append(charuco_ids)
                
                # Guardar imagen
                img_path = calibration_dir / f"calibration_{captured:02d}.jpg"
                cv2.imwrite(str(img_path), frame)
                captured += 1
                print(f"Imagen {captured} capturada: {img_path}")
        
        cap.release()
        cv2.destroyAllWindows()
        print(f"Capturación completada: {captured} imágenes")
        
    def calibrate(self, image_shape=(480, 640)):
        """
        Realiza la calibración con las imágenes capturadas
        
        Args:
            image_shape: (height, width) de las imágenes capturadas
        """
        if len(self.charuco_corners) == 0:
            print("Error: No hay imágenes de calibración capturadas")
            return False
        
        print(f"Calibrando con {len(self.charuco_corners)} imágenes Charuco...")

        try:
            calibration = self._calibrate_charuco(image_shape)
        except cv2.error as error:
            print(f"Error en la calibración Charuco: {error}")
            return False
        
        if calibration['success'] and calibration['camera_matrix'] is not None and calibration['distortion_coefficients'] is not None:
            self.calibration_data = {
                'pattern': 'charuco',
                'board_size': self.board_size,
                'square_size': self.square_size,
                'marker_size': self.marker_size,
                'camera_matrix': calibration['camera_matrix'].tolist(),
                'distortion_coefficients': calibration['distortion_coefficients'].tolist(),
                'reprojection_error': calibration['reprojection_error'],
                'image_shape': image_shape,
                'num_images': len(self.charuco_corners)
            }
            print(f"Calibración exitosa - Error de reproyección: {calibration['reprojection_error']:.6f}")
            return True
        else:
            print("Error en la calibración")
            return False
    
    def save_calibration(self, filename="camera_calibration.json"):
        """Guarda los datos de calibración en JSON"""
        if not self.calibration_data:
            print("Error: No hay datos de calibración para guardar")
            return False
        
        with open(filename, 'w') as f:
            json.dump(self.calibration_data, f, indent=4)
        print(f"Calibración guardada en: {filename}")
        return True
    
    def load_calibration(self, filename="camera_calibration.json"):
        """Carga datos de calibración desde JSON"""
        try:
            with open(filename, 'r') as f:
                self.calibration_data = json.load(f)
            print(f"Calibración cargada desde: {filename}")
            return True
        except FileNotFoundError:
            print(f"Archivo no encontrado: {filename}")
            return False
    
    def get_camera_matrix(self):
        """Retorna matriz intrínseca"""
        if not self.calibration_data:
            return None
        return np.array(self.calibration_data['camera_matrix'])
    
    def get_distortion_coefficients(self):
        """Retorna coeficientes de distorsión"""
        if not self.calibration_data:
            return None
        return np.array(self.calibration_data['distortion_coefficients'])
    
    def print_calibration_data(self):
        """Imprime datos de calibración en formato legible"""
        if not self.calibration_data:
            print("No hay datos de calibración cargados")
            return
        
        print("\n" + "="*60)
        print("DATOS DE CALIBRACIÓN DE CÁMARA")
        print("="*60)
        print(f"Patrón: {self.calibration_data.get('pattern', 'charuco')}")
        print(f"Tablero: {self.calibration_data.get('board_size', self.board_size)}")
        print(f"Número de imágenes: {self.calibration_data['num_images']}")
        print(f"Resolución: {self.calibration_data['image_shape']}")
        print(f"Error de reproyección: {self.calibration_data['reprojection_error']:.6f}")
        print("\nMatriz de Cámara (Matriz Intrínseca):")
        print(np.array(self.calibration_data['camera_matrix']))
        print("\nCoeficientes de Distorsión:")
        print(np.array(self.calibration_data['distortion_coefficients']))
        print("="*60 + "\n")


if __name__ == "__main__":
    import sys
    
    print("Sistema de Calibración de Cámara con Charuco")
    print("Uso previsto: calibración del sistema estéreo\n")
    
    # Crear calibrador
    calibrator = CameraCalibration(
        board_size=DEFAULT_CHARUCO_BOARD_SIZE,
        square_size=DEFAULT_CHARUCO_SQUARE_SIZE_M,
        marker_size=DEFAULT_CHARUCO_MARKER_SIZE_M
    )
    
    # Capturar imágenes
    print("\n1. CAPTURA DE IMÁGENES DE CALIBRACIÓN")
    print("-" * 40)
    input("Prepara el tablero Charuco y presiona ENTER para comenzar...")
    calibrator.capture_calibration_images(camera_id=0, num_images=20)
    
    # Realizar calibración
    print("\n2. CALIBRACIÓN")
    print("-" * 40)
    if calibrator.calibrate(image_shape=(480, 640)):
        calibrator.print_calibration_data()
        
        # Guardar calibración
        print("\n3. GUARDAR CALIBRACIÓN")
        print("-" * 40)
        calibrator.save_calibration("camera_calibration.json")
        print("✓ Calibración completada y guardada")
    else:
        print("✗ Fallo en la calibración")
        sys.exit(1)
