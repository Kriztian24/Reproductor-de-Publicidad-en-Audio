# ==============================================================================
# === REPRODUCTOR DE CUÑAS AUTOMÁTICO - VERSIÓN FINAL ===
# ==============================================================================

# --- 1. IMPORTACIÓN DE LIBRERÍAS ---
# Se importan todas las herramientas que necesitaremos para el proyecto.

import configparser  # Para leer el archivo de configuración 'config.txt'.
import os  # Para interactuar con el sistema operativo (rutas de archivos).
import random  # Importamos el módulo para la aleatoriedad.
import re  # Para analizar los nombres de archivo en busca de pesos.
import sys  # Para detectar si el script se ejecuta como .exe y para los logs.
import time  # Para manejar pausas y temporizadores.
from datetime import datetime

import pygame  # Para reproducir el audio de la cuña con control de volumen.
# Importación específica para controlar el audio de otras aplicaciones en Windows.
from pycaw.pycaw import AudioUtilities

 # Para manejar las fechas de caducidad de las cuñas.


# --- 2. FUNCIONES DE CONFIGURACIÓN INICIAL Y LOGS ---
# Estas funciones preparan el entorno del script, encontrando sus propios archivos
# y configurando el sistema de logs para cuando se ejecute como .exe.

def obtener_ruta_base():
    """
    Determina la carpeta donde se está ejecutando el script.
    Esto es crucial para que el .exe encuentre sus archivos (config.txt, cuna.mp3).
    - sys.frozen: Es una variable que PyInstaller añade cuando empaqueta el script.
    - sys.executable: Es la ruta al .exe.
    - __file__: Es la ruta al .py.
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

RUTA_BASE = obtener_ruta_base()

class FileLogger:
    """
    Una clase personalizada para redirigir los mensajes de 'print()' a un archivo de texto.
    Esto nos permite tener un log de actividad cuando el .exe se ejecuta en segundo plano.
    """
    def __init__(self, filename):
        self.log_file = open(filename, 'a', encoding='utf-8')
    
    def write(self, message):
        timestamp = time.strftime("[%Y-%m-%d %H:%M:%S] ")
        if message.strip():
            self.log_file.write(f"{timestamp}{message}")
        else:
            self.log_file.write(message)
        self.flush()

    def flush(self):
        self.log_file.flush()

if getattr(sys, 'frozen', False):
    log_path = os.path.join(RUTA_BASE, "log_reproductor.txt")
    sys.stdout = FileLogger(log_path)
    sys.stderr = sys.stdout


# --- 3. DEFINICIÓN DE CONSTANTES Y FUNCIONES PRINCIPALES ---

PROCESOS_IGNORADOS = ["SystemSoundsService.exe", "audiodg.exe", "python.exe", "py.exe"]

def cargar_configuracion():
    """
    Lee el archivo 'config.txt' y devuelve los ajustes.
    Si el archivo no existe, lo crea con valores por defecto para facilitar el primer uso.
    """
    config = configparser.ConfigParser()
    defaults = {
        'intervalo_minimo_segundos': '30',
        'intervalo_maximo_segundos': '300',
        'carpeta_cunas': 'Cunas', # ---> CAMBIO: De 'ruta_cuna' a 'carpeta_cunas'
        'volumen_atenuado': '0.10',
        'archivo_stop': 'stop.txt'
    }
    
    config_path = os.path.join(RUTA_BASE, 'config.txt')
    if not os.path.exists(config_path):
        print(f"No se encontró '{config_path}'. Creando uno nuevo con valores por defecto.")
        config['Settings'] = defaults
        with open(config_path, 'w') as configfile:
            config.write(configfile)
    
    config.read(config_path)
    
    min_intervalo = config.getint('Settings', 'intervalo_minimo_segundos', fallback=int(defaults['intervalo_minimo_segundos']))
    max_intervalo = config.getint('Settings', 'intervalo_maximo_segundos', fallback=int(defaults['intervalo_maximo_segundos']))
    if min_intervalo > max_intervalo:
        print(f"ADVERTENCIA: El intervalo mínimo ({min_intervalo}s) es mayor que el máximo ({max_intervalo}s). Se invertirán los valores.")
        min_intervalo, max_intervalo = max_intervalo, min_intervalo

    settings = {
        'intervalo_min': min_intervalo,
        'intervalo_max': max_intervalo,
        'carpeta_cunas': os.path.join(RUTA_BASE, config.get('Settings', 'carpeta_cunas', fallback=defaults['carpeta_cunas'])), # ---> CAMBIO
        'volumen_atenuado': config.getfloat('Settings', 'volumen_atenuado', fallback=float(defaults['volumen_atenuado'])),
        'archivo_stop': os.path.join(RUTA_BASE, config.get('Settings', 'archivo_stop', fallback=defaults['archivo_stop']))
    }
    return settings

# ---> FUNCIÓN: Ahora valida la fecha de caducidad en el nombre del archivo.
def elegir_cuna_aleatoria(carpeta_path):
    """
    Busca archivos de audio, filtra los caducados y elige uno al azar
    basado en un sistema de "pesos" definido en el nombre del archivo.
    Formato: '[YYYYMMDD] Nombre de la promo [_wX].mp3'
    - Los archivos sin fecha son permanentes.
    - Los archivos sin peso (_wX) tienen un peso por defecto de 1.
    """
    if not os.path.isdir(carpeta_path):
        print(f"¡ERROR! La carpeta de cuñas '{carpeta_path}' no existe.")
        return None

    hoy_str = datetime.now().strftime("%Y%m%d")
    extensiones_validas = ('.mp3', '.wav', '.ogg')
    
    cunas_validas = [] # ---> Lista para los nombres de archivo.
    pesos_cunas = []   # ---> Lista para los pesos correspondientes.

    for nombre_archivo in os.listdir(carpeta_path):
        if not nombre_archivo.lower().endswith(extensiones_validas):
            continue

        # 1. Validación por fecha (lógica ya existente)
        es_valida_por_fecha = False
        if len(nombre_archivo) > 8 and nombre_archivo[:8].isdigit():
            fecha_caducidad_str = nombre_archivo[:8]
            if fecha_caducidad_str >= hoy_str:
                es_valida_por_fecha = True
            else:
                print(f"INFO: Omitiendo cuña caducada: '{nombre_archivo}'")
        else:
            es_valida_por_fecha = True # Es permanente (sin fecha)

        # 2. Si es válida por fecha, extraemos su peso.
        if es_valida_por_fecha:
            # Quitamos la extensión para facilitar la búsqueda del peso.
            nombre_sin_extension, _ = os.path.splitext(nombre_archivo)
            
            # Usamos una expresión regular para encontrar el patrón '_w' seguido de dígitos al final.
            match = re.search(r'_w(\d+)$', nombre_sin_extension)
            
            peso_actual = 1 # Peso por defecto
            if match:
                # Si encontramos el patrón, extraemos el número y lo convertimos a entero.
                peso_actual = int(match.group(1))
                if peso_actual < 1: peso_actual = 1 # El peso mínimo es 1.
                print(f"INFO: Cuña '{nombre_archivo}' tiene un peso de {peso_actual}.")
            
            # Añadimos la cuña y su peso a nuestras listas.
            cunas_validas.append(nombre_archivo)
            pesos_cunas.append(peso_actual)

    # 3. Hacemos el sorteo ponderado.
    if cunas_validas:
        # random.choices() devuelve una lista, por eso tomamos el primer elemento [0].
        # El parámetro 'weights' le indica la probabilidad de cada elemento.
        nombre_cuna_elegida = random.choices(cunas_validas, weights=pesos_cunas, k=1)[0]
        
        print(f"Se ha elegido la cuña ponderada y aleatoria: '{nombre_cuna_elegida}'")
        return os.path.join(carpeta_path, nombre_cuna_elegida)
    else:
        print(f"ADVERTENCIA: No se encontraron cuñas válidas (no caducadas o permanentes) en la carpeta.")
        return None

def get_sesiones_activas():
    # ... (Sin cambios aquí)
    sesiones_activas = []
    try:
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.State == 1 and session.Process and session.Process.name() not in PROCESOS_IGNORADOS:
                sesiones_activas.append(session)
    except Exception as e:
        print(f"Error al obtener sesiones de audio: {e}")
    return sesiones_activas

def reproducir_cuna_con_volumen(ruta_audio, volumen):
    # ... (Sin cambios aquí)
    try:
        print(f"Reproduciendo cuña a un volumen de {volumen:.0%}")
        pygame.mixer.init()
        pygame.mixer.music.load(ruta_audio)
        pygame.mixer.music.set_volume(volumen)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.quit()
        print("La cuña ha terminado.")
    except Exception as e:
        print(f"Error al reproducir la cuña con Pygame: {e}")
        if pygame.mixer.get_init():
            pygame.mixer.quit()

# --- 4. BUCLE PRINCIPAL DE LA APLICACIÓN ---
print(f"Iniciando el reproductor de cuñas (v_final - A prueba de fallos). PID: {os.getpid()}")

ultimo_lanzamiento = 0
primera_vez = True
en_pausa = False
proximo_intervalo = 0

while True:
    config = cargar_configuracion()
    
    if os.path.exists(config['archivo_stop']):
        if not en_pausa:
            print(f"\nArchivo '{os.path.basename(config['archivo_stop'])}' detectado. Funcionalidad en pausa.")
            en_pausa = True
        time.sleep(5)
        continue

    if en_pausa:
        print(f"\nArchivo '{os.path.basename(config['archivo_stop'])}' no encontrado. Reanudando funcionalidad.")
        en_pausa = False
        # ---> CAMBIO: Al reanudar, forzamos que se regenere el temporizador reiniciando el 'primer arranque'.
        primera_vez = True

    if primera_vez:
        proximo_intervalo = random.randint(config['intervalo_min'], config['intervalo_max'])
        # ---> CAMBIO: El mensaje de inicio ahora muestra la carpeta en lugar de un archivo.
        print(f"Configuración cargada: Carpeta de cuñas '{os.path.basename(config['carpeta_cunas'])}', Intervalo aleatorio entre {config['intervalo_min']}s y {config['intervalo_max']}s.")
        print(f"Próxima comprobación en {proximo_intervalo / 60:.1f} minutos...")
        ultimo_lanzamiento = time.time()
        primera_vez = False

    if time.time() - ultimo_lanzamiento >= proximo_intervalo:
        print("\n¡Tiempo de intervalo cumplido! Comprobando si hay audio...")
        
        # ---> CAMBIO: Se elige una cuña de la carpeta ANTES de buscar audio.
        cuna_a_reproducir = elegir_cuna_aleatoria(config['carpeta_cunas'])
        
        # ---> CAMBIO: El resto de la lógica solo se ejecuta si se encontró una cuña.
        if cuna_a_reproducir:
            sesiones_activas = get_sesiones_activas()
            if sesiones_activas:
                volumenes_originales = {}
                try:
                    # --- FASE 1: ATENUAR VOLUMEN ---
                    print(f"¡Audio detectado en {len(sesiones_activas)} aplicación(es)!")
                    volumen_objetivo_cuna = 0.8
                    print("Atenuando música de fondo...")
                    for i, session in enumerate(sesiones_activas):
                        volume_control = session.SimpleAudioVolume
                        volumen_actual = volume_control.GetMasterVolume()
                        volumenes_originales[session.Process.pid] = (session, volumen_actual)
                        if i == 0:
                            volumen_objetivo_cuna = volumen_actual
                            print(f"   -> {session.Process.name()} [PID: {session.Process.pid}] está a {volumen_actual:.0%}. Se usará como referencia.")
                        volume_control.SetMasterVolume(config['volumen_atenuado'], None)

                    # --- FASE 2: REPRODUCIR CUÑA ---
                    # ---> CAMBIO: Se reproduce la cuña elegida aleatoriamente.
                    reproducir_cuna_con_volumen(cuna_a_reproducir, volumen_objetivo_cuna)
                finally:
                    # --- FASE 3: RESTAURAR VOLUMEN (SE EJECUTA SIEMPRE) ---
                    if volumenes_originales:
                        print("Restaurando volumen original...")
                        for pid, (session, vol_original) in volumenes_originales.items():
                            try:
                                session.SimpleAudioVolume.SetMasterVolume(vol_original, None)
                                print(f"   -> Volumen de {session.Process.name()} [PID: {pid}] restaurado a {vol_original:.0%}")
                            except Exception:
                                print(f"No se pudo restaurar el volumen para el proceso {pid} (posiblemente se cerró).")
            else:
                print("No se detectó audio. Se omitirá la cuña en este ciclo.")
        
        # Reinicia el temporizador para el siguiente intervalo.
        ultimo_lanzamiento = time.time()
        proximo_intervalo = random.randint(config['intervalo_min'], config['intervalo_max'])
        print(f"Próxima comprobación en {proximo_intervalo / 60:.1f} minutos (valor aleatorio).")
    
    time.sleep(5)