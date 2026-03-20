import tkinter as tk
from tkinter import messagebox
import datetime
import socket
import threading
import json
import os
import random
import string
import configparser
import sys
import urllib.request

# ─────────────────────────────────────────
NAME = "OneFileTextChat"
# ─────────────────────────────────────────

# Корректный путь и в .py-скрипте, и в .exe (PyInstaller)
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
    # Ресурсы, упакованные внутрь exe, распакованы во временную папку _MEIPASS
    _RES_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    _RES_DIR = BASE_DIR

DATA_DIR  = os.path.join(_RES_DIR, "DATA")
SAVE_PATH = os.path.join(BASE_DIR, "OFTC_Save.ini")   # сохранения — рядом с exe
ICON_PATH = os.path.join(DATA_DIR, "ico.ico")

ID   = "00000"
PORT = "00001"

def generate_random_string(length=10):
    characters = string.ascii_letters + string.digits
    random_str = ''.join(random.choices(characters, k=length))
    return random_str

RANDOM_ID   = generate_random_string(10)
RANDOM_PORT = generate_random_string(6)

# ── Сеть: внешний IP и UPnP ──────────────────
def get_external_ip():
    """Получает внешний IP через публичный сервис."""
    try:
        with urllib.request.urlopen("https://api.ipify.org", timeout=4) as r:
            return r.read().decode().strip()
    except Exception:
        pass
    try:
        with urllib.request.urlopen("https://checkip.amazonaws.com", timeout=4) as r:
            return r.read().decode().strip()
    except Exception:
        return None

def upnp_add_port(port):
    """Пробрасывает порт через UPnP. Возвращает внешний IP или None."""
    try:
        import miniupnpc
        u = miniupnpc.UPnP()
        u.discoverdelay = 200
        u.discover()
        u.selectigd()
        u.addportmapping(port, 'TCP', u.lanaddr, port,
                         f'{NAME} port {port}', '')
        return u.externalipaddress()
    except Exception:
        return None

def upnp_remove_port(port):
    """Удаляет проброс порта UPnP."""
    try:
        import miniupnpc
        u = miniupnpc.UPnP()
        u.discoverdelay = 200
        u.discover()
        u.selectigd()
        u.deleteportmapping(port, 'TCP')
    except Exception:
        pass


# ── Темы ──────────────────────────────────
THEMES = {
    "dark": {
        "BG_DARK":    "#0d0d0d",
        "BG_PANEL":   "#141414",
        "BG_INPUT":   "#1c1c1c",
        "BORDER":     "#2a2a2a",
        "TEXT_MAIN":  "#f0f0f0",
        "TEXT_DIM":   "#666666",
        "ACCENT":     "#ffffff",
        "ACCENT2":    "#aaaaaa",
        "BTN_FG":     "#ffffff",
        "STATUS_OK":  "#888888",
        "STATUS_ERR": "#ff4444",
        "TOAST_BG":   "#1c1c1c",
        "TOAST_FG":   "#f0f0f0",
    },
    "light": {
        "BG_DARK":    "#f5f5f5",
        "BG_PANEL":   "#e8e8e8",
        "BG_INPUT":   "#ffffff",
        "BORDER":     "#cccccc",
        "TEXT_MAIN":  "#0d0d0d",
        "TEXT_DIM":   "#888888",
        "ACCENT":     "#000000",
        "ACCENT2":    "#444444",
        "BTN_FG":     "#000000",
        "STATUS_OK":  "#333333",
        "STATUS_ERR": "#cc0000",
        "TOAST_BG":   "#ffffff",
        "TOAST_FG":   "#0d0d0d",
    },
}

LANG_NAMES = {
    "en": "English",
    "ru": "Русский",
    "uk": "Українська",
    "de": "Deutsch",
    "fr": "Français",
    "es": "Español",
    "pl": "Polski",
    "pt": "Português",
    "it": "Italiano",
    "zh": "中文",
    "ja": "日本語",
    "ko": "한국어",
}

