# 🎵 Reproductor de Cuñas Automático

Un sistema inteligente que reproduce automáticamente cuñas de audio a intervalos regulares, atenuando temporalmente la música de fondo de otras aplicaciones para que la cuña se escuche claramente.

## 📋 Descripción

Este proyecto consiste en un reproductor automático de cuñas que:

- **Detecta automáticamente** cuando hay audio reproduciéndose en otras aplicaciones
- **Atenúa temporalmente** el volumen de las aplicaciones activas
- **Reproduce la cuña** con volumen optimizado
- **Restaura automáticamente** el volumen original de las aplicaciones
- **Funciona en segundo plano** sin interrumpir el trabajo del usuario

## 🚀 Características Principales

- ✅ **Reproducción automática** a intervalos configurables
- ✅ **Detección inteligente** de aplicaciones con audio activo
- ✅ **Control de volumen** automático y seguro
- ✅ **Sistema de pausa** mediante archivo de control
- ✅ **Logs detallados** para monitoreo y debugging
- ✅ **Configuración flexible** mediante archivo de texto
- ✅ **Ejecutable independiente** (no requiere Python instalado)

## 📁 Estructura del Proyecto

```
Cuña auto/
├── reproductor_cunas.py      # Código fuente principal
├── config.txt               # Archivo de configuración
├── cuna.mp3                 # Archivo de audio de la cuña
├── cuna.mpeg                # Versión alternativa del audio
├── stop1.txt               # Archivo para pausar la funcionalidad
├── ReproductorCunas.spec   # Especificación para PyInstaller
└── Release/                # Carpeta con el ejecutable
    ├── ReproductorCunas.exe # Ejecutable compilado
    ├── config.txt          # Configuración para el ejecutable
    └── cuna.mp3            # Audio para el ejecutable
```

## ⚙️ Configuración

El archivo `config.txt` permite personalizar el comportamiento del reproductor:

```ini
[Settings]
# Tiempo en segundos entre cada reproducción de la cuña
# Ejemplos: 300 = 5 minutos, 1800 = 30 minutos, 3600 = 1 hora
intervalo_segundos = 1800

# Nombre del archivo de audio de la cuña (debe estar en la misma carpeta)
ruta_cuna = cuna.mp3

# A qué volumen se bajará la música de fondo (0.0 = silencio, 1.0 = máximo)
# 0.10 es un 10%. Es un buen valor para que la música se escuche muy de fondo.
volumen_atenuado = 0.10

# Para pausar la funcionalidad, crea un archivo con este nombre y ruta
# Bórralo para reanudar. Puedes usar rutas absolutas (ej: C:\Temp\stop.txt)
archivo_stop = stop.txt
```

### Parámetros de Configuración

| Parámetro            | Descripción                      | Valores Recomendados         |
| -------------------- | -------------------------------- | ---------------------------- |
| `intervalo_segundos` | Tiempo entre reproducciones      | 1800 (30 min), 3600 (1 hora) |
| `ruta_cuna`          | Archivo de audio a reproducir    | cuna.mp3, cuna.wav           |
| `volumen_atenuado`   | Volumen de fondo durante la cuña | 0.10 (10%), 0.05 (5%)        |
| `archivo_stop`       | Archivo para pausar el sistema   | stop.txt                     |

## 🎯 Uso

### Opción 1: Ejecutable (Recomendado)

1. Ve a la carpeta `Release/`
2. Ejecuta `ReproductorCunas.exe`
3. El programa comenzará a funcionar automáticamente

### Opción 2: Código Fuente

1. Asegúrate de tener Python instalado
2. Instala las dependencias:
   ```bash
   pip install pygame pycaw
   ```
3. Ejecuta el script:
   ```bash
   python reproductor_cunas.py
   ```

## 🎛️ Control del Sistema

### Pausar/Reanudar

- **Para pausar**: Crea un archivo llamado `stop.txt` en la carpeta del programa
- **Para reanudar**: Elimina el archivo `stop.txt`

### Monitoreo

- El programa genera logs automáticamente en `log_reproductor.txt`
- Los logs incluyen timestamps y detalles de cada operación
- Útil para debugging y monitoreo del sistema

## 🔧 Requisitos del Sistema

- **Sistema Operativo**: Windows 10/11
- **Audio**: Tarjeta de sonido compatible con Windows
- **Permisos**: Acceso al control de volumen del sistema
- **Espacio**: ~20MB para el ejecutable + archivos de audio

## 📦 Dependencias (Solo para desarrollo)

- `pygame` - Reproducción de audio
- `pycaw` - Control de volumen de Windows
- `configparser` - Lectura de archivos de configuración

## 🛠️ Desarrollo

### Compilar el Ejecutable

Para crear el ejecutable desde el código fuente:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed ReproductorCunas.spec
python -m PyInstaller --onefile --windowed --name="ReproductorCunas" reproductor_cunas.py
```

### Estructura del Código

- **Configuración**: Función `cargar_configuracion()` para leer `config.txt`
- **Detección de Audio**: Función `get_sesiones_activas()` usando pycaw
- **Reproducción**: Función `reproducir_cuna_con_volumen()` usando pygame
- **Logging**: Clase `FileLogger` para logs automáticos
- **Bucle Principal**: Control de intervalos y gestión de pausas

## 🔍 Solución de Problemas

### Problemas Comunes

1. **No se reproduce la cuña**

   - Verifica que `cuna.mp3` existe en la carpeta
   - Comprueba que el archivo de audio no esté corrupto

2. **No se atenúa el volumen**

   - Asegúrate de que hay aplicaciones reproduciendo audio
   - Verifica los permisos del sistema

3. **El programa se cierra inesperadamente**
   - Revisa el archivo `log_reproductor.txt` para errores
   - Verifica que todas las dependencias estén instaladas

### Logs de Debug

El archivo `log_reproductor.txt` contiene información detallada:

- Timestamps de cada operación
- Detección de aplicaciones con audio
- Cambios de volumen realizados
- Errores y excepciones

## 📝 Notas Técnicas

- El programa utiliza `pycaw` para controlar el volumen de aplicaciones específicas
- `pygame` se usa para reproducir la cuña con control preciso del volumen
- El sistema de logs funciona automáticamente cuando se ejecuta como .exe
- Los cambios de configuración se detectan en tiempo real

## 🤝 Contribuciones

Para contribuir al proyecto:

1. Fork el repositorio
2. Crea una rama para tu feature
3. Realiza tus cambios
4. Envía un pull request

---

**Desarrollado con IA para automatizar la reproducción de cuñas de audio**
