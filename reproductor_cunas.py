# ==============================================================================
# === REPRODUCTOR DE CUÑAS AUTOMÁTICO - VERSIÓN FINAL ===
# ==============================================================================

# --- 1. IMPORTACIÓN DE LIBRERÍAS ---
# Se importan todas las herramientas que necesitaremos para el proyecto.

import configparser  # Para leer el archivo de configuración 'config.txt'.
import os  # Para interactuar con el sistema operativo (rutas de archivos).
import sys  # Para detectar si el script se ejecuta como .exe y para los logs.
import time  # Para manejar pausas y temporizadores.

import pygame  # Para reproducir el audio de la cuña con control de volumen.
# Importación específica para controlar el audio de otras aplicaciones en Windows.
from pycaw.pycaw import AudioUtilities

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
        # Estamos ejecutando como un .exe empaquetado.
        return os.path.dirname(sys.executable)
    else:
        # Estamos ejecutando como un script .py normal.
        return os.path.dirname(os.path.abspath(__file__))

# Se define la ruta base una sola vez al inicio del script.
RUTA_BASE = obtener_ruta_base()

class FileLogger:
    """
    Una clase personalizada para redirigir los mensajes de 'print()' a un archivo de texto.
    Esto nos permite tener un log de actividad cuando el .exe se ejecuta en segundo plano.
    """
    def __init__(self, filename):
        # Abre el archivo en modo 'append' ('a') para añadir logs sin borrar los anteriores.
        self.log_file = open(filename, 'a', encoding='utf-8')
    
    def write(self, message):
        """
        Este método se llama cada vez que el programa intenta imprimir algo.
        Añade una marca de tiempo antes de escribir el mensaje en el archivo.
        """
        timestamp = time.strftime("[%Y-%m-%d %H:%M:%S] ")
        # Solo añade timestamp a líneas con contenido para un log más limpio.
        if message.strip():
            self.log_file.write(f"{timestamp}{message}")
        else:
            self.log_file.write(message)
        self.flush() # Se asegura de que el mensaje se escriba en el disco inmediatamente.

    def flush(self):
        """Método necesario para que la redirección de salida funcione correctamente."""
        self.log_file.flush()

# Lógica de redirección: solo se activa si el script es un .exe.
if getattr(sys, 'frozen', False):
    log_path = os.path.join(RUTA_BASE, "log_reproductor.txt")
    # Redirige la salida estándar (print) a nuestro archivo de log.
    sys.stdout = FileLogger(log_path)
    # Redirige también los errores. Si el programa falla, el error quedará guardado.
    sys.stderr = sys.stdout


# --- 3. DEFINICIÓN DE CONSTANTES Y FUNCIONES PRINCIPALES ---

# Lista de procesos del sistema que debemos ignorar para no bajarles el volumen por error.
PROCESOS_IGNORADOS = ["SystemSoundsService.exe", "audiodg.exe", "python.exe", "py.exe"]

