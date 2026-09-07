"""
Detector de AprilTags y cálculo de distancias
Especializado para mediciones de precisión (3mm)
"""

import cv2
import numpy as np
from pupil_apriltags import AprilTagDetector
import json
from datetime import datetime
from pathlib import Path

class AprilTagMeasurement:
    """
    Sistema de medición de distancias basado en AprilTags
    Rango: 50cm - 2m, Precisión: 3mm
    """
    
    def __init__(self, camera_matrix, distortion_coefficients, tag_size=0.1):
        """
        Args:
            camera_matrix: Matriz intrínseca de calibración (3x3)
            distortion_coefficients: Coeficientes de distorsión
            tag_size: Tamaño físico del AprilTag en metros (default 10cm)
        """
        self.camera_matrix = camera_matrix
        self.distortion_coefficients = distortion_coefficients
        self.tag_size = tag_size
        
        # Detector de AprilTags
        self.detector = AprilTagDetector(
            families='tag36h11',
            nthreads=4,
            quad_decimate=1.0,  # Sin decimación para máxima precisión
            quad_sigma=0.0,
            refine_edges=1,
            decode_sharpening=0.25,
            debug=False
        )
        
        self.measurements = []
        self.frame_count = 0
        
    def detect_tags(self, frame):
        """
        Detecta AprilTags en el frame
        
        Args:
            frame: Imagen BGR de OpenCV
            
        Returns:
            Lista de detecciones
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detections = self.detector.detect(gray)
        return detections
    
    def calculate_distance(self, tag_detection):
        """
        Calcula distancia del tag a la cámara usando solvePnP
        
        Args:
            tag_detection: Objeto de detección de AprilTag
            
        Returns:
            dict con distancia y pose
        """
        # Puntos 3D del tag (cuadrado centrado)
        half_size = self.tag_size / 2
        object_points = np.array([
            [-half_size, -half_size, 0],
            [half_size, -half_size, 0],
            [half_size, half_size, 0],
            [-half_size, half_size, 0]
        ], dtype=np.float32)
        
        # Puntos 2D detectados en la imagen
        image_points = tag_detection.corners.astype(np.float32)
        
        # Resolver PnP para obtener pose
        success, rvec, tvec = cv2.solvePnP(
            object_points,
            image_points,
            self.camera_matrix,
            self.distortion_coefficients,
            useExtrinsicGuess=False,
            flags=cv2.SOLVEPNP_ITERATIVE
        )
        
        if not success:
            return None
        
        # Calcular distancia Euclidiana
        distance = np.linalg.norm(tvec)
        
        # Convertir a metros
        distance_m = distance
        distance_cm = distance * 100
        distance_mm = distance * 1000
        
        # Ángulos de rotación (radianes a grados)
        angles = cv2.Rodrigues(rvec)[0]
        angles_deg = np.degrees(angles.flatten())
        
        result = {
            'tag_id': tag_detection.tag_id,
            'distance_m': distance_m,
            'distance_cm': distance_cm,
            'distance_mm': distance_mm,
            'tvec': tvec.flatten().tolist(),
            'rvec': rvec.flatten().tolist(),
            'angles_deg': angles_deg.tolist(),
            'corners': tag_detection.corners.tolist(),
            'center': tag_detection.center.tolist(),
            'pose_error': tag_detection.pose_error
        }
        
        return result
    
    def estimate_uncertainty(self, distance_m, tag_size_px):
        """
        Estima la incertidumbre de la medición
        Basada en tamaño del tag en píxeles y distancia
        
        Args:
            distance_m: Distancia en metros
            tag_size_px: Tamaño del tag detectado en píxeles
            
        Returns:
            Incertidumbre estimada en mm (±)
        """
        # Modelo empírico para error de medición
        # Error = k * distancia / (tamaño_en_pixeles)
        # Ajustado para precisión de 3mm
        k = 0.15  # Constante de calibración
        uncertainty_m = k * distance_m / tag_size_px
        uncertainty_mm = uncertainty_m * 1000
        
        return max(uncertainty_mm, 3.0)  # Mínimo 3mm de incertidumbre
    
    def draw_measurements(self, frame, measurements):
        """
        Dibuja información de mediciones en el frame
        
        Args:
            frame: Imagen para dibujar
            measurements: Lista de mediciones
            
        Returns:
            Frame modificado
        """
        display_frame = frame.copy()
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        for i, meas in enumerate(measurements):
            if meas is None:
                continue
            
            # Dibujar rectángulo alrededor del tag
            corners = np.array(meas['corners'], dtype=np.int32)
            cv2.polylines(display_frame, [corners], True, (0, 255, 0), 2)
            
            # Dibujar centro
            center = tuple(map(int, meas['center']))
            cv2.circle(display_frame, center, 5, (0, 0, 255), -1)
            
            # Información de distancia
            text_y = 30 + i * 80
            
            cv2.putText(display_frame, 
                       f"Tag ID: {meas['tag_id']}", 
                       (10, text_y), font, 0.6, (255, 255, 255), 2)
            
            cv2.putText(display_frame, 
                       f"Distancia: {meas['distance_cm']:.2f} cm ({meas['distance_mm']:.1f} mm)", 
                       (10, text_y + 25), font, 0.6, (0, 255, 0), 2)
            
            # Calcular incertidumbre
            tag_size_px = np.linalg.norm(corners[0] - corners[1])
            uncertainty = self.estimate_uncertainty(meas['distance_m'], tag_size_px)
            
            cv2.putText(display_frame, 
                       f"Incertidumbre: ±{uncertainty:.1f} mm", 
                       (10, text_y + 50), font, 0.5, (0, 165, 255), 1)
        
        # Información general
        cv2.putText(display_frame, 
                   f"Frame: {self.frame_count} | Tags detectados: {len(measurements)}", 
                   (10, display_frame.shape[0] - 20), font, 0.5, (255, 255, 255), 1)
        
        return display_frame
    
    def save_measurement(self, measurements, output_dir="measurements"):
        """
        Guarda mediciones en archivo JSON
        
        Args:
            measurements: Lista de mediciones
            output_dir: Directorio de salida
        """
        Path(output_dir).mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_dir}/measurement_{timestamp}.json"
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'frame_number': self.frame_count,
            'measurements': measurements,
            'tag_size_m': self.tag_size
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        
        return filename
    
    def analyze_scene(self, frame, measurements):
        """
        Analiza los alrededores y contexto de las mediciones
        
        Args:
            frame: Imagen actual
            measurements: Mediciones detectadas
            
        Returns:
            dict con análisis de escena
        """
        analysis = {
            'frame_shape': frame.shape,
            'brightness': float(cv2.mean(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))[0]),
            'contrast': float(np.std(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))),
            'num_tags': len([m for m in measurements if m is not None]),
            'tags_info': []
        }
        
        for meas in measurements:
            if meas is None:
                continue
            
            tag_info = {
                'id': meas['tag_id'],
                'distance_m': meas['distance_m'],
                'position_x': meas['center'][0],
                'position_y': meas['center'][1],
                'angles': meas['angles_deg']
            }
            analysis['tags_info'].append(tag_info)
        
        return analysis


class MeasurementSession:
    """Gestiona una sesión completa de mediciones"""
    
    def __init__(self, camera_matrix, distortion_coefficients, tag_size=0.1):
        self.detector = AprilTagMeasurement(camera_matrix, distortion_coefficients, tag_size)
        self.all_measurements = []
        self.scene_analysis = []
        self.start_time = datetime.now()
    
    def process_frame(self, frame):
        """Procesa un frame y guarda mediciones"""
        self.detector.frame_count += 1
        
        # Detectar tags
        detections = self.detector.detect_tags(frame)
        
        # Calcular distancias
        measurements = []
        for detection in detections:
            measurement = self.detector.calculate_distance(detection)
            measurements.append(measurement)
        
        # Analizar escena
        analysis = self.detector.analyze_scene(frame, measurements)
        
        self.all_measurements.append({
            'frame': self.detector.frame_count,
            'measurements': measurements,
            'timestamp': datetime.now().isoformat()
        })
        self.scene_analysis.append(analysis)
        
        return measurements, analysis
    
    def generate_report(self, output_file="measurement_report.json"):
        """Genera reporte de sesión completa"""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        report = {
            'session_info': {
                'start_time': self.start_time.isoformat(),
                'duration_seconds': duration,
                'total_frames': self.detector.frame_count,
                'total_measurements': sum(len(m['measurements']) for m in self.all_measurements)
            },
            'measurements': self.all_measurements,
            'scene_analysis': self.scene_analysis
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=4)
        
        print(f"\nReporte guardado en: {output_file}")
        return report


if __name__ == "__main__":
    print("AprilTag Distance Measurement System")
    print("Precisión: 3mm | Rango: 50cm - 2m")
