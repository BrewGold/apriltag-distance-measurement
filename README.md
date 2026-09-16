# Prototipo portátil para medición de hincas y validación de despeje

Este repositorio documenta y soporta el prototipo integrado para seguidores solares que debe:

- medir la altura real de la hinca,
- generar un modelo local del terreno alrededor de la hinca,
- calcular el despeje mínimo módulo-suelo,
- decidir automáticamente **✅ APTO** o **❌ NO APTO** con despeje mínimo configurable (**300 mm** o **400 mm**).

## Alcance de este repositorio (implementación actual)

Este repositorio **no implementa todavía el sistema integrado completo** en Uno Q.  
El código actual en Python aporta módulos de soporte para:

- calibración de cámara,
- detección de AprilTag 36h11,
- estimación de pose/distancia del tag de referencia.

## Arquitectura final validada del prototipo (nivel sistema)

### Procesador principal
- **Arduino Uno Q**
- Responsable de control de cámaras, IMU, RTK3B Compass, servo PWM, procesamiento simplificado y decisión APTO/NO APTO.

### Cámaras estéreo
- **2 × Arducam IMX298**
- 16 MP, **4656 × 3496**
- HFOV aproximado: **105°**
- Baseline estéreo: **350 mm**
- Esta configuración corresponde al prototipo integrado objetivo; no al flujo mono-cámara actual de `main.py`.

### Referencia geométrica
- Angular magnético desmontable (aluminio + imanes + **AprilTag 36h11**)
- Tamaño de tag: **150 × 150 mm**
- Uso temporal en base de cada hinca para:
  - referencia absoluta,
  - origen de coordenadas,
  - corrección geométrica,
  - validación angular.

### Sensores auxiliares
- **IMU**: roll y pitch reales del equipo.
- **RTK3B Compass**: pitch, heading, referencia absoluta y corrección de vertical real.
- **VL53L1X / ToF (opcional)**: solo verificación puntual auxiliar de distancia/altura, **no** parte de la arquitectura principal.

### Base giratoria
- **ServoCity Servo Driven Base Pan Kit** por PWM RC desde Uno Q.
- La base no define ángulos precisos; los ángulos reales se estiman con AprilTag + IMU + RTK3B.

## Flujo de captura y procesamiento objetivo (prototipo integrado)

### Captura
- Tres posiciones: **-15°**, **0°**, **+15°**
- En cada posición: 1 par estéreo
- Total: **3 pares / 6 fotos**

### Resolución
- Captura nativa: **4656 × 3496**
- Procesamiento estéreo inicial: **50%** (**2328 × 1748**) para reducir carga

### Modelo de terreno
- No se almacena nube de puntos completa
- Conversión directa a malla topográfica de **5 cm × 5 cm**
- Cada celda guarda: **Zmin, Zmax, Zmean, confidence**

### Sistema de coordenadas
- Origen: base de hinca (AprilTag)
- Ejes:
  - **X** longitudinal seguidor
  - **Y** transversal
  - **Z** altura

### Fusión entre hincas
- Se genera un tile por hinca (A, B, C, ...)
- Alineación mediante AprilTag + RTK + geometría conocida
- Zonas negras pequeñas entre hincas: medida real + interpolación con nivel de confianza

## Salida esperada del sistema integrado

- Altura de hinca, por ejemplo: `1842 mm`
- Despeje mínimo, por ejemplo: `347 mm`
- Punto crítico, por ejemplo: `X = 5.42 m`, `Y = -0.67 m`
- Resultado final: `✅ APTO` o `❌ NO APTO`

## Precisión objetivo y ventana operativa

- Altura de hinca:
  - objetivo: **±5 mm**
  - esperado en buenas condiciones: **±3 a ±5 mm**
  - esperado en condiciones difíciles: **±5 a ±10 mm**
- Modelo de terreno en campo: **±5 a ±10 mm**
- Tiempo operativo por hinca: **15 a 20 s**

## Estado del prototipo (arquitectura validada)

Componentes validados y alineados en este repositorio:

- Uno Q
- 2 cámaras IMX298
- Baseline 350 mm
- AprilTag 150×150 mm en referencia magnética
- IMU integrada
- RTK3B Compass
- Base giratoria PWM
- Capturas a -15°, 0°, +15°
- Malla topográfica 5×5 cm
- Fusión entre hincas
- Resultado APTO / NO APTO

## Uso disponible hoy en este repositorio (scripts Python)

```bash
python main.py --mode calibrate
python main.py --mode measure --tag-size 0.15
python main.py --mode info
```

### Ejemplo API (tag de 150 mm)

```python
from apriltag_detector import AprilTagMeasurement

detector = AprilTagMeasurement(camera_matrix, distortion_coefficients, tag_size=0.15)
```

### Salida actual de los scripts Python

La salida actual corresponde a mediciones visuales de AprilTag (pose/distancia, análisis de escena y reportes JSON).  
El cálculo final de altura de hinca + despeje mínimo + decisión APTO/NO APTO pertenece al sistema integrado objetivo.

## Nota de arquitectura

**LiDAR no forma parte del diseño principal de este prototipo.**