TRANSLATIONS = {
    "en": {
        "section_connection": "CONNECTION",
        "btn_create": "⚡  Create Chat",
        "btn_connect": "🔗  Connect",
        "btn_disconnect": "✕   Disconnect",
        "btn_theme": "◑  Toggle Theme",
        "btn_tray": "▼  To Tray",
        "lang_label": "🌐 Language",
        "status_disconnected": "● Not Connected",
        "status_waiting": "⏳ Waiting :{port}",
        "status_connected": "● Connected  {addr}",
        "status_broken": "● Connection Lost",
        "chat_title": "Chat",
        "btn_send": "Send",
        "welcome": "Create or connect to a chat",
        "enter_name": "Enter your name",
        "btn_enter": "Enter",
        "win_create": "Create Chat",
        "create_header": "⚡  Create Chat",
        "create_desc": "The other participant must connect to your IP and Port",
        "label_local_ip": "Local IP:",
        "label_ext_ip": "Ext. IP:",
        "label_port": "Port:",
        "btn_start": "Start Chat",
        "btn_starting": "Starting…",
        "upnp_trying": "⏳ Trying UPnP port mapping…",
        "upnp_ok": "✔ UPnP: port {port} mapped automatically",
        "upnp_fail": "⚠ UPnP failed — forward port {port} manually on your router",
        "win_connect": "Connect",
        "connect_header": "🔗  Connect",
        "connect_desc": "Enter the IP address and port of your contact's server",
        "label_ip": "IP/Host:",
        "btn_do_connect": "Connect",
        "already_connected": "Already connected!",
        "port_number": "Port must be a number!",
        "waiting_on": "Waiting for connection on {ip}:{port}…",
        "local_net": "Local network: {ip}:{port}",
        "enter_ip": "Enter the server IP address!",
        "conn_error": "Connection error:\n{e}",
        "connected_to": "Connected: {addr}",
        "peer_joined": "{name} joined",
        "no_conn": "No connection — connect first",
        "send_error": "Send error: {e}",
        "disconnected": "Disconnected",
        "peer_disconnected": "Contact disconnected",
        "failed_start": "Failed to start chat:\n{e}",
        "tray_open": "Open",
        "tray_exit": "Exit",
        "peer_default": "Contact",
    },
    "ru": {
        "section_connection": "СОЕДИНЕНИЕ",
        "btn_create": "⚡  Создать чат",
        "btn_connect": "🔗  Подключиться",
        "btn_disconnect": "✕   Отключиться",
        "btn_theme": "◑  Сменить тему",
        "btn_tray": "▼  В трей",
        "lang_label": "🌐 Язык",
        "status_disconnected": "● Не подключён",
        "status_waiting": "⏳ Ожидание :{port}",
        "status_connected": "● Подключён  {addr}",
        "status_broken": "● Соединение разорвано",
        "chat_title": "Чат",
        "btn_send": "Отправить",
        "welcome": "Создайте или подключитесь к чату",
        "enter_name": "Введите ваше имя",
        "btn_enter": "Войти",
        "win_create": "Создать чат",
        "create_header": "⚡  Создать чат",
        "create_desc": "Другой участник должен подключиться к вашему IP и Порту",
        "label_local_ip": "Лок. IP:",
        "label_ext_ip": "Внеш. IP:",
        "label_port": "Порт:",
        "btn_start": "Запустить чат",
        "btn_starting": "Запуск…",
        "upnp_trying": "⏳ Пробую UPnP проброс порта…",
        "upnp_ok": "✔ UPnP: порт {port} проброшен автоматически",
        "upnp_fail": "⚠ UPnP не сработал — пробросьте порт {port} вручную на роутере",
        "win_connect": "Подключиться",
        "connect_header": "🔗  Подключиться",
        "connect_desc": "Введите IP-адрес и порт сервера собеседника",
        "label_ip": "IP/Хост:",
        "btn_do_connect": "Подключиться",
        "already_connected": "Уже подключено!",
        "port_number": "Порт должен быть числом!",
        "waiting_on": "Ожидание подключения на {ip}:{port}…",
        "local_net": "Локальная сеть: {ip}:{port}",
        "enter_ip": "Введите IP-адрес сервера!",
        "conn_error": "Ошибка подключения:\n{e}",
        "connected_to": "Подключено: {addr}",
        "peer_joined": "{name} присоединился",
        "no_conn": "Нет соединения — подключитесь сначала",
        "send_error": "Ошибка отправки: {e}",
        "disconnected": "Отключено",
        "peer_disconnected": "Собеседник отключился",
        "failed_start": "Не удалось запустить чат:\n{e}",
        "tray_open": "Открыть",
        "tray_exit": "Выход",
        "peer_default": "Собеседник",
    },
    "uk": {
        "section_connection": "З'ЄДНАННЯ",
        "btn_create": "⚡  Створити чат",
        "btn_connect": "🔗  Підключитися",
        "btn_disconnect": "✕   Відключитися",
        "btn_theme": "◑  Змінити тему",
        "btn_tray": "▼  У трей",
        "lang_label": "🌐 Мова",
        "status_disconnected": "● Не підключено",
        "status_waiting": "⏳ Очікування :{port}",
        "status_connected": "● Підключено  {addr}",
        "status_broken": "● З'єднання перервано",
        "chat_title": "Чат",
        "btn_send": "Надіслати",
        "welcome": "Створіть або підключіться до чату",
        "enter_name": "Введіть ваше ім'я",
        "btn_enter": "Увійти",
        "win_create": "Створити чат",
        "create_header": "⚡  Створити чат",
        "create_desc": "Інший учасник повинен підключитися до вашого IP та Порту",
        "label_local_ip": "Лок. IP:",
        "label_ext_ip": "Зовн. IP:",
        "label_port": "Порт:",
        "btn_start": "Запустити чат",
        "btn_starting": "Запуск…",
        "upnp_trying": "⏳ Пробую UPnP перенаправлення порту…",
        "upnp_ok": "✔ UPnP: порт {port} перенаправлено автоматично",
        "upnp_fail": "⚠ UPnP не спрацював — перенаправте порт {port} вручну на роутері",
        "win_connect": "Підключитися",
        "connect_header": "🔗  Підключитися",
        "connect_desc": "Введіть IP-адресу та порт сервера співрозмовника",
        "label_ip": "IP/Хост:",
        "btn_do_connect": "Підключитися",
        "already_connected": "Вже підключено!",
        "port_number": "Порт повинен бути числом!",
        "waiting_on": "Очікування підключення на {ip}:{port}…",
        "local_net": "Локальна мережа: {ip}:{port}",
        "enter_ip": "Введіть IP-адресу сервера!",
        "conn_error": "Помилка підключення:\n{e}",
        "connected_to": "Підключено: {addr}",
        "peer_joined": "{name} приєднався",
        "no_conn": "Немає з'єднання — спочатку підключіться",
        "send_error": "Помилка відправки: {e}",
        "disconnected": "Відключено",
        "peer_disconnected": "Співрозмовник відключився",
        "failed_start": "Не вдалося запустити чат:\n{e}",
        "tray_open": "Відкрити",
        "tray_exit": "Вихід",
        "peer_default": "Співрозмовник",
    },
    "de": {
        "section_connection": "VERBINDUNG",
        "btn_create": "⚡  Chat erstellen",
        "btn_connect": "🔗  Verbinden",
        "btn_disconnect": "✕   Trennen",
        "btn_theme": "◑  Design wechseln",
        "btn_tray": "▼  In Tray",
        "lang_label": "🌐 Sprache",
        "status_disconnected": "● Nicht verbunden",
        "status_waiting": "⏳ Warten :{port}",
        "status_connected": "● Verbunden  {addr}",
        "status_broken": "● Verbindung getrennt",
        "chat_title": "Chat",
        "btn_send": "Senden",
        "welcome": "Erstellen Sie einen Chat oder verbinden Sie sich",
        "enter_name": "Geben Sie Ihren Namen ein",
        "btn_enter": "Eintreten",
        "win_create": "Chat erstellen",
        "create_header": "⚡  Chat erstellen",
        "create_desc": "Der andere Teilnehmer muss sich mit Ihrer IP und Ihrem Port verbinden",
        "label_local_ip": "Lok. IP:",
        "label_ext_ip": "Ext. IP:",
        "label_port": "Port:",
        "btn_start": "Chat starten",
        "btn_starting": "Starte…",
        "upnp_trying": "⏳ Versuche UPnP-Portweiterleitung…",
        "upnp_ok": "✔ UPnP: Port {port} automatisch weitergeleitet",
        "upnp_fail": "⚠ UPnP fehlgeschlagen — leiten Sie Port {port} manuell am Router weiter",
        "win_connect": "Verbinden",
        "connect_header": "🔗  Verbinden",
        "connect_desc": "Geben Sie die IP-Adresse und den Port des Servers ein",
        "label_ip": "IP/Host:",
        "btn_do_connect": "Verbinden",
        "already_connected": "Bereits verbunden!",
        "port_number": "Port muss eine Zahl sein!",
        "waiting_on": "Warte auf Verbindung auf {ip}:{port}…",
        "local_net": "Lokales Netzwerk: {ip}:{port}",
        "enter_ip": "Geben Sie die Server-IP-Adresse ein!",
        "conn_error": "Verbindungsfehler:\n{e}",
        "connected_to": "Verbunden: {addr}",
        "peer_joined": "{name} ist beigetreten",
        "no_conn": "Keine Verbindung — zuerst verbinden",
        "send_error": "Sendefehler: {e}",
        "disconnected": "Getrennt",
        "peer_disconnected": "Gesprächspartner getrennt",
        "failed_start": "Chat konnte nicht gestartet werden:\n{e}",
        "tray_open": "Öffnen",
        "tray_exit": "Beenden",
        "peer_default": "Gesprächspartner",
    },
    "fr": {
        "section_connection": "CONNEXION",
        "btn_create": "⚡  Créer un chat",
        "btn_connect": "🔗  Se connecter",
        "btn_disconnect": "✕   Déconnecter",
        "btn_theme": "◑  Changer le thème",
        "btn_tray": "▼  Dans le bac",
        "lang_label": "🌐 Langue",
        "status_disconnected": "● Non connecté",
        "status_waiting": "⏳ En attente :{port}",
        "status_connected": "● Connecté  {addr}",
        "status_broken": "● Connexion perdue",
        "chat_title": "Chat",
        "btn_send": "Envoyer",
        "welcome": "Créez ou rejoignez un chat",
        "enter_name": "Entrez votre nom",
        "btn_enter": "Entrer",
        "win_create": "Créer un chat",
        "create_header": "⚡  Créer un chat",
        "create_desc": "L'autre participant doit se connecter à votre IP et Port",
        "label_local_ip": "IP loc.:",
        "label_ext_ip": "IP ext.:",
        "label_port": "Port:",
        "btn_start": "Démarrer le chat",
        "btn_starting": "Démarrage…",
        "upnp_trying": "⏳ Tentative de redirection UPnP…",
        "upnp_ok": "✔ UPnP: port {port} redirigé automatiquement",
        "upnp_fail": "⚠ UPnP échoué — redirigez le port {port} manuellement sur votre routeur",
        "win_connect": "Se connecter",
        "connect_header": "🔗  Se connecter",
        "connect_desc": "Entrez l'adresse IP et le port du serveur",
        "label_ip": "IP/Hôte:",
        "btn_do_connect": "Connecter",
        "already_connected": "Déjà connecté!",
        "port_number": "Le port doit être un nombre!",
        "waiting_on": "En attente de connexion sur {ip}:{port}…",
        "local_net": "Réseau local: {ip}:{port}",
        "enter_ip": "Entrez l'adresse IP du serveur!",
        "conn_error": "Erreur de connexion:\n{e}",
        "connected_to": "Connecté: {addr}",
        "peer_joined": "{name} a rejoint",
        "no_conn": "Pas de connexion — connectez-vous d'abord",
        "send_error": "Erreur d'envoi: {e}",
        "disconnected": "Déconnecté",
        "peer_disconnected": "L'interlocuteur s'est déconnecté",
        "failed_start": "Impossible de démarrer le chat:\n{e}",
        "tray_open": "Ouvrir",
        "tray_exit": "Quitter",
        "peer_default": "Interlocuteur",
    },
    "es": {
        "section_connection": "CONEXIÓN",
        "btn_create": "⚡  Crear chat",
        "btn_connect": "🔗  Conectar",
        "btn_disconnect": "✕   Desconectar",
        "btn_theme": "◑  Cambiar tema",
        "btn_tray": "▼  Al área notif.",
        "lang_label": "🌐 Idioma",
        "status_disconnected": "● No conectado",
        "status_waiting": "⏳ Esperando :{port}",
        "status_connected": "● Conectado  {addr}",
        "status_broken": "● Conexión perdida",
        "chat_title": "Chat",
        "btn_send": "Enviar",
        "welcome": "Crea o conéctate a un chat",
        "enter_name": "Introduce tu nombre",
        "btn_enter": "Entrar",
        "win_create": "Crear chat",
        "create_header": "⚡  Crear chat",
        "create_desc": "El otro participante debe conectarse a tu IP y Puerto",
        "label_local_ip": "IP loc.:",
        "label_ext_ip": "IP ext.:",
        "label_port": "Puerto:",
        "btn_start": "Iniciar chat",
        "btn_starting": "Iniciando…",
        "upnp_trying": "⏳ Intentando reenvío de puerto UPnP…",
        "upnp_ok": "✔ UPnP: puerto {port} reenviado automáticamente",
        "upnp_fail": "⚠ UPnP falló — reenvíe el puerto {port} manualmente en su router",
        "win_connect": "Conectar",
        "connect_header": "🔗  Conectar",
        "connect_desc": "Introduce la dirección IP y el puerto del servidor",
        "label_ip": "IP/Host:",
        "btn_do_connect": "Conectar",
        "already_connected": "¡Ya conectado!",
        "port_number": "¡El puerto debe ser un número!",
        "waiting_on": "Esperando conexión en {ip}:{port}…",
        "local_net": "Red local: {ip}:{port}",
        "enter_ip": "¡Introduce la dirección IP del servidor!",
        "conn_error": "Error de conexión:\n{e}",
        "connected_to": "Conectado: {addr}",
        "peer_joined": "{name} se unió",
        "no_conn": "Sin conexión — conéctate primero",
        "send_error": "Error de envío: {e}",
        "disconnected": "Desconectado",
        "peer_disconnected": "El interlocutor se desconectó",
        "failed_start": "No se pudo iniciar el chat:\n{e}",
        "tray_open": "Abrir",
        "tray_exit": "Salir",
        "peer_default": "Interlocutor",
    },
    "pl": {
        "section_connection": "POŁĄCZENIE",
        "btn_create": "⚡  Utwórz czat",
        "btn_connect": "🔗  Połącz",
        "btn_disconnect": "✕   Rozłącz",
        "btn_theme": "◑  Zmień motyw",
        "btn_tray": "▼  Do zasobnika",
        "lang_label": "🌐 Język",
        "status_disconnected": "● Nie połączono",
        "status_waiting": "⏳ Oczekiwanie :{port}",
        "status_connected": "● Połączono  {addr}",
        "status_broken": "● Połączenie zerwane",
        "chat_title": "Czat",
        "btn_send": "Wyślij",
        "welcome": "Utwórz lub dołącz do czatu",
        "enter_name": "Wprowadź swoje imię",
        "btn_enter": "Wejdź",
        "win_create": "Utwórz czat",
        "create_header": "⚡  Utwórz czat",
        "create_desc": "Drugi uczestnik musi połączyć się z Twoim IP i Portem",
        "label_local_ip": "Lok. IP:",
        "label_ext_ip": "Zewn. IP:",
        "label_port": "Port:",
        "btn_start": "Uruchom czat",
        "btn_starting": "Uruchamianie…",
        "upnp_trying": "⏳ Próba przekierowania portu UPnP…",
        "upnp_ok": "✔ UPnP: port {port} przekierowany automatycznie",
        "upnp_fail": "⚠ UPnP nie zadziałał — przekieruj port {port} ręcznie na routerze",
        "win_connect": "Połącz",
        "connect_header": "🔗  Połącz",
        "connect_desc": "Wprowadź adres IP i port serwera rozmówcy",
        "label_ip": "IP/Host:",
        "btn_do_connect": "Połącz",
        "already_connected": "Już połączono!",
        "port_number": "Port musi być liczbą!",
        "waiting_on": "Oczekiwanie na połączenie na {ip}:{port}…",
        "local_net": "Sieć lokalna: {ip}:{port}",
        "enter_ip": "Wprowadź adres IP serwera!",
        "conn_error": "Błąd połączenia:\n{e}",
        "connected_to": "Połączono: {addr}",
        "peer_joined": "{name} dołączył",
        "no_conn": "Brak połączenia — najpierw się połącz",
        "send_error": "Błąd wysyłania: {e}",
        "disconnected": "Rozłączono",
        "peer_disconnected": "Rozmówca rozłączył się",
        "failed_start": "Nie udało się uruchomić czatu:\n{e}",
        "tray_open": "Otwórz",
        "tray_exit": "Wyjdź",
        "peer_default": "Rozmówca",
    },
    "pt": {
        "section_connection": "CONEXÃO",
        "btn_create": "⚡  Criar chat",
        "btn_connect": "🔗  Conectar",
        "btn_disconnect": "✕   Desconectar",
        "btn_theme": "◑  Alterar tema",
        "btn_tray": "▼  Para o tray",
        "lang_label": "🌐 Idioma",
        "status_disconnected": "● Não conectado",
        "status_waiting": "⏳ Aguardando :{port}",
        "status_connected": "● Conectado  {addr}",
        "status_broken": "● Conexão perdida",
        "chat_title": "Chat",
        "btn_send": "Enviar",
        "welcome": "Crie ou conecte-se a um chat",
        "enter_name": "Digite seu nome",
        "btn_enter": "Entrar",
        "win_create": "Criar chat",
        "create_header": "⚡  Criar chat",
        "create_desc": "O outro participante deve se conectar ao seu IP e Porta",
        "label_local_ip": "IP loc.:",
        "label_ext_ip": "IP ext.:",
        "label_port": "Porta:",
        "btn_start": "Iniciar chat",
        "btn_starting": "Iniciando…",
        "upnp_trying": "⏳ Tentando redirecionamento UPnP…",
        "upnp_ok": "✔ UPnP: porta {port} redirecionada automaticamente",
        "upnp_fail": "⚠ UPnP falhou — redirecione a porta {port} manualmente no roteador",
        "win_connect": "Conectar",
        "connect_header": "🔗  Conectar",
        "connect_desc": "Digite o endereço IP e a porta do servidor",
        "label_ip": "IP/Host:",
        "btn_do_connect": "Conectar",
        "already_connected": "Já conectado!",
        "port_number": "A porta deve ser um número!",
        "waiting_on": "Aguardando conexão em {ip}:{port}…",
        "local_net": "Rede local: {ip}:{port}",
        "enter_ip": "Digite o endereço IP do servidor!",
        "conn_error": "Erro de conexão:\n{e}",
        "connected_to": "Conectado: {addr}",
        "peer_joined": "{name} entrou",
        "no_conn": "Sem conexão — conecte-se primeiro",
        "send_error": "Erro de envio: {e}",
        "disconnected": "Desconectado",
        "peer_disconnected": "O interlocutor se desconectou",
        "failed_start": "Falha ao iniciar o chat:\n{e}",
        "tray_open": "Abrir",
        "tray_exit": "Sair",
        "peer_default": "Interlocutor",
    },
    "it": {
        "section_connection": "CONNESSIONE",
        "btn_create": "⚡  Crea chat",
        "btn_connect": "🔗  Connetti",
        "btn_disconnect": "✕   Disconnetti",
        "btn_theme": "◑  Cambia tema",
        "btn_tray": "▼  Nel vassoio",
        "lang_label": "🌐 Lingua",
        "status_disconnected": "● Non connesso",
        "status_waiting": "⏳ In attesa :{port}",
        "status_connected": "● Connesso  {addr}",
        "status_broken": "● Connessione persa",
        "chat_title": "Chat",
        "btn_send": "Invia",
        "welcome": "Crea o connettiti a una chat",
        "enter_name": "Inserisci il tuo nome",
        "btn_enter": "Entra",
        "win_create": "Crea chat",
        "create_header": "⚡  Crea chat",
        "create_desc": "L'altro partecipante deve connettersi al tuo IP e Porta",
        "label_local_ip": "IP loc.:",
        "label_ext_ip": "IP est.:",
        "label_port": "Porta:",
        "btn_start": "Avvia chat",
        "btn_starting": "Avvio…",
        "upnp_trying": "⏳ Tentativo di port forwarding UPnP…",
        "upnp_ok": "✔ UPnP: porta {port} inoltrata automaticamente",
        "upnp_fail": "⚠ UPnP non riuscito — inoltra la porta {port} manualmente nel router",
        "win_connect": "Connetti",
        "connect_header": "🔗  Connetti",
        "connect_desc": "Inserisci l'indirizzo IP e la porta del server",
        "label_ip": "IP/Host:",
        "btn_do_connect": "Connetti",
        "already_connected": "Già connesso!",
        "port_number": "La porta deve essere un numero!",
        "waiting_on": "In attesa di connessione su {ip}:{port}…",
        "local_net": "Rete locale: {ip}:{port}",
        "enter_ip": "Inserisci l'indirizzo IP del server!",
        "conn_error": "Errore di connessione:\n{e}",
        "connected_to": "Connesso: {addr}",
        "peer_joined": "{name} si è unito",
        "no_conn": "Nessuna connessione — connettiti prima",
        "send_error": "Errore di invio: {e}",
        "disconnected": "Disconnesso",
        "peer_disconnected": "L'interlocutore si è disconnesso",
        "failed_start": "Impossibile avviare la chat:\n{e}",
        "tray_open": "Apri",
        "tray_exit": "Esci",
        "peer_default": "Interlocutore",
    },
    "zh": {
        "section_connection": "连接",
        "btn_create": "⚡  创建聊天",
        "btn_connect": "🔗  连接",
        "btn_disconnect": "✕   断开连接",
        "btn_theme": "◑  切换主题",
        "btn_tray": "▼  最小化到托盘",
        "lang_label": "🌐 语言",
        "status_disconnected": "● 未连接",
        "status_waiting": "⏳ 等待中 :{port}",
        "status_connected": "● 已连接  {addr}",
        "status_broken": "● 连接断开",
        "chat_title": "聊天",
        "btn_send": "发送",
        "welcome": "创建或加入聊天",
        "enter_name": "输入您的用户名",
        "btn_enter": "进入",
        "win_create": "创建聊天",
        "create_header": "⚡  创建聊天",
        "create_desc": "另一位参与者需要连接到您的IP和端口",
        "label_local_ip": "本地IP:",
        "label_ext_ip": "外部IP:",
        "label_port": "端口:",
        "btn_start": "启动聊天",
        "btn_starting": "启动中…",
        "upnp_trying": "⏳ 尝试UPnP端口映射…",
        "upnp_ok": "✔ UPnP: 端口 {port} 已自动映射",
        "upnp_fail": "⚠ UPnP失败 — 请在路由器上手动映射端口 {port}",
        "win_connect": "连接",
        "connect_header": "🔗  连接",
        "connect_desc": "输入服务器的IP地址和端口",
        "label_ip": "IP/主机:",
        "btn_do_connect": "连接",
        "already_connected": "已经连接！",
        "port_number": "端口必须是数字！",
        "waiting_on": "等待连接到 {ip}:{port}…",
        "local_net": "本地网络: {ip}:{port}",
        "enter_ip": "请输入服务器IP地址！",
        "conn_error": "连接错误:\n{e}",
        "connected_to": "已连接: {addr}",
        "peer_joined": "{name} 加入了",
        "no_conn": "无连接 — 请先连接",
        "send_error": "发送错误: {e}",
        "disconnected": "已断开",
        "peer_disconnected": "对方已断开",
        "failed_start": "无法启动聊天:\n{e}",
        "tray_open": "打开",
        "tray_exit": "退出",
        "peer_default": "对方",
    },
    "ja": {
        "section_connection": "接続",
        "btn_create": "⚡  チャット作成",
        "btn_connect": "🔗  接続",
        "btn_disconnect": "✕   切断",
        "btn_theme": "◑  テーマ切替",
        "btn_tray": "▼  トレイへ",
        "lang_label": "🌐 言語",
        "status_disconnected": "● 未接続",
        "status_waiting": "⏳ 待機中 :{port}",
        "status_connected": "● 接続済  {addr}",
        "status_broken": "● 接続が切断されました",
        "chat_title": "チャット",
        "btn_send": "送信",
        "welcome": "チャットを作成または接続してください",
        "enter_name": "お名前を入力してください",
        "btn_enter": "入室",
        "win_create": "チャット作成",
        "create_header": "⚡  チャット作成",
        "create_desc": "相手はあなたのIPとポートに接続する必要があります",
        "label_local_ip": "ローカルIP:",
        "label_ext_ip": "外部IP:",
        "label_port": "ポート:",
        "btn_start": "チャット開始",
        "btn_starting": "起動中…",
        "upnp_trying": "⏳ UPnPポートマッピングを試みています…",
        "upnp_ok": "✔ UPnP: ポート {port} が自動的にマッピングされました",
        "upnp_fail": "⚠ UPnP失敗 — ルーターでポート {port} を手動で転送してください",
        "win_connect": "接続",
        "connect_header": "🔗  接続",
        "connect_desc": "サーバーのIPアドレスとポートを入力してください",
        "label_ip": "IP/ホスト:",
        "btn_do_connect": "接続",
        "already_connected": "既に接続されています！",
        "port_number": "ポートは数字でなければなりません！",
        "waiting_on": "{ip}:{port} で接続を待機中…",
        "local_net": "ローカルネットワーク: {ip}:{port}",
        "enter_ip": "サーバーのIPアドレスを入力してください！",
        "conn_error": "接続エラー:\n{e}",
        "connected_to": "接続済み: {addr}",
        "peer_joined": "{name} が参加しました",
        "no_conn": "接続なし — まず接続してください",
        "send_error": "送信エラー: {e}",
        "disconnected": "切断されました",
        "peer_disconnected": "相手が切断しました",
        "failed_start": "チャットを開始できませんでした:\n{e}",
        "tray_open": "開く",
        "tray_exit": "終了",
        "peer_default": "相手",
    },
    "ko": {
        "section_connection": "연결",
        "btn_create": "⚡  채팅 만들기",
        "btn_connect": "🔗  연결",
        "btn_disconnect": "✕   연결 끊기",
        "btn_theme": "◑  테마 변경",
        "btn_tray": "▼  트레이로",
        "lang_label": "🌐 언어",
        "status_disconnected": "● 연결 안됨",
        "status_waiting": "⏳ 대기 중 :{port}",
        "status_connected": "● 연결됨  {addr}",
        "status_broken": "● 연결이 끊겼습니다",
        "chat_title": "채팅",
        "btn_send": "전송",
        "welcome": "채팅을 만들거나 연결하세요",
        "enter_name": "이름을 입력하세요",
        "btn_enter": "입장",
        "win_create": "채팅 만들기",
        "create_header": "⚡  채팅 만들기",
        "create_desc": "상대방은 당신의 IP와 포트에 연결해야 합니다",
        "label_local_ip": "로컬 IP:",
        "label_ext_ip": "외부 IP:",
        "label_port": "포트:",
        "btn_start": "채팅 시작",
        "btn_starting": "시작 중…",
        "upnp_trying": "⏳ UPnP 포트 매핑 시도 중…",
        "upnp_ok": "✔ UPnP: 포트 {port} 자동으로 매핑됨",
        "upnp_fail": "⚠ UPnP 실패 — 라우터에서 포트 {port} 를 수동으로 전달하세요",
        "win_connect": "연결",
        "connect_header": "🔗  연결",
        "connect_desc": "서버의 IP 주소와 포트를 입력하세요",
        "label_ip": "IP/호스트:",
        "btn_do_connect": "연결",
        "already_connected": "이미 연결되어 있습니다!",
        "port_number": "포트는 숫자여야 합니다!",
        "waiting_on": "{ip}:{port} 에서 연결 대기 중…",
        "local_net": "로컬 네트워크: {ip}:{port}",
        "enter_ip": "서버 IP 주소를 입력하세요!",
        "conn_error": "연결 오류:\n{e}",
        "connected_to": "연결됨: {addr}",
        "peer_joined": "{name} 이(가) 참가했습니다",
        "no_conn": "연결 없음 — 먼저 연결하세요",
        "send_error": "전송 오류: {e}",
        "disconnected": "연결 끊김",
        "peer_disconnected": "상대방이 연결을 끊었습니다",
        "failed_start": "채팅을 시작할 수 없습니다:\n{e}",
        "tray_open": "열기",
        "tray_exit": "종료",
        "peer_default": "상대방",
    },
}


