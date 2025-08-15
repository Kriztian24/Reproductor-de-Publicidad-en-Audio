# 🎵 Reproductor de Cuñas Automático

Un sistema inteligente que reproduce automáticamente cuñas de audio a intervalos aleatorios, atenuando temporalmente la música de fondo de otras aplicaciones para que la cuña se escuche claramente.

## 📋 Descripción

Este proyecto consiste en un reproductor automático de cuñas que:

- **Detecta automáticamente** cuando hay audio reproduciéndose en otras aplicaciones
- **Atenúa temporalmente** el volumen de las aplicaciones activas
- **Selecciona cuñas aleatoriamente** de una carpeta con sistema de pesos y fechas de caducidad
- **Reproduce la cuña** con volumen optimizado
- **Restaura automáticamente** el volumen original de las aplicaciones
- **Funciona en segundo plano** sin interrumpir el trabajo del usuario

## 🚀 Características Principales

- ✅ **Reproducción automática** a intervalos aleatorios configurables
- ✅ **Selección inteligente** de cuñas con sistema de pesos y fechas de caducidad
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
├── Cunas/                   # Carpeta con múltiples cuñas de audio
│   ├── [20241201] Promo Navidad _w3.mp3
│   ├── [20241215] Oferta Especial _w2.mp3
│   └── Cuña Permanente.mp3
├── cuna.mp3                 # Archivo de audio de la cuña (legacy)
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
# Tiempo mínimo en segundos entre reproducciones (ej: 30 = 30 segundos)
intervalo_minimo_segundos = 30

# Tiempo máximo en segundos entre reproducciones (ej: 300 = 5 minutos)
intervalo_maximo_segundos = 300

# Carpeta donde se encuentran las cuñas de audio
carpeta_cunas = Cunas

# A qué volumen se bajará la música de fondo (0.0 = silencio, 1.0 = máximo)
# 0.10 es un 10%. Es un buen valor para que la música se escuche muy de fondo.
volumen_atenuado = 0.10

# Para pausar la funcionalidad, crea un archivo con este nombre y ruta
# Bórralo para reanudar. Puedes usar rutas absolutas (ej: C:\Temp\stop.txt)
archivo_stop = stop.txt
```

### Parámetros de Configuración

| Parámetro                   | Descripción                        | Valores Recomendados       |
| --------------------------- | ---------------------------------- | -------------------------- |
| `intervalo_minimo_segundos` | Tiempo mínimo entre reproducciones | 30 (30 seg), 60 (1 min)    |
| `intervalo_maximo_segundos` | Tiempo máximo entre reproducciones | 300 (5 min), 1800 (30 min) |
| `carpeta_cunas`             | Carpeta con las cuñas de audio     | Cunas, Audio, Promos       |
| `volumen_atenuado`          | Volumen de fondo durante la cuña   | 0.10 (10%), 0.05 (5%)      |
| `archivo_stop`              | Archivo para pausar el sistema     | stop.txt                   |

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

## 🎲 Sistema de Cuñas Inteligente

### Formato de Nombres de Archivo

El sistema utiliza un formato especial para los nombres de las cuñas que permite:

- **Fechas de caducidad**: `[YYYYMMDD] Nombre de la cuña.mp3`
- **Sistema de pesos**: `Nombre de la cuña _wX.mp3`
- **Combinación**: `[20241201] Promo Navidad _w3.mp3`

### Ejemplos de Nomenclatura

| Formato   | Descripción                        | Ejemplo                              |
| --------- | ---------------------------------- | ------------------------------------ |
| Sin fecha | Cuña permanente                    | `Cuña Permanente.mp3`                |
| Con fecha | Caduca en fecha específica         | `[20241201] Promo Navidad.mp3`       |
| Con peso  | Mayor probabilidad de reproducción | `Oferta Especial _w5.mp3`            |
| Completo  | Fecha + peso                       | `[20241215] Oferta Especial _w2.mp3` |

### Lógica de Selección

1. **Filtrado por fecha**: Solo se consideran cuñas no caducadas o permanentes
2. **Sistema de pesos**: Las cuñas con `_wX` tienen X veces más probabilidad de ser elegidas
3. **Selección aleatoria**: El sistema elige una cuña al azar basándose en los pesos
4. **Peso por defecto**: Las cuñas sin peso tienen peso = 1

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
- **Selección de Cuñas**: Función `elegir_cuna_aleatoria()` con sistema de pesos y fechas
- **Detección de Audio**: Función `get_sesiones_activas()` usando pycaw
- **Reproducción**: Función `reproducir_cuna_con_volumen()` usando pygame
- **Logging**: Clase `FileLogger` para logs automáticos
- **Bucle Principal**: Control de intervalos aleatorios y gestión de pausas

## 🔍 Solución de Problemas

### Problemas Comunes

1. **No se reproduce la cuña**

   - Verifica que la carpeta `Cunas/` existe y contiene archivos de audio
   - Comprueba que los archivos de audio no estén corruptos
   - Asegúrate de que hay cuñas válidas (no caducadas o permanentes)

2. **No se atenúa el volumen**

   - Asegúrate de que hay aplicaciones reproduciendo audio
   - Verifica los permisos del sistema

3. **El programa se cierra inesperadamente**

   - Revisa el archivo `log_reproductor.txt` para errores
   - Verifica que todas las dependencias estén instaladas

4. **Intervalos muy cortos o largos**
   - Ajusta `intervalo_minimo_segundos` y `intervalo_maximo_segundos` en `config.txt`
   - El sistema elige un valor aleatorio entre estos dos parámetros

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
- **Intervalos aleatorios**: El sistema elige un tiempo aleatorio entre el mínimo y máximo configurado
- **Sistema de pesos**: Utiliza `random.choices()` con pesos para seleccionar cuñas
- **Validación de fechas**: Compara fechas en formato YYYYMMDD para filtrar cuñas caducadas

## 🤝 Contribuciones

Para contribuir al proyecto:

1. Fork el repositorio
2. Crea una rama para tu feature
3. Realiza tus cambios
4. Envía un pull request

---

**Desarrollado con IA para automatizar la reproducción de cuñas de audio**
