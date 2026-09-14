# Sistema de referencia y despeje con visión estéreo

Repositorio base para la arquitectura de medición de despeje con:

- **2 cámaras USB** montadas en los extremos de un perfil **8080**
- **visión estéreo** como sensor principal
- **AprilTag** como referencia de campo de la **hinca**
- **Charuco** para calibración de cámaras
- **VL53L1X / ToF** solo como comprobación auxiliar puntual

> **LiDAR no forma parte de la arquitectura principal.**

## Arquitectura objetivo

Las dos cámaras se montan en los extremos del perfil 8080 y **apuntan verticalmente hacia el suelo**, paralelas a la referencia de la hinca.

```text
Vista frontal

   cámara USB ↓                           ↓ cámara USB
┌────────────────────────────────────────────────────────┐
│                 perfil 8080 horizontal                 │
└────────────────────────────────────────────────────────┘
                         ↓
                    terreno / proyección
                         ↓
                      AprilTag en hinca
```

## Geometría de diseño

La documentación y el dimensionado deben tomar como caso de diseño el escenario más exigente:

- **altura de hinca:** 0.80 m a 1.80 m
- **caso de diseño mínimo:** **0.80 m**
- **altura de montaje de cámaras (ejemplo):** **0.90 m** sobre el terreno
- **vuelo / overhang del módulo:** **~1.20 m**
- **posición segura / reposo:** **45° mínimo**

## Cobertura requerida

El sistema de cámaras debe cubrir simultáneamente:

1. la **proyección del módulo sobre el terreno**
2. el **área de terreno necesaria para calcular el despeje mínimo**

La solución principal es geométrica: reconstrucción estéreo del terreno + referencia absoluta del conjunto con AprilTag.

## Papel de cada tecnología

### Sensor principal
- **Visión estéreo con 2 cámaras USB**
  - reconstrucción 3D del terreno
  - cobertura de la zona bajo el módulo
  - cálculo del despeje mínimo

### Calibración
- **Charuco**
  - calibración intrínseca de cada cámara
  - calibración extrínseca entre cámaras
  - rectificación estéreo

### Referencia de campo
- **AprilTag**
  - referencia espacial de la hinca
  - alineación del sistema con la geometría real de trabajo

### Sensor opcional
- **VL53L1X / ToF**
  - uso opcional
  - solo como **medida puntual auxiliar** o contraste
  - **no** sustituye a la visión estéreo

### Fuera de arquitectura principal
- **LiDAR**
  - eliminado del diseño principal
  - no se usa como sensor base del sistema

## Estado actual del repositorio

El repositorio contiene utilidades base para la transición a la solución estéreo:

- `camera_calibration.py`: calibración de cámara con **Charuco**
- `apriltag_detector.py`: detección y pose de **AprilTag**
- `main.py`: utilidades CLI de calibración y captura de referencia
- `generate_templates.py`: generación de plantillas **Charuco** y apoyo para AprilTag

La integración completa de reconstrucción estéreo y cálculo de despeje se apoya en estos bloques.

## Instalación

```bash
git clone https://github.com/BrewGold/apriltag-distance-measurement.git
cd apriltag-distance-measurement
bash install.sh
```

`./install.sh` es la ruta soportada y recomendada para preparar el entorno del repositorio.

## Uso rápido

### 1. Generar patrón Charuco

```bash
python generate_templates.py
```

### 2. Calibrar una cámara

```bash
python main.py --mode calibrate
```

### 3. Verificar detección de AprilTag

```bash
python main.py --mode measure
```

### 4. Ver información de calibración

```bash
python main.py --mode info
```

## Notas de implementación

- La calibración de producción debe hacerse con **Charuco**.
- El **AprilTag** se usa como referencia de campo de la hinca.
- El sistema debe diseñarse con el caso límite de **hinca a 0.80 m**.
- La disposición mecánica debe asegurar que ambas cámaras miren **directamente hacia abajo**.
- Si se mantiene un **VL53L1X**, su papel es únicamente de verificación puntual.

## Estructura del proyecto

```text
apriltag-distance-measurement/
├── main.py
├── camera_calibration.py
├── apriltag_detector.py
├── system_config.py
├── generate_templates.py
├── install.sh
├── requirements.txt
└── README.md
```

## Licencia

MIT License