def timestamp():
    return datetime.datetime.now().strftime("%H:%M")


# ══════════════════════════════════════
#  СОХРАНЕНИЕ / ЗАГРУЗКА
# ══════════════════════════════════════

def load_save():
    cfg = configparser.ConfigParser()
    try:
        cfg.read(SAVE_PATH, encoding="utf-8")
        data = {}
        if cfg.has_section("app"):
            for key, val in cfg.items("app"):
                data[key] = val
        if cfg.has_section("history"):
            raw = cfg.get("history", "chat_history", fallback="[]")
            try:
                data["chat_history"] = json.loads(raw)
            except Exception:
                data["chat_history"] = []
        return data
    except Exception:
        return {}

def write_save(data: dict):
    cfg = configparser.ConfigParser()
    cfg["app"] = {
        k: str(v) for k, v in data.items()
        if k not in ("chat_history", "last_id", "last_port")
    }
    cfg["history"] = {
        "chat_history": json.dumps(data.get("chat_history", []),
                                   ensure_ascii=False)
    }
    try:
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            cfg.write(f)
    except Exception:
        pass


# ══════════════════════════════════════
#  ТРЕЙ
# ══════════════════════════════════════

def _build_tray_icon():
    """Иконка для трея: ico.ico или нарисованная заглушка."""
    from PIL import Image, ImageDraw

    # Пробуем загрузить ico.ico
    try:
        img = Image.open(ICON_PATH).convert("RGBA").resize((64, 64), Image.LANCZOS)
        return img
    except Exception:
        pass

    # Рисуем заглушку — синий квадрат с буквой M
    img = Image.new("RGBA", (64, 64), (50, 50, 120, 255))
    d   = ImageDraw.Draw(img)
    w   = 5
    d.line([(10, 52), (10, 12)], fill=(255, 255, 255, 255), width=w)
    d.line([(10, 12), (32, 36)], fill=(255, 255, 255, 255), width=w)
    d.line([(32, 36), (54, 12)], fill=(255, 255, 255, 255), width=w)
    d.line([(54, 12), (54, 52)], fill=(255, 255, 255, 255), width=w)
    return img


class MessengerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(NAME)
        self.root.minsize(700, 500)
        try:
            self.root.iconbitmap(ICON_PATH)
        except Exception:
            pass

        self.save = load_save()
        self.current_theme = self.save.get("theme", "dark")
        self.current_lang  = self.save.get("lang", "ru")
        self.t = THEMES[self.current_theme]

        geometry = self.save.get("geometry", "900x680")
        self.root.geometry(geometry)
        self.root.bind("<Configure>", self._on_resize)

        saved_name = self.save.get("username", "").strip()
        if saved_name:
            self.username = saved_name
            self.root.deiconify()
        else:
            self.username = self._ask_name_window(saved_name)

        self.mode        = None
        self.conn        = None
        self.server_sock = None
        self.running     = False
        self.chat_log    = []
        self._tray_icon  = None
        self._upnp_port  = None

        self._build_sidebar()
        self._build_chat_header()
        self._build_chat_area()
        self._build_input_bar()

        self._apply_theme()
        self._show_welcome()

        for entry in self.save.get("chat_history", []):
            self._append(entry["sender"], entry["text"],
                         is_me=entry.get("is_me", False))

        self.root.protocol("WM_DELETE_WINDOW", self._quit_app)
        self._setup_tray()

    # ══════════════════════════════════════
    #  ТРЕЙ
    # ══════════════════════════════════════

    def _setup_tray(self):
        """Запускает иконку в системном трее в отдельном потоке."""
        try:
            import pystray
        except ImportError:
            return

        img = _build_tray_icon()
        if img is None:
            return

        menu = pystray.Menu(
            pystray.MenuItem(self._tr("tray_open"), self._show_from_tray, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(self._tr("tray_exit"),   self._quit_app),
        )
        self._tray_icon = pystray.Icon(NAME, img, NAME, menu)
        threading.Thread(target=self._tray_icon.run, daemon=True).start()

    def _hide_to_tray(self):
        """Прячет окно в трей вместо закрытия."""
        self._save_all()
        self.root.withdraw()

    def _show_from_tray(self, icon=None, item=None):
        """Показывает окно из трея."""
        self.root.after(0, self.root.deiconify)
        self.root.after(0, self.root.lift)

    def _quit_app(self, icon=None, item=None):
        """Полный выход из приложения."""
        self._save_all()
        if self._tray_icon:
            try:
                self._tray_icon.stop()
            except Exception:
                pass
        self.root.after(0, self.root.destroy)

    # ══════════════════════════════════════
    #  ВСПЛЫВАЮЩЕЕ УВЕДОМЛЕНИЕ
    # ══════════════════════════════════════

    def _show_toast(self, sender, text):
        """Всплывашка в правом нижнем углу экрана."""
        t = self.t
        toast = tk.Toplevel(self.root)
        toast.overrideredirect(True)          # без рамки и заголовка
        toast.attributes("-topmost", True)
        toast.attributes("-alpha", 0.92)
        toast.configure(bg=t["TOAST_BG"])

        pad = tk.Frame(toast, bg=t["TOAST_BG"], padx=14, pady=10)
        pad.pack(fill="both", expand=True)

        tk.Label(pad, text=f"{NAME}  •  {timestamp()}",
                 bg=t["TOAST_BG"], fg=t["TEXT_DIM"],
                 font=("Courier", 7)).pack(anchor="w")
        tk.Label(pad, text=sender,
                 bg=t["TOAST_BG"], fg=t["ACCENT"],
                 font=("Courier", 9, "bold")).pack(anchor="w")

        preview = text if len(text) <= 60 else text[:57] + "…"
        tk.Label(pad, text=preview,
                 bg=t["TOAST_BG"], fg=t["TOAST_FG"],
                 font=("Courier", 9), wraplength=280,
                 justify="left").pack(anchor="w", pady=(2, 0))

        toast.update_idletasks()
        w = toast.winfo_width()
        h = toast.winfo_height()

        sw = toast.winfo_screenwidth()
        sh = toast.winfo_screenheight()
        x  = sw - w - 20
        y  = sh - h - 60          # чуть выше панели задач

        toast.geometry(f"+{x}+{y}")

        # клик по тосту — открыть окно
        def _on_click(e=None):
            toast.destroy()
            self._show_from_tray()

        for child in (toast, pad) + tuple(pad.winfo_children()):
            try:
                child.bind("<Button-1>", _on_click)
            except Exception:
                pass

        # анимация: появляется снизу
        def _slide_in(step=0):
            target_y = sh - h - 60
            start_y  = sh + 10
            cur_y = int(start_y + (target_y - start_y) * step / 10)
            toast.geometry(f"+{x}+{cur_y}")
            if step < 10:
                toast.after(20, lambda: _slide_in(step + 1))

        _slide_in()

        # автозакрытие через 4 секунды
        toast.after(4000, lambda: toast.destroy() if toast.winfo_exists() else None)

    # ══════════════════════════════════════
    #  СОХРАНЕНИЕ
    # ══════════════════════════════════════

    def _save_all(self):
        self.save["username"]     = self.username
        self.save["theme"]        = self.current_theme
        self.save["lang"]         = self.current_lang
        self.save["geometry"]     = self.root.geometry()
        self.save["chat_history"] = self.chat_log[-200:]
        write_save(self.save)

    def _on_resize(self, event=None):
        if event and event.widget == self.root:
            self.save["geometry"] = self.root.geometry()
            write_save(self.save)

    # ══════════════════════════════════════
    #  ОКНО ВВОДА ИМЕНИ
    # ══════════════════════════════════════

    def _ask_name_window(self, default_name=""):
        t = self.t
        win = tk.Toplevel(self.root)
        win.title(NAME)
        win.geometry("340x220")
        win.resizable(False, False)
        win.configure(bg=t["BG_DARK"])
        self._set_icon(win)
        win.grab_set()
        self.root.withdraw()

        result = {"name": default_name}

        tk.Label(win, text=NAME,
                 bg=t["BG_DARK"], fg=t["ACCENT"],
                 font=("Courier", 20, "bold")).pack(pady=(28, 4))
        tk.Label(win, text=self._tr("enter_name"),
                 bg=t["BG_DARK"], fg=t["TEXT_DIM"],
                 font=("Courier", 9)).pack()
        tk.Frame(win, bg=t["BORDER"], height=1).pack(fill="x", padx=24, pady=16)

        entry_var = tk.StringVar(value=default_name)
        entry = tk.Entry(win, textvariable=entry_var,
                         bg=t["BG_INPUT"], fg=t["TEXT_MAIN"],
                         font=("Courier", 13), bd=0, relief="flat",
                         insertbackground=t["ACCENT"], justify="center")
        entry.pack(fill="x", padx=24, ipady=6)
        entry.focus_set()
        entry.select_range(0, "end")

        tk.Frame(win, bg=t["BORDER"], height=1).pack(fill="x", padx=24, pady=16)

        def _confirm(e=None):
            name = entry_var.get().strip()
            if not name:
                entry.configure(bg="#3a1a1a")
                win.after(600, lambda: entry.configure(bg=t["BG_INPUT"]))
                return
            result["name"] = name
            win.destroy()

        entry.bind("<Return>", _confirm)
        tk.Button(win, text=self._tr("btn_enter"), command=_confirm).pack(pady=4)
        win.protocol("WM_DELETE_WINDOW", lambda: None)
        self.root.wait_window(win)
        self.root.deiconify()
        return result["name"]

    # ══════════════════════════════════════
    #  ЛОКАЛИЗАЦИЯ
    # ══════════════════════════════════════

    def _tr(self, key, **kwargs):
        """Возвращает переведённую строку для текущего языка."""
        lang_dict = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["ru"])
        text = lang_dict.get(key, TRANSLATIONS["ru"].get(key, key))
        return text.format(**kwargs) if kwargs else text

    def _change_lang(self, lang_code):
        """Переключает язык интерфейса."""
        if lang_code not in TRANSLATIONS:
            return
        self.current_lang = lang_code
        self._apply_lang()
        self._save_all()

    def _apply_lang(self):
        """Обновляет все переведённые надписи в интерфейсе."""
        self.lbl_conn_title.configure(text=self._tr("section_connection"))
        self.btn_server.configure(text=self._tr("btn_create"))
        self.btn_client.configure(text=self._tr("btn_connect"))
        self.btn_disc.configure(text=self._tr("btn_disconnect"))
        self.btn_theme_btn.configure(text=self._tr("btn_theme"))
        self.btn_tray_btn.configure(text=self._tr("btn_tray"))
        self.lbl_channel.configure(text=self._tr("chat_title"))
        self.btn_send.configure(text=self._tr("btn_send"))
        # Обновляем статус только если не подключены
        if not self.running:
            self.status_var.set(self._tr("status_disconnected"))
        # Обновляем меню языков
        t = self.t
        self.lang_menu.configure(
            bg=t["BG_INPUT"], fg=t["TEXT_MAIN"],
            activebackground=t["ACCENT"], activeforeground=t["BG_DARK"],
            highlightthickness=0, bd=0, relief="flat",
            font=("Courier", 9)
        )
        self.lang_menu["menu"].configure(
            bg=t["BG_INPUT"], fg=t["TEXT_MAIN"],
            activebackground=t["ACCENT"], activeforeground=t["BG_DARK"],
            font=("Courier", 9)
        )

    # ══════════════════════════════════════
    #  ОКНА / СЕКЦИИ
    # ══════════════════════════════════════

    def _build_sidebar(self):
        self.sidebar = tk.Frame(self.root, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.lbl_logo = tk.Label(self.sidebar, text=NAME,
                                  font=("Courier", 18, "bold"), pady=24)
        self.lbl_logo.pack(fill="x")

        self.lbl_user = tk.Label(self.sidebar, text="▸  " + self.username,
                                  font=("Courier", 11), anchor="w", padx=18)
        self.lbl_user.pack(fill="x", pady=(0, 20))

        self.sep1 = tk.Frame(self.sidebar, height=1)
        self.sep1.pack(fill="x", padx=16, pady=4)

        self.lbl_conn_title = tk.Label(self.sidebar, text=self._tr("section_connection"),
                                        font=("Courier", 8), anchor="w", padx=18)
        self.lbl_conn_title.pack(fill="x", pady=(14, 6))

        self.btn_server = self._make_btn(self.sidebar, self._tr("btn_create"),   self._start_server)
        self.btn_server.pack(fill="x", padx=14, pady=4)

        self.btn_client = self._make_btn(self.sidebar, self._tr("btn_connect"),  self._connect_client)
        self.btn_client.pack(fill="x", padx=14, pady=4)

        self.btn_disc   = self._make_btn(self.sidebar, self._tr("btn_disconnect"),   self._disconnect)
        self.btn_disc.pack(fill="x", padx=14, pady=4)

        self.sep2 = tk.Frame(self.sidebar, height=1)
        self.sep2.pack(fill="x", padx=16, pady=14)

        self.btn_theme_btn  = self._make_btn(self.sidebar, self._tr("btn_theme"),   self._toggle_theme)
        self.btn_theme_btn.pack(fill="x", padx=14, pady=4)

        self.btn_tray_btn   = self._make_btn(self.sidebar, self._tr("btn_tray"),         self._hide_to_tray)
        self.btn_tray_btn.pack(fill="x", padx=14, pady=4)

        # ── Выбор языка ──────────────────────────────────
        self.sep_lang = tk.Frame(self.sidebar, height=1)
        self.sep_lang.pack(fill="x", padx=16, pady=8)

        lang_display_names = list(LANG_NAMES.values())
        self.lang_var = tk.StringVar(value=LANG_NAMES.get(self.current_lang, "Русский"))

        def _on_lang_select(selected_name):
            for code, name in LANG_NAMES.items():
                if name == selected_name:
                    self.lang_var.set(selected_name)
                    self._change_lang(code)
                    break

        self.lang_menu = tk.OptionMenu(self.sidebar, self.lang_var,
                                       *lang_display_names, command=_on_lang_select)
        self.lang_menu.configure(font=("Courier", 9), bd=0, relief="flat",
                                  highlightthickness=0, anchor="w", padx=14)
        self.lang_menu.pack(fill="x", padx=14, pady=4)
        # ─────────────────────────────────────────────────

        self.sep3 = tk.Frame(self.sidebar, height=1)
        self.sep3.pack(fill="x", padx=16, pady=8)

        self.status_var = tk.StringVar(value=self._tr("status_disconnected"))
        self.lbl_status = tk.Label(self.sidebar, textvariable=self.status_var,
                                    font=("Courier", 9), anchor="w",
                                    padx=18, wraplength=190, justify="left")
        self.lbl_status.pack(fill="x", pady=4)

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(side="right", fill="both", expand=True)

    def _build_chat_header(self):
        self.header = tk.Frame(self.main_frame, height=56)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        self.lbl_channel = tk.Label(self.header, text=self._tr("chat_title"),
                                     font=("Courier", 13, "bold"), padx=20)
        self.lbl_channel.pack(side="left", fill="y")

    def _build_chat_area(self):
        self.msg_frame = tk.Frame(self.main_frame)
        self.msg_frame.pack(fill="both", expand=True)

        self.chat_area = tk.Text(self.msg_frame, wrap=tk.WORD, state="disabled",
                                  font=("Courier", 11), bd=0, relief="flat",
                                  padx=20, pady=16)
        self.chat_area.pack(fill="both", expand=True, side="left")

        scrollbar = tk.Scrollbar(self.msg_frame, command=self.chat_area.yview)
        scrollbar.pack(side="right", fill="y")
        self.chat_area.configure(yscrollcommand=scrollbar.set)

        for tag in ("me_name", "other_name", "me_msg", "other_msg", "system", "time"):
            self.chat_area.tag_config(tag)

    def _build_input_bar(self):
        self.input_bar = tk.Frame(self.main_frame, height=60)
        self.input_bar.pack(fill="x", side="bottom")
        self.input_bar.pack_propagate(False)

        self.msg_entry = tk.Entry(self.input_bar, font=("Courier", 12),
                                   bd=0, relief="flat")
        self.msg_entry.pack(side="left", fill="both", expand=True, padx=20, pady=14)
        self.msg_entry.bind("<Return>", self._send_message)

        self.btn_send = tk.Button(self.input_bar, text=self._tr("btn_send"),
                                   command=self._send_message)
        self.btn_send.pack(side="right", padx=(0, 10), pady=14)

    # ══════════════════════════════════════
    #  ТЕМЫ
    # ══════════════════════════════════════

    def _toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.t = THEMES[self.current_theme]
        self._apply_theme()
        self._save_all()

    def _apply_theme(self):
        t = self.t
        self.root.configure(bg=t["BG_DARK"])

        for w in (self.sidebar, self.lbl_logo, self.lbl_user,
                  self.lbl_conn_title, self.lbl_status):
            w.configure(bg=t["BG_PANEL"])
        self.lbl_logo.configure(fg=t["ACCENT"])
        self.lbl_user.configure(fg=t["TEXT_MAIN"])
        self.lbl_conn_title.configure(fg=t["TEXT_DIM"])
        self.lbl_status.configure(fg=t["STATUS_ERR"])
        for sep in (self.sep1, self.sep2, self.sep3, self.sep_lang):
            sep.configure(bg=t["BORDER"])

        # Стиль меню языков
        self.lang_menu.configure(
            bg=t["BG_INPUT"], fg=t["TEXT_MAIN"],
            activebackground=t["ACCENT"], activeforeground=t["BG_DARK"],
            highlightthickness=0, bd=0, relief="flat",
        )
        self.lang_menu["menu"].configure(
            bg=t["BG_INPUT"], fg=t["TEXT_MAIN"],
            activebackground=t["ACCENT"], activeforeground=t["BG_DARK"],
        )

        self.header.configure(bg=t["BG_PANEL"])
        self.lbl_channel.configure(bg=t["BG_PANEL"], fg=t["TEXT_MAIN"])

        self.msg_frame.configure(bg=t["BG_DARK"])
        self.chat_area.configure(bg=t["BG_DARK"], fg=t["TEXT_MAIN"],
                                  selectbackground=t["ACCENT"])
        self.chat_area.tag_config("me_name",    foreground=t["ACCENT"],   font=("Courier", 10, "bold"))
        self.chat_area.tag_config("other_name", foreground=t["ACCENT2"],  font=("Courier", 10, "bold"))
        self.chat_area.tag_config("me_msg",     foreground=t["TEXT_MAIN"],font=("Courier", 11))
        self.chat_area.tag_config("other_msg",  foreground=t["TEXT_MAIN"],font=("Courier", 11))
        self.chat_area.tag_config("system",     foreground=t["TEXT_DIM"], font=("Courier", 9, "italic"))
        self.chat_area.tag_config("time",       foreground=t["TEXT_DIM"], font=("Courier", 8))

        self.input_bar.configure(bg=t["BG_INPUT"])
        self.msg_entry.configure(bg=t["BG_INPUT"], fg=t["TEXT_MAIN"],
                                  insertbackground=t["ACCENT"])
        self.main_frame.configure(bg=t["BG_DARK"])

    # ══════════════════════════════════════
    #  СООБЩЕНИЯ
    # ══════════════════════════════════════

    def _append(self, sender, text, is_me=False):
        self.chat_area.configure(state="normal")
        name_tag = "me_name"  if is_me else "other_name"
        msg_tag  = "me_msg"   if is_me else "other_msg"
        prefix   = "  » "     if is_me else "  « "
        self.chat_area.insert("end", f"\n{prefix}", "time")
        self.chat_area.insert("end", sender, name_tag)
        self.chat_area.insert("end", f"  {timestamp()}\n", "time")
        self.chat_area.insert("end", f"    {text}\n", msg_tag)
        self.chat_area.configure(state="disabled")
        self.chat_area.see("end")

    def _system(self, text):
        self.chat_area.configure(state="normal")
        self.chat_area.insert("end", f"\n  ── {text} ──\n", "system")
        self.chat_area.configure(state="disabled")
        self.chat_area.see("end")

    def _show_welcome(self):
        self._system(self._tr("welcome"))

    # ══════════════════════════════════════
    #  СЕТЬ
    # ══════════════════════════════════════

    def _start_server(self):
        if self.running:
            messagebox.showinfo(NAME, self._tr("already_connected"))
            return
        self._show_create_chat_window()

    def _show_create_chat_window(self):
        t = self.t
        win = tk.Toplevel(self.root)
        win.title(self._tr("win_create"))
        win.geometry("360x320")
        win.resizable(False, False)
        win.configure(bg=t["BG_DARK"])
        self._set_icon(win)
        win.grab_set()

        tk.Label(win, text=self._tr("create_header"),
                 bg=t["BG_DARK"], fg=t["ACCENT"],
                 font=("Courier", 15, "bold")).pack(pady=(24, 4))
        tk.Label(win, text=self._tr("create_desc"),
                 bg=t["BG_DARK"], fg=t["TEXT_DIM"],
                 font=("Courier", 8), wraplength=300).pack()
        tk.Frame(win, bg=t["BORDER"], height=1).pack(fill="x", padx=24, pady=12)

        # Локальный IP
        try:
            _s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            _s.connect(("8.8.8.8", 80))
            local_ip = _s.getsockname()[0]
            _s.close()
        except Exception:
            local_ip = "127.0.0.1"

        row_local = tk.Frame(win, bg=t["BG_DARK"])
        row_local.pack(fill="x", padx=24, pady=2)
        tk.Label(row_local, text=self._tr("label_local_ip"), bg=t["BG_DARK"], fg=t["TEXT_DIM"],
                 font=("Courier", 9), width=8, anchor="w").pack(side="left")
        tk.Label(row_local, text=local_ip,
                 bg=t["BG_INPUT"], fg=t["TEXT_DIM"],
                 font=("Courier", 11), padx=6, pady=4, anchor="w").pack(side="left", fill="x", expand=True)

        # Внешний IP
        row_ext = tk.Frame(win, bg=t["BG_DARK"])
        row_ext.pack(fill="x", padx=24, pady=2)
        tk.Label(row_ext, text=self._tr("label_ext_ip"), bg=t["BG_DARK"], fg=t["TEXT_DIM"],
                 font=("Courier", 9), width=8, anchor="w").pack(side="left")
        ext_ip_var = tk.StringVar(value="…")
        ext_ip_lbl = tk.Label(row_ext, textvariable=ext_ip_var,
                              bg=t["BG_INPUT"], fg=t["ACCENT"],
                              font=("Courier", 11), padx=6, pady=4, anchor="w")
        ext_ip_lbl.pack(side="left", fill="x", expand=True)

        # UPnP статус
        upnp_var = tk.StringVar(value="")
        upnp_lbl = tk.Label(win, textvariable=upnp_var,
                            bg=t["BG_DARK"], fg=t["TEXT_DIM"],
                            font=("Courier", 7), wraplength=310)
        upnp_lbl.pack(padx=24, anchor="w")

        # Порт
        row_port = tk.Frame(win, bg=t["BG_DARK"])
        row_port.pack(fill="x", padx=24, pady=4)
        tk.Label(row_port, text=self._tr("label_port"), bg=t["BG_DARK"], fg=t["TEXT_DIM"],
                 font=("Courier", 9), width=8, anchor="w").pack(side="left")
        port_var  = tk.StringVar(value=str(random.randint(10000, 65000)))
        vcmd_port = win.register(lambda s: s.isdigit() or s == "")
        tk.Entry(row_port, textvariable=port_var,
                 validate="key", validatecommand=(vcmd_port, "%P"),
                 bg=t["BG_INPUT"], fg=t["TEXT_MAIN"],
                 font=("Courier", 11), bd=0, relief="flat",
                 insertbackground=t["ACCENT"]).pack(
            side="left", fill="x", expand=True, ipady=4)
        tk.Button(row_port, text="🎲",
                  command=lambda: port_var.set(str(random.randint(10000, 65000)))
                  ).pack(side="left", padx=(4, 0))

        tk.Frame(win, bg=t["BORDER"], height=1).pack(fill="x", padx=24, pady=12)

        # Фоновая загрузка внешнего IP + UPnP
        self._upnp_port = None
        def _fetch_ext():
            ext = get_external_ip()
            if ext:
                win.after(0, lambda: ext_ip_var.set(ext))
            else:
                win.after(0, lambda: ext_ip_var.set("недоступен"))
        threading.Thread(target=_fetch_ext, daemon=True).start()

        def _launch():
            try:
                port = int(port_var.get().strip())
            except ValueError:
                messagebox.showerror(NAME, self._tr("port_number"), parent=win)
                return

            btn_launch.configure(state="disabled", text=self._tr("btn_starting"))
            upnp_var.set(self._tr("upnp_trying"))

            def _do_launch():
                # Пробуем UPnP
                upnp_ext = upnp_add_port(port)
                if upnp_ext:
                    self._upnp_port = port
                    win.after(0, lambda: ext_ip_var.set(upnp_ext))
                    win.after(0, lambda: upnp_var.set(self._tr("upnp_ok", port=port)))
                else:
                    win.after(0, lambda: upnp_var.set(self._tr("upnp_fail", port=port)))

                win.after(300, _start_server)

            def _start_server():
                win.destroy()
                self.mode = "server"
                self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                try:
                    self.server_sock.bind(("0.0.0.0", port))
                except Exception as e:
                    messagebox.showerror(NAME, self._tr("failed_start", e=e))
                    self.server_sock = None
                    return
                self.server_sock.listen(1)
                display_ip = ext_ip_var.get() if ext_ip_var.get() not in ("…", "недоступен") else local_ip
                self._system(self._tr("waiting_on", ip=display_ip, port=port))
                self._system(self._tr("local_net",  ip=local_ip,   port=port))
                self.status_var.set(self._tr("status_waiting", port=port))
                threading.Thread(target=self._accept, daemon=True).start()

            threading.Thread(target=_do_launch, daemon=True).start()

        btn_launch = tk.Button(win, text=self._tr("btn_start"), command=_launch)
        btn_launch.pack(pady=4)

    def _connect_client(self):
        if self.running:
            messagebox.showinfo(NAME, self._tr("already_connected"))
            return
        self._show_connect_window()

    def _show_connect_window(self):
        t = self.t
        win = tk.Toplevel(self.root)
        win.title(self._tr("win_connect"))
        win.geometry("360x260")
        win.resizable(False, False)
        win.configure(bg=t["BG_DARK"])
        self._set_icon(win)
        win.grab_set()

        tk.Label(win, text=self._tr("connect_header"),
                 bg=t["BG_DARK"], fg=t["ACCENT"],
                 font=("Courier", 15, "bold")).pack(pady=(24, 4))
        tk.Label(win, text=self._tr("connect_desc"),
                 bg=t["BG_DARK"], fg=t["TEXT_DIM"],
                 font=("Courier", 8), wraplength=300).pack()
        tk.Frame(win, bg=t["BORDER"], height=1).pack(fill="x", padx=24, pady=16)

        # IP / хост
        row_id = tk.Frame(win, bg=t["BG_DARK"])
        row_id.pack(fill="x", padx=24, pady=4)
        tk.Label(row_id, text=self._tr("label_ip"), bg=t["BG_DARK"], fg=t["TEXT_DIM"],
                 font=("Courier", 9), width=8, anchor="w").pack(side="left")
        id_var  = tk.StringVar(value="")
        id_entry = tk.Entry(row_id, textvariable=id_var,
                            bg=t["BG_INPUT"], fg=t["TEXT_MAIN"],
                            font=("Courier", 11), bd=0, relief="flat",
                            insertbackground=t["ACCENT"])
        id_entry.pack(side="left", fill="x", expand=True, ipady=4)
        id_entry.focus_set()

        # Порт
        row_port = tk.Frame(win, bg=t["BG_DARK"])
        row_port.pack(fill="x", padx=24, pady=4)
        tk.Label(row_port, text=self._tr("label_port"), bg=t["BG_DARK"], fg=t["TEXT_DIM"],
                 font=("Courier", 9), width=6, anchor="w").pack(side="left")
        port_var  = tk.StringVar(value="")
        vcmd_port = win.register(lambda s: s.isdigit() or s == "")
        tk.Entry(row_port, textvariable=port_var,
                 validate="key", validatecommand=(vcmd_port, "%P"),
                 bg=t["BG_INPUT"], fg=t["TEXT_MAIN"],
                 font=("Courier", 11), bd=0, relief="flat",
                 insertbackground=t["ACCENT"]).pack(
            side="left", fill="x", expand=True, ipady=4)

        tk.Frame(win, bg=t["BORDER"], height=1).pack(fill="x", padx=24, pady=16)

        def _do_connect(e=None):
            host = id_var.get().strip()
            if not host:
                messagebox.showerror(NAME, self._tr("enter_ip"), parent=win)
                return
            try:
                port = int(port_var.get().strip())
            except ValueError:
                messagebox.showerror(NAME, self._tr("port_number"), parent=win)
                return
            win.destroy()
            self.mode = "client"
            try:
                self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.conn.connect((host, port))
                self.running = True
                self.root.after(0, lambda: self._on_connected(host))
                threading.Thread(target=self._receive, daemon=True).start()
            except Exception as ex:
                messagebox.showerror(NAME, self._tr("conn_error", e=ex))

        id_entry.bind("<Return>", _do_connect)
        tk.Button(win, text=self._tr("btn_do_connect"), command=_do_connect).pack(pady=4)

    def _accept(self):
        try:
            self.conn, addr = self.server_sock.accept()
            self.running = True
            self.root.after(0, lambda: self._on_connected(addr[0]))
            threading.Thread(target=self._receive, daemon=True).start()
        except Exception:
            pass

    def _on_connected(self, addr):
        self._system(self._tr("connected_to", addr=addr))
        self.status_var.set(self._tr("status_connected", addr=addr))
        self.lbl_status.configure(fg=self.t["STATUS_OK"])
        try:
            self.conn.send(json.dumps(
                {"type": "hello", "name": self.username}
            ).encode())
        except Exception:
            pass

    def _receive(self):
        self.peer_name = self._tr("peer_default")
        while self.running:
            try:
                data = self.conn.recv(4096)
                if not data:
                    break
                payload = json.loads(data.decode())
                if payload["type"] == "hello":
                    self.peer_name = payload["name"]
                    self.root.after(0, lambda n=payload["name"]:
                                    self._system(self._tr("peer_joined", name=n)))
                elif payload["type"] == "msg":
                    self.root.after(0, lambda p=payload:
                                    self._receive_msg(p["name"], p["text"]))
            except Exception:
                break
        self.root.after(0, self._on_disconnected)

    def _receive_msg(self, name, text):
        self._append(name, text, is_me=False)
        self.chat_log.append({"sender": name, "text": text, "is_me": False})
        self._save_all()
        # показываем тост только если окно свёрнуто/скрыто
        if not self.root.winfo_viewable():
            self._show_toast(name, text)

    def _send_message(self, event=None):
        text = self.msg_entry.get().strip()
        if not text:
            return
        if not self.running:
            self._system(self._tr("no_conn"))
            return
        try:
            self.conn.send(json.dumps(
                {"type": "msg", "name": self.username, "text": text}
            ).encode())
            self._append(self.username, text, is_me=True)
            self.chat_log.append({"sender": self.username, "text": text, "is_me": True})
            self._save_all()
            self.msg_entry.delete(0, "end")
        except Exception as e:
            self._system(self._tr("send_error", e=e))

    def _disconnect(self):
        self.running = False
        for s in (self.conn, self.server_sock):
            if s:
                try:
                    s.close()
                except Exception:
                    pass
        self.conn = self.server_sock = None
        # Убираем UPnP проброс если был
        if getattr(self, "_upnp_port", None):
            threading.Thread(target=upnp_remove_port,
                             args=(self._upnp_port,), daemon=True).start()
            self._upnp_port = None
        self.status_var.set(self._tr("status_disconnected"))
        self.lbl_status.configure(fg=self.t["STATUS_ERR"])
        self._system(self._tr("disconnected"))

    def _on_disconnected(self):
        self.running = False
        self.status_var.set(self._tr("status_broken"))
        self.lbl_status.configure(fg=self.t["STATUS_ERR"])
        self._system(self._tr("peer_disconnected"))

    # ══════════════════════════════════════
    #  ХЕЛПЕРЫ
    # ══════════════════════════════════════

    def _set_icon(self, win):
        """Устанавливает иконку на любое окно Toplevel."""
        try:
            win.iconbitmap(ICON_PATH)
        except Exception:
            pass

    def _make_btn(self, parent, text, cmd, danger=False):
        return tk.Button(parent, text=text, command=cmd)


if __name__ == "__main__":
    root = tk.Tk()
    app = MessengerApp(root)
    try:
        root.iconbitmap(ICON_PATH)
    except Exception:
        pass
    root.mainloop()