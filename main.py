"""
Script principal para captura en tiempo real y mediciones con Raspberry Pi
Menú interactivo para calibración y mediciones
"""

import cv2
import numpy as np
import argparse
from pathlib import Path
from camera_calibration import CameraCalibration
from apriltag_detector import AprilTagMeasurement, MeasurementSession
import json

class MeasurementSystem:
    """Sistema completo de medición con AprilTags"""
    
    def __init__(self, calibration_file="camera_calibration.json", tag_size=0.1):
        self.calibration_file = calibration_file
        self.tag_size = tag_size
        self.camera_matrix = None
        self.distortion_coefficients = None
        self.measurement_session = None
        
        self.load_calibration()
    
    def load_calibration(self):
        """Carga calibración desde archivo"""
        try:
            with open(self.calibration_file, 'r') as f:
                data = json.load(f)
            self.camera_matrix = np.array(data['camera_matrix'])
            self.distortion_coefficients = np.array(data['distortion_coefficients'])
            print(f"✓ Calibración cargada desde: {self.calibration_file}")
            return True
        except FileNotFoundError:
            print(f"✗ Archivo de calibración no encontrado: {self.calibration_file}")
            return False
    
    def run_calibration(self):
        """Ejecuta proceso de calibración interactivo"""
        print("\n" + "="*60)
        print("CALIBRACIÓN DE CÁMARA")
        print("="*60)
        
        calibrator = CameraCalibration(
            checkerboard_size=(9, 6),
            square_size=0.025
        )
        
        print("\nPaso 1: Captura de imágenes de calibración")
        print("-" * 40)
        print("Necesitas un tablero de ajedrez (9x6)")
        print("Cada cuadrado debe medir 25mm")
        input("Presiona ENTER para comenzar la captura...")
        
        calibrator.capture_calibration_images(camera_id=0, num_images=20)
        
        print("\nPaso 2: Calibración")
        print("-" * 40)
        if calibrator.calibrate(image_shape=(480, 640)):
            calibrator.print_calibration_data()
            
            print("\nPaso 3: Guardar calibración")
            print("-" * 40)
            calibrator.save_calibration(self.calibration_file)
            
            self.camera_matrix = calibrator.get_camera_matrix()
            self.distortion_coefficients = calibrator.get_distortion_coefficients()
            print("✓ Calibración completada exitosamente")
            return True
        else:
            print("✗ Error en la calibración")
            return False
    
    def run_measurement(self, camera_id=0, save_video=False):
        """
        Ejecuta mediciones en tiempo real
        
        Args:
            camera_id: ID de la cámara
            save_video: Si guardar video de la sesión
        """
        if self.camera_matrix is None:
            print("✗ Error: Debe calibrar la cámara primero")
            return
        
        print("\n" + "="*60)
        print("MEDICIÓN EN TIEMPO REAL")
        print("="*60)
        print(f"Tag size: {self.tag_size*100:.1f} cm")
        print("Controles:")
        print("  SPACE: Guardar frame actual")
        print("  'R': Resetear mediciones")
        print("  'ESC': Salir")
        print("-" * 40 + "\n")
        
        # Crear sesión de medición
        self.measurement_session = MeasurementSession(
            self.camera_matrix,
            self.distortion_coefficients,
            self.tag_size
        )
        
        cap = cv2.VideoCapture(camera_id)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Configurar grabación de video si se solicita
        video_writer = None
        if save_video:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(
                'measurement_video.mp4',
                fourcc,
                30.0,
                (640, 480)
            )
        
        frame_count = 0
        saved_frames = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # Procesar frame
                measurements, analysis = self.measurement_session.process_frame(frame)
                
                # Dibujar mediciones
                display_frame = self.measurement_session.detector.draw_measurements(frame, measurements)
                
                # Agregar información de escena
                cv2.putText(display_frame,
                           f"Brillo: {analysis['brightness']:.0f} | Contraste: {analysis['contrast']:.0f}",
                           (10, display_frame.shape[0] - 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
                
                cv2.imshow("AprilTag Measurement System", display_frame)
                
                # Grabar video si está habilitado
                if video_writer:
                    video_writer.write(display_frame)
                
                # Procesar teclas
                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC
                    break
                elif key == 32:  # SPACE - Guardar frame
                    saved_frames += 1
                    self.measurement_session.detector.save_measurement(measurements)
                    print(f"Frame {frame_count} guardado")
                elif key == ord('r') or key == ord('R'):  # Reset
                    print("Reseteando mediciones...")
                    self.measurement_session = MeasurementSession(
                        self.camera_matrix,
                        self.distortion_coefficients,
                        self.tag_size
                    )
        
        finally:
            cap.release()
            if video_writer:
                video_writer.release()
            cv2.destroyAllWindows()
        
        # Generar reporte
        print(f"\nSesión finalizada")
        print(f"Frames procesados: {frame_count}")
        print(f"Frames guardados: {saved_frames}")
        
        self.measurement_session.generate_report()
    
    def show_calibration_info(self):
        """Muestra información de calibración actual"""
        if self.camera_matrix is None:
            print("✗ Sin calibración cargada")
            return
        
        try:
            with open(self.calibration_file, 'r') as f:
                data = json.load(f)
            
            print("\n" + "="*60)
            print("INFORMACIÓN DE CALIBRACIÓN")
            print("="*60)
            print(f"Archivo: {self.calibration_file}")
            print(f"Imágenes usadas: {data['num_images']}")
            print(f"Resolución: {data['image_shape']}")
            print(f"Error de reproyección: {data['reprojection_error']:.6f}")
            print("\nMatriz de Cámara:")
            print(np.array(data['camera_matrix']))
            print("\nCoeficientes de Distorsión:")
            print(np.array(data['distortion_coefficients']))
            print("="*60 + "\n")
        except Exception as e:
            print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Sistema de Medición con AprilTags para Raspberry Pi"
    )
    parser.add_argument(
        "--mode",
        choices=["calibrate", "measure", "info"],
        default="measure",
        help="Modo de operación"
    )
    parser.add_argument(
        "--calibration",
        default="camera_calibration.json",
        help="Archivo de calibración"
    )
    parser.add_argument(
        "--tag-size",
        type=float,
        default=0.1,
        help="Tamaño del AprilTag en metros (default: 0.1m = 10cm)"
    )
    parser.add_argument(
        "--camera",
        type=int,
        default=0,
        help="ID de la cámara (default: 0)"
    )
    parser.add_argument(
        "--save-video",
        action="store_true",
        help="Guardar video de la sesión"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("SISTEMA DE MEDICIÓN CON APRILTAGS")
    print("Precisión: 3mm | Rango: 50cm - 2m")
    print("="*60 + "\n")
    
    system = MeasurementSystem(
        calibration_file=args.calibration,
        tag_size=args.tag_size
    )
    
    if args.mode == "calibrate":
        system.run_calibration()
    elif args.mode == "measure":
        system.run_measurement(
            camera_id=args.camera,
            save_video=args.save_video
        )
    elif args.mode == "info":
        system.show_calibration_info()


if __name__ == "__main__":
    main()
