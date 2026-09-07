# Sistema de Medición de Distancias con AprilTags

Sistema completo para medir distancias entre una cámara Raspberry Pi y AprilTags con precisión de **3mm** en un rango de **50cm a 2 metros**.

## 📋 Características

- ✅ Detección de AprilTags en tiempo real
- ✅ Cálculo de distancias con precisión de 3mm
- ✅ Calibración automática de cámara
- ✅ Análisis de escena (brillo, contraste, posición)
- ✅ Guardado de mediciones en JSON
- ✅ Generación de reportes completos
- ✅ Interfaz CLI intuitiva
- ✅ Soporte para Raspberry Pi

## 🛠️ Requisitos

### Hardware
- **Cámara**: Raspberry Pi Camera V2 / CSI Camera / USB Webcam
- **Plataforma**: Raspberry Pi 4B o superior (o cualquier Linux/Windows/Mac)
- **RAM mínima**: 1GB
- **Tablero de ajedrez**: 9x6 esquinas con cuadrados de 25mm

### Software
- Python 3.7+
- OpenCV
- NumPy
- Pupil AprilTags

## 📦 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/BrewGold/apriltag-distance-measurement.git
cd apriltag-distance-measurement
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Verificar instalación

```bash
python main.py --mode info
```

## 🚀 Uso Rápido

### Paso 1: Calibración de Cámara (PRIMERA VEZ)

La calibración es **crítica** para obtener precisión de 3mm. Necesitas un tablero de ajedrez impreso (9x6 esquinas, cuadrados de 25mm).

```bash
python main.py --mode calibrate
```

**Instrucciones:**
1. Imprime el tablero de ajedrez
2. Pega sobre una superficie plana rígida
3. Ejecuta el comando
4. Captura 20 imágenes del tablero en diferentes ángulos
5. El sistema generará `camera_calibration.json`

### Paso 2: Mediciones en Tiempo Real

```bash
python main.py --mode measure
```

**Controles:**
- `ESPACIO`: Guardar frame actual con mediciones
- `R`: Resetear sesión de medición
- `ESC`: Salir

### Paso 3: Ver Información de Calibración

```bash
python main.py --mode info
```

## 📊 Archivos de Salida

### Mediciones (`measurements/`)
```json
{
  "timestamp": "2026-09-07T10:30:45.123456",
  "frame_number": 150,
  "measurements": [
    {
      "tag_id": 0,
      "distance_m": 0.75,
      "distance_cm": 75.23,
      "distance_mm": 752.3,
      "angles_deg": [2.1, 1.5, -0.3],
      "center": [320, 240],
      "pose_error": 0.002
    }
  ]
}
```

## 🔬 Parámetros de Precisión

| Parámetro | Valor |
|-----------|-------|
| Precisión requerida | ±3mm |
| Rango de medición | 50cm - 2m |
| Resolución cámara | 640x480 |
| FPS | 30 |

## 🎯 Opciones Avanzadas

### Cambiar tamaño del AprilTag

```bash
python main.py --mode measure --tag-size 0.15
```

### Usar cámara alternativa

```bash
python main.py --mode measure --camera 1
```

### Guardar video

```bash
python main.py --mode measure --save-video
```

## 🔧 API de Python

```python
from apriltag_detector import AprilTagMeasurement
import json
import numpy as np

# Cargar calibración
with open("camera_calibration.json") as f:
    cal = json.load(f)

camera_matrix = np.array(cal['camera_matrix'])
distortion = np.array(cal['distortion_coefficients'])

# Crear detector
detector = AprilTagMeasurement(camera_matrix, distortion, tag_size=0.1)

# Detectar
tags = detector.detect_tags(frame)
for tag in tags:
    measurement = detector.calculate_distance(tag)
    print(f"Distance: {measurement['distance_cm']:.2f}cm")
```

## 📖 Estructura del Proyecto

```
apriltag-distance-measurement/
├── main.py                    # Script principal
├── camera_calibration.py      # Módulo de calibración
├── apriltag_detector.py       # Módulo de detección
├── requirements.txt           # Dependencias
├── camera_calibration.json    # Calibración (generado)
├── measurements/              # Mediciones (creado)
└── README.md                  # Documentación
```

## 📝 Licencia

MIT License

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor abre un Issue o Pull Request.

---

**Versión**: 1.0.0  
**Última actualización**: 2026-09-07
