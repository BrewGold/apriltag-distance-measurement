#!/bin/bash

# Script de instalación para Raspberry Pi

echo "================================================"
echo "Instalación - Sistema de Medición AprilTag"
echo "================================================"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "Instalando Python3..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip
fi

echo "✓ Python3 encontrado: $(python3 --version)"

# Actualizar pip
echo ""
echo "Actualizando pip..."
python3 -m pip install --upgrade pip setuptools wheel

# Instalar dependencias del sistema
echo ""
echo "Instalando dependencias del sistema..."
sudo apt-get install -y \
    libatlas-base-dev \
    libjasper-dev \
    libtiff-dev \
    libjasper1 \
    libjasper-dev \
    libhdf5-dev \
    libharfbuzz0b \
    libwebp6 \
    libtiff5 \
    libjasper1 \
    libatlas3-base \
    libharfbuzz0b \
    libwebp6 \
    libtiff5 \
    libjasper1

# Instalar dependencias Python
echo ""
echo "Instalando dependencias Python..."
python3 -m pip install -r requirements.txt

# Crear directorios
echo ""
echo "Creando directorios..."
mkdir -p measurements calibration_images

# Verificar instalación
echo ""
echo "Verificando instalación..."
python3 -c "import cv2; print(f'✓ OpenCV: {cv2.__version__}')"
python3 -c "import numpy; print(f'✓ NumPy: {numpy.__version__}')"
python3 -c "from pupil_apriltags import AprilTagDetector; print('✓ Pupil AprilTags')"

echo ""
echo "================================================"
echo "Instalación completada"
echo "================================================"
echo ""
echo "Próximos pasos:"
echo "1. Calibra la cámara:"
echo "   python3 main.py --mode calibrate"
echo ""
echo "2. Ejecuta mediciones:"
echo "   python3 main.py --mode measure"
echo ""
echo "3. Ver calibración:"
echo "   python3 main.py --mode info"
echo ""