def cargar_configuracion():
    """
    Lee el archivo 'config.txt' y devuelve los ajustes.
    Si el archivo no existe, lo crea con valores por defecto para facilitar el primer uso.
    """
    config = configparser.ConfigParser()
    defaults = {
        'intervalo_segundos': '1800',
        'ruta_cuna': 'cuna.mp3',
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
    
    # Se leen los valores y se convierten al tipo de dato correcto (int, float, string).
    # Se usan rutas absolutas para evitar cualquier ambigüedad.
    settings = {
        'intervalo': config.getint('Settings', 'intervalo_segundos', fallback=int(defaults['intervalo_segundos'])),
        'ruta_cuna': os.path.join(RUTA_BASE, config.get('Settings', 'ruta_cuna', fallback=defaults['ruta_cuna'])),
        'volumen_atenuado': config.getfloat('Settings', 'volumen_atenuado', fallback=float(defaults['volumen_atenuado'])),
        'archivo_stop': os.path.join(RUTA_BASE, config.get('Settings', 'archivo_stop', fallback=defaults['archivo_stop']))
    }
    return settings

def get_sesiones_activas():
    """
    Utiliza pycaw para escanear todas las aplicaciones que están emitiendo sonido.
    Devuelve una lista de las sesiones de audio activas, ignorando las del sistema.
    """
    sesiones_activas = []
    try:
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            # session.State == 1 significa que la sesión está activa (sonando).
            if session.State == 1 and session.Process and session.Process.name() not in PROCESOS_IGNORADOS:
                sesiones_activas.append(session)
    except Exception as e:
        print(f"Error al obtener sesiones de audio: {e}")
    return sesiones_activas

def reproducir_cuna_con_volumen(ruta_audio, volumen):
    """
    Utiliza pygame para reproducir el archivo de la cuña con un volumen específico.
    Espera a que la cuña termine antes de continuar.
    """
    try:
        print(f"Reproduciendo cuña a un volumen de {volumen:.0%}")
        pygame.mixer.init()
        pygame.mixer.music.load(ruta_audio)
        pygame.mixer.music.set_volume(volumen) # Ajusta el volumen (0.0 a 1.0)
        pygame.mixer.music.play()
        # Bucle que espera hasta que la música de pygame termine.
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.quit()
        print("La cuña ha terminado.")
    except Exception as e:
        print(f"Error al reproducir la cuña con Pygame: {e}")
        # Se asegura de que pygame se cierre si hay un error.
        if pygame.mixer.get_init():
            pygame.mixer.quit()


# --- 4. BUCLE PRINCIPAL DE LA APLICACIÓN ---
# Este bucle se ejecuta infinitamente, es el corazón del programa.

print(f"Iniciando el reproductor de cuñas (v_final - A prueba de fallos). PID: {os.getpid()}")

# Variables para controlar el tiempo y el estado del programa.
ultimo_lanzamiento = 0
primera_vez = True
en_pausa = False

while True:
    # Carga la configuración en cada ciclo para detectar cambios al instante.
    config = cargar_configuracion()
    
    # Lógica de pausa: comprueba si existe el archivo 'stop.txt'.
    if os.path.exists(config['archivo_stop']):
        if not en_pausa:
            print(f"\nArchivo '{os.path.basename(config['archivo_stop'])}' detectado. Funcionalidad en pausa.")
            en_pausa = True
        time.sleep(5)
        continue # Salta el resto del ciclo y vuelve a empezar.

    # Si salimos de la pausa, se notifica y se reinicia el temporizador.
    if en_pausa:
        print(f"\nArchivo '{os.path.basename(config['archivo_stop'])}' no encontrado. Reanudando funcionalidad.")
        en_pausa = False
        ultimo_lanzamiento = time.time()
        print(f"Temporizador reiniciado. Próxima comprobación en {config['intervalo'] / 60:.1f} minutos...")
    
    # En la primera ejecución, se inicializa el temporizador.
    if primera_vez:
        print(f"Configuración cargada: Intervalo {config['intervalo'] / 60:.1f} min, Cuña '{os.path.basename(config['ruta_cuna'])}'")
        ultimo_lanzamiento = time.time()
        primera_vez = False

    # Comprueba si ya ha pasado el tiempo para la siguiente cuña.
    if time.time() - ultimo_lanzamiento >= config['intervalo']:
        print("\n¡Tiempo de intervalo cumplido! Comprobando si hay audio...")
        
        if not os.path.exists(config['ruta_cuna']):
            print(f"¡ERROR! No se encontró el archivo de cuña '{config['ruta_cuna']}'.")
        else:
            sesiones_activas = get_sesiones_activas()
            if sesiones_activas:
                
                volumenes_originales = {}
                
                # --- Bloque de seguridad TRY...FINALLY ---
                # Esto garantiza que el volumen se restaure incluso si el programa
                # se cierra o falla mientras la cuña se está reproduciendo.
                try:
                    # --- FASE 1: ATENUAR VOLUMEN ---
                    print(f"¡Audio detectado en {len(sesiones_activas)} aplicación(es)!")
                    volumen_objetivo_cuna = 0.8 # Volumen por defecto
                    print("Atenuando música de fondo...")
                    for i, session in enumerate(sesiones_activas):
                        volume_control = session.SimpleAudioVolume
                        volumen_actual = volume_control.GetMasterVolume()
                        volumenes_originales[session.Process.pid] = (session, volumen_actual)
                        if i == 0:
                            volumen_objetivo_cuna = volumen_actual # Adapta el volumen de la cuña
                            print(f"   -> {session.Process.name()} [PID: {session.Process.pid}] está a {volumen_actual:.0%}. Se usará como referencia.")
                        volume_control.SetMasterVolume(config['volumen_atenuado'], None)

                    # --- FASE 2: REPRODUCIR CUÑA ---
                    reproducir_cuna_con_volumen(config['ruta_cuna'], volumen_objetivo_cuna)

                finally:
                    # --- FASE 3: RESTAURAR VOLUMEN (SE EJECUTA SIEMPRE) ---
                    if volumenes_originales:
                        print("Restaurando volumen original...")
                        for pid, (session, vol_original) in volumenes_originales.items():
                            try:
                                session.SimpleAudioVolume.SetMasterVolume(vol_original, None)
                                print(f"   -> Volumen de {session.Process.name()} [PID: {pid}] restaurado a {vol_original:.0%}")
                            except Exception:
                                # Esto puede pasar si el usuario cerró la aplicación (ej: Chrome) mientras sonaba la cuña.
                                print(f"No se pudo restaurar el volumen para el proceso {pid} (posiblemente se cerró).")
            else:
                print("No se detectó audio. Se omitirá la cuña en este ciclo.")

        # Reinicia el temporizador para el siguiente intervalo.
        ultimo_lanzamiento = time.time()
        print(f"Próxima comprobación en {config['intervalo'] / 60:.1f} minutos...")
    
    # El script "duerme" por 5 segundos antes de volver a empezar el ciclo.
    # Esto es eficiente y permite que detecte cambios en config.txt o stop.txt rápidamente.
    time.sleep(5)