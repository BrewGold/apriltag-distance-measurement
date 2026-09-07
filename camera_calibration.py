"""
Calibración de cámara para mediciones precisas (3mm)
Generador de matriz intrínseca y distorsión
"""

import cv2
import numpy as np
import json
import os
from pathlib import Path

class CameraCalibration:
    """Calibración de cámara using checkerboard pattern"""
    
    def __init__(self, checkerboard_size=(9, 6), square_size=0.025):
        """
        Args:
            checkerboard_size: (width, height) número de esquinas internas
            square_size: tamaño del cuadrado en metros (0.025m = 25mm)
        """
        self.checkerboard_size = checkerboard_size
        self.square_size = square_size
        self.objpoints = []
        self.imgpoints = []
        self.calibration_data = {}
        
    def prepare_object_points(self):
        """Prepara puntos 3D reales del tablero de ajedrez"""
        objp = np.zeros((self.checkerboard_size[0] * self.checkerboard_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:self.checkerboard_size[0], 
                                0:self.checkerboard_size[1]].T.reshape(-1, 2)
        objp *= self.square_size
        return objp
    
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
        print(f"Capturando {num_images} imágenes de calibración...")
        print("Presiona 'SPACE' para capturar, 'ESC' para salir")
        
        while captured < num_images:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detectar esquinas del tablero de ajedrez
            ret_find, corners = cv2.findChessboardCorners(
                gray, 
                self.checkerboard_size, 
                None
            )
            
            display_frame = frame.copy()
            
            if ret_find:
                # Refinar esquinas
                criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
                refined_corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                
                # Dibujar esquinas
                cv2.drawChessboardCorners(display_frame, self.checkerboard_size, refined_corners, ret_find)
                cv2.putText(display_frame, f"Detected! Press SPACE to capture ({captured}/{num_images})", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                cv2.putText(display_frame, f"No checkerboard detected ({captured}/{num_images})", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            cv2.imshow("Calibration - Press SPACE to capture, ESC to exit", display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break
            elif key == 32 and ret_find:  # SPACE
                self.objpoints.append(self.prepare_object_points())
                self.imgpoints.append(refined_corners)
                
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
        if len(self.objpoints) == 0:
            print("Error: No hay imágenes de calibración capturadas")
            return False
        
        print(f"Calibrando con {len(self.objpoints)} imágenes...")
        
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
            self.objpoints,
            self.imgpoints,
            image_shape[::-1],  # OpenCV usa (width, height)
            None,
            None
        )
        
        if ret:
            self.calibration_data = {
                'camera_matrix': mtx.tolist(),
                'distortion_coefficients': dist.tolist(),
                'reprojection_error': float(ret),
                'image_shape': image_shape,
                'num_images': len(self.objpoints)
            }
            print(f"Calibración exitosa - Error de reproyección: {ret:.6f}")
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
    
    print("Sistema de Calibración de Cámara para AprilTag")
    print("Precisión requerida: 3mm\n")
    
    # Crear calibrador
    calibrator = CameraCalibration(
        checkerboard_size=(9, 6),  # 9x6 esquinas internas
        square_size=0.025  # Cuadrados de 25mm
    )
    
    # Capturar imágenes
    print("\n1. CAPTURA DE IMÁGENES DE CALIBRACIÓN")
    print("-" * 40)
    input("Prepara el tablero de ajedrez y presiona ENTER para comenzar...")
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
