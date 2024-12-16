from playwright.sync_api import sync_playwright
import json
import os
import pygame
import threading
from datetime import datetime
import winsound
import webbrowser
import sys

def get_playwright_path():
    """Get the correct path for Playwright resources when bundled"""
    if getattr(sys, 'frozen', False):
        return {
            'browser_path': sys._MEIPASS  # Just use the base directory
        }
    return None

class AppGUI:
    def __init__(self):
        pygame.init()
        self.width = 500  # More compact width
        self.height = 700  # Increased from 600 to 700 to fit everything
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("RVSQ Appointment Finder")
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (20, 20, 20)
        self.GRAY = (229, 231, 235)
        self.BLUE = (63, 131, 248)
        self.LIGHT_BLUE = (241, 245, 249)
        self.RED = (239, 68, 68)
        self.GREEN = (34, 197, 94)
        self.HOVER_GREEN = (22, 163, 74)
        self.HOVER_RED = (220, 38, 38)
        self.INPUT_BG = (248, 250, 252)  # Slightly off-white for input fields
        self.INPUT_BG_ACTIVE = (255, 255, 255)
        self.INPUT_BORDER = (203, 213, 225)  # Tailwind slate-300
        self.INPUT_BORDER_ACTIVE = self.BLUE
        self.INPUT_SHADOW = (241, 245, 249)  # Tailwind slate-100
        
        # Fonts with better international support
        try:
            # For Latin characters
            self.latin_font = pygame.font.SysFont('segoe ui', 16)
            # For Chinese characters
            self.chinese_font = pygame.font.SysFont('simsun', 16)
            # For Hindi characters - try multiple Hindi fonts
            hindi_fonts = ['nirmala ui', 'mangal', 'aparajita']
            self.hindi_font = None
            for font_name in hindi_fonts:
                try:
                    self.hindi_font = pygame.font.SysFont(font_name, 16)
                    test_text = self.hindi_font.render('हिंदी', True, (0, 0, 0))
                    break
                except:
                    continue
            if not self.hindi_font:
                self.hindi_font = pygame.font.SysFont('arial unicode ms', 16)
            
            self.title_font = self.latin_font
            self.main_font = self.latin_font
            self.log_font = self.latin_font
        except:
            default_font = pygame.font.SysFont('arial unicode ms', 16)
            self.latin_font = default_font
            self.chinese_font = default_font
            self.hindi_font = default_font
            self.title_font = default_font
            self.main_font = default_font
            self.log_font = default_font
        
        # Initialize translations first
        self.translations = {
            'Français': {
                'first_name': 'Prénom',
                'last_name': 'Nom de famille',
                'nam': 'Numéro d\'assurance maladie',
                'card_seq_number': 'Numéro de séquence (deux chiffres sous le nom, ex: 11)',
                'placeholder_first_name': 'Entrez votre prénom',
                'placeholder_last_name': 'Entrez votre nom de famille',
                'placeholder_nam': 'Format: XXXX 0000 0000',
                'placeholder_card_seq': 'Entrez le numéro de séquence',
                'start': 'Démarrer',
                'stop': 'Arrêter',
                'status': 'Statut',
                'ready': 'Prêt à démarrer',
                'running': 'En cours...',
                'stopping': 'Arrêt...',
                'error_fields': 'Erreur: Veuillez remplir tous les champs',
                'app_title': 'Recherche Automatique de rendez-vous',
                'language': 'Langue',
                'footer': 'www.meulade.com - Bien tanné de se faire fourrer.',
                'birth_day': 'Jour de naissance',
                'birth_month': 'Mois de naissance',
                'birth_year': 'Année de naissance',
                'placeholder_birth_day': 'JJ',
                'placeholder_birth_month': 'MM',
                'placeholder_birth_year': 'AAAA',
                'sound_notification_1': "Un son vous avertira quand un rendez-vous aura été trouvé,",
                'sound_notification_2': "allumez vos haut parleurs!",
            },
            'English': {
                'first_name': 'First Name',
                'last_name': 'Last Name',
                'nam': 'Health Insurance Number',
                'card_seq_number': 'Card Sequence (two digits under name, ex: 11)',
                'placeholder_first_name': 'Enter your first name',
                'placeholder_last_name': 'Enter your last name',
                'placeholder_nam': 'Format: XXXX 0000 0000',
                'placeholder_card_seq': 'Enter sequence number',
                'start': 'Start',
                'stop': 'Stop',
                'status': 'Status',
                'ready': 'Ready to start',
                'running': 'Running...',
                'stopping': 'Stopping...',
                'error_fields': 'Error: Please fill in all fields',
                'app_title': 'RVSQ Appointment Finder',
                'language': 'Language',
                'footer': 'www.meulade.com - Fed up with getting screwed over.',
                'birth_day': 'Birth Day',
                'birth_month': 'Birth Month',
                'birth_year': 'Birth Year',
                'placeholder_birth_day': 'DD',
                'placeholder_birth_month': 'MM',
                'placeholder_birth_year': 'YYYY',
                'sound_notification_1': "A sound will alert you when an appointment is found,",
                'sound_notification_2': "turn on your speakers!",
            },
            'Español': {
                'first_name': 'Nombre',
                'last_name': 'Apellido',
                'nam': 'Número de seguro médico',
                'card_seq_number': 'Número de secuencia (dos dígitos debajo del nombre, ej: 11)',
                'placeholder_first_name': 'Ingrese su nombre',
                'placeholder_last_name': 'Ingrese su apellido',
                'placeholder_nam': 'Formato: XXXX 0000 0000',
                'placeholder_card_seq': 'Ingrese el número de secuencia',
                'start': 'Empezar',
                'stop': 'Detener',
                'status': 'Estado',
                'ready': 'Listo para empezar',
                'running': 'En ejecución...',
                'stopping': 'Deteniendo...',
                'error_fields': 'Error: Por favor complete todos los campos',
                'app_title': 'Buscador de Citas RVSQ',
                'language': 'Idioma',
                'footer': 'www.meulade.com - Hartos de que nos tomen el pelo.',
                'birth_day': 'Día de nacimiento',
                'birth_month': 'Mes de nacimiento',
                'birth_year': 'Año de nacimiento',
                'placeholder_birth_day': 'DD',
                'placeholder_birth_month': 'MM',
                'placeholder_birth_year': 'AAAA',
                'sound_notification_1': "¡Un sonido le avisará cuando se encuentre una cita,",
                'sound_notification_2': "encienda sus altavoces!",
            },
            'Italiano': {
                'first_name': 'Nome',
                'last_name': 'Cognome',
                'nam': 'Numero di assicurazione sanitaria',
                'card_seq_number': 'Numero di sequenza (due cifre sotto il nome, es: 11)',
                'placeholder_first_name': 'Inserisci il tuo nome',
                'placeholder_last_name': 'Inserisci il tuo cognome',
                'placeholder_nam': 'Formato: XXXX 0000 0000',
                'placeholder_card_seq': 'Inserisci il numero di sequenza',
                'start': 'Iniziare',
                'stop': 'Arrestare',
                'status': 'Stato',
                'ready': 'Pronto per iniziare',
                'running': 'In esecuzione...',
                'stopping': 'Arrestando...',
                'error_fields': 'Errore: Per favore riempire tutti i campi',
                'app_title': 'Ricerca Appuntamenti RVSQ',
                'language': 'Lingua',
                'footer': 'www.meulade.com - Stufi di essere presi in giro.',
                'birth_day': 'Giorno di nascita',
                'birth_month': 'Mese di nascita',
                'birth_year': 'Anno di nascita',
                'placeholder_birth_day': 'GG',
                'placeholder_birth_month': 'MM',
                'placeholder_birth_year': 'AAAA',
                'sound_notification_1': "Un suono ti avviserà quando viene trovato un appuntamento,",
                'sound_notification_2': "accendi gli altoparlanti!",
            },
            'Kreyòl': {
                'first_name': 'Nonm',
                'last_name': 'Nonm',
                'nam': 'Nonm de sécurité sociale',
                'card_seq_number': 'Nimewo sekans (de chif anba non an, egzanp: 11)',
                'placeholder_first_name': 'Antre ouvè ou nonm',
                'placeholder_last_name': 'Antre ouv nonm',
                'placeholder_nam': 'Format: XXXX 0000 0000',
                'placeholder_card_seq': 'Antre séquence',
                'start': 'Kòmèt',
                'stop': 'Arrest',
                'status': 'Estad',
                'ready': 'Pronto pou kòmèt',
                'running': 'En kouri...',
                'stopping': 'Arrestant...',
                'error_fields': 'Erè: Tanpri plese plè ou tous les champs',
                'app_title': 'Chèchè Randevou RVSQ',
                'language': 'Lang',
                'footer': 'www.meulade.com - Nou bouke ak tout magouy sa yo.',
                'birth_day': 'Jou nesans',
                'birth_month': 'Mwa nesans',
                'birth_year': 'Ane nesans',
                'placeholder_birth_day': 'JJ',
                'placeholder_birth_month': 'MM',
                'placeholder_birth_year': 'AAAA',
                'sound_notification_1': "Yon son pral avèti ou lè nou jwenn yon randevou,",
                'sound_notification_2': "limen bafle ou yo!",
            },
            '中文': {
                'first_name': '名字',
                'last_name': '姓氏',
                'nam': '医疗保险号码',
                'card_seq_number': '卡序列号（姓名下方的两位数字，例：11）',
                'placeholder_first_name': '输入你的名字',
                'placeholder_last_name': '输入你的姓氏',
                'placeholder_nam': '格式：XXXX 0000 0000',
                'placeholder_card_seq': '输入序列号',
                'start': '开始',
                'stop': '停止',
                'status': '状态',
                'ready': '准备开始',
                'running': '运行中...',
                'stopping': '停止中...',
                'error_fields': '错误：请填写所有字段',
                'app_title': 'RVSQ 预约查找器',
                'language': '语言',
                'footer': 'www.meulade.com - 受够了被欺骗。',
                'birth_day': '出生日',
                'birth_month': '出生月',
                'birth_year': '出生年',
                'placeholder_birth_day': '日',
                'placeholder_birth_month': '月',
                'placeholder_birth_year': '年',
                'sound_notification_1': "找到预约时会有声音提醒，",
                'sound_notification_2': "请打开扬声器！",
            },
            'हिंदी': {
                'first_name': 'नाम',
                'last_name': 'उपनाम',
                'nam': 'आवेदन ंख्या',
                'card_seq_number': 'कार्ड क्रम संख्या (नाम के नीचे दो अं���, उदा: 11)',
                'placeholder_first_name': 'अपना नाम दर्ज करें',
                'placeholder_last_name': 'अपना उपनाम दर्ज करें',
                'placeholder_nam': 'फॉर्मेट: XXXX 0000 0000',
                'placeholder_card_seq': 'क्रमांक दर्ज करें',
                'start': 'सुरु करें',
                'stop': 'रोकें',
                'status': 'सथिति',
                'ready': 'सुरु करने के लिए 準備',
                'running': 'चल रहा है...',
                'stopping': 'रोक रहा है...',
                'error_fields': 'त्रुटि: सभी फ़ील्ड भरें',
                'app_title': 'RVSQ दपॉइंटमेंट फाइंडर',
                'language': 'भाषा',
                'footer': 'www.meulade.com - परेशान हो गए हैं इस धोखाधड़ी से।',
                'birth_day': 'दन्म दिन',
                'birth_month': 'जन्म महीना',
                'birth_year': 'जन्म वर्ष',
                'placeholder_birth_day': 'दिन',
                'placeholder_birth_month': 'महीना',
                'placeholder_birth_year': 'वर्ष',
                'sound_notification_1': "जब अपॉइंटमेंट मिल जाएगा तो एक आवाज़ आपको सूचित करेगी,",
                'sound_notification_2': "अपने स्पीकर चालू करें!",
            }
            # Add other languages here...
        }
        
        # Language setup
        self.languages = ['Français', 'English', 'Español', 'Italiano', 'Kreyòl', '中文', 'हिंदी']
        self.current_language = 'Français'
        self.language_dropdown_open = False
        
        # Language button - wider to accommodate all languages and moved to top-right
        button_width = 100
        self.language_button = pygame.Rect(self.width - button_width - 20, 15, button_width, 30)
        
        # Dropdown positioned to the left of the button
        dropdown_width = 120
        self.dropdown_rect = pygame.Rect(
            self.language_button.x - (dropdown_width - button_width),  # Align right edge with button
            self.language_button.bottom,
            dropdown_width,
            len(self.languages) * 25
        )
        
        # Layout calculations - adjust spacing for logo
        self.field_width = 400
        self.field_height = 40
        start_y = 250  # Position for first input field
        spacing = 55  # Spacing between fields
        self.center_x = (self.width - self.field_width) // 2
        
        # Load logo
        try:
            # Get the correct path whether running as script or executable
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                base_path = sys._MEIPASS
            else:
                # Running as script
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            logo_path = os.path.join(base_path, 'images', 'logo_small.png')
            self.logo = pygame.image.load(logo_path)
            self.logo_rect = self.logo.get_rect()
            self.logo_rect.centerx = self.width // 2
            self.logo_rect.y = 70  # Moved down to make room for title
        except Exception as e:
            self.logo = None
            print(f"Warning: Could not load logo image: {str(e)}")
        
        # Input fields
        self.fields = {
            'first_name': {
                'text': '',
                'rect': pygame.Rect(self.center_x, start_y, self.field_width, self.field_height),
                'label': self.get_text('first_name'),
                'placeholder': self.get_text('placeholder_first_name')
            },
            'last_name': {
                'text': '',
                'rect': pygame.Rect(self.center_x, start_y + spacing, self.field_width, self.field_height),
                'label': self.get_text('last_name'),
                'placeholder': self.get_text('placeholder_last_name')
            },
            'nam': {
                'text': '',
                'rect': pygame.Rect(self.center_x, start_y + spacing*2, self.field_width, self.field_height),
                'label': self.get_text('nam'),
                'placeholder': self.get_text('placeholder_nam')
            },
            'card_seq_number': {
                'text': '',
                'rect': pygame.Rect(self.center_x, start_y + spacing*3, self.field_width, self.field_height),
                'label': self.get_text('card_seq_number'),
                'placeholder': self.get_text('placeholder_card_seq')
            },
            'birth_day': {
                'text': '',
                'rect': pygame.Rect(self.center_x, start_y + spacing*4, self.field_width//3 - 10, self.field_height),
                'label': self.get_text('birth_day'),
                'placeholder': self.get_text('placeholder_birth_day')
            },
            'birth_month': {
                'text': '',
                'rect': pygame.Rect(self.center_x + self.field_width//3, start_y + spacing*4, self.field_width//3 - 10, self.field_height),
                'label': self.get_text('birth_month'),
                'placeholder': self.get_text('placeholder_birth_month')
            },
            'birth_year': {
                'text': '',
                'rect': pygame.Rect(self.center_x + 2*(self.field_width//3), start_y + spacing*4, self.field_width//3, self.field_height),
                'label': self.get_text('birth_year'),
                'placeholder': self.get_text('placeholder_birth_year')
            }
        }
        
        # Buttons
        button_width = 100
        button_height = 35
        button_spacing = 10
        buttons_y = start_y + spacing*5 + 10  # Adjusted for new fields
        
        # Center buttons
        total_buttons_width = (button_width * 2) + button_spacing
        buttons_start_x = (self.width - total_buttons_width) // 2
        
        self.start_button = pygame.Rect(buttons_start_x, buttons_y, button_width, button_height)
        self.stop_button = pygame.Rect(buttons_start_x + button_width + button_spacing, 
                                     buttons_y, button_width, button_height)
        
        # Log area
        log_y = buttons_y + button_height + 20
        self.log_rect = pygame.Rect(self.center_x, log_y, self.field_width, 150)
        
        # Cursor blink timer
        self.cursor_visible = True
        self.cursor_timer = 0
        self.CURSOR_BLINK_TIME = 530  # milliseconds
        
        # Status and logging with better positioning
        self.status = "Ready to start"
        self.log_messages = []
        
        self.active_field = None
        self.running = True
        self.search_running = False
        
        # Load saved config
        self.load_saved_config()
        
        # Add URL rect for click detection
        self.url = "www.meulade.com"
        self.url_rect = None  # Will be set in draw method
        
        # Add URL color and hover color
        self.URL_COLOR = (63, 131, 248)  # Same as self.BLUE
        self.URL_HOVER_COLOR = (29, 78, 216)  # Darker blue for hover

    def load_saved_config(self):
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                personal_info = config['personal_info']
                for field in self.fields:
                    self.fields[field]['text'] = personal_info.get(field, '')
        except FileNotFoundError:
            pass

    def save_config(self):
        config = {
            "personal_info": {
                field: self.fields[field]['text']
                for field in self.fields
            }
        }
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)

    def log_message(self, message):
        # Translate debug messages
        if message.startswith("[DEBUG]"):
            debug_key = message.lower().replace("[debug] ", "debug_")
            translated_message = self.get_text(debug_key)
            if translated_message != debug_key:  # If translation exists
                message = f"[DEBUG] {translated_message}"
        
        self.log_messages.append(message)
        if len(self.log_messages) > 10:
            self.log_messages.pop(0)

    def get_text(self, key):
        """Get translated text for current language"""
        return self.translations.get(self.current_language, self.translations['English']).get(key, key)

    def render_text(self, text, color, font_size=16):
        """Render text with appropriate font based on content"""
        try:
            if any('\u0900' <= char <= '\u097f' for char in text):  # Hindi characters
                font = pygame.font.SysFont('nirmala ui', font_size)
            elif any('\u4e00' <= char <= '\u9fff' for char in text):  # Chinese characters
                font = pygame.font.SysFont('simsun', font_size)
            else:
                font = pygame.font.SysFont('segoe ui', font_size)
            
            return font.render(text, True, color)
        except:
            # Fallback to arial unicode ms if specific font fails
            fallback_font = pygame.font.SysFont('arial unicode ms', font_size)
            return fallback_font.render(text, True, color)

    def draw(self):
        # Fill background
        self.screen.fill(self.WHITE)
        
        # Draw title first
        title = self.render_text(self.get_text('app_title'), self.BLACK, 24)
        title_rect = title.get_rect(centerx=self.width//2, y=30)  # Fixed position at top
        self.screen.blit(title, title_rect)
        
        # Draw logo if available
        if self.logo:
            self.screen.blit(self.logo, self.logo_rect)
        
        # Draw input fields with enhanced styling
        for field_name, field in self.fields.items():
            # Draw label
            label = self.render_text(field['label'], self.BLACK)
            self.screen.blit(label, (field['rect'].x, field['rect'].y - 22))
            
            # Draw input box shadow
            shadow_rect = field['rect'].inflate(2, 2)
            pygame.draw.rect(self.screen, self.INPUT_SHADOW, shadow_rect, border_radius=6)
            
            # Draw input box background
            if self.active_field == field_name:
                # Active field styling
                bg_color = self.INPUT_BG_ACTIVE
                border_color = self.INPUT_BORDER_ACTIVE
                # Add glow effect
                glow_rect = field['rect'].inflate(4, 4)
                pygame.draw.rect(self.screen, self.LIGHT_BLUE, glow_rect, border_radius=6)
            else:
                # Inactive field styling
                bg_color = self.INPUT_BG
                border_color = self.INPUT_BORDER
            
            # Draw main input box
            pygame.draw.rect(self.screen, bg_color, field['rect'], border_radius=6)
            pygame.draw.rect(self.screen, border_color, field['rect'], 2, border_radius=6)
            
            # Draw text or placeholder with better positioning
            if field['text']:
                text_surface = self.render_text(field['text'], self.BLACK)
            else:
                text_surface = self.render_text(field['placeholder'], self.GRAY)
            
            text_y = field['rect'].y + (field['rect'].height - text_surface.get_height())//2
            self.screen.blit(text_surface, (field['rect'].x + 12, text_y))  # Slightly more padding
            
            # Draw cursor with better positioning
            if self.active_field == field_name and self.cursor_visible:
                text_width = self.render_text(field['text'], self.BLACK).get_width()
                cursor_x = field['rect'].x + 12 + text_width
                cursor_y = field['rect'].y + 8
                pygame.draw.line(self.screen, self.BLACK,
                               (cursor_x, cursor_y),
                               (cursor_x, cursor_y + field['rect'].height - 16),
                               2)  # Slightly thicker cursor
        
        # Draw buttons with updated styling
        button_y = self.fields['birth_year']['rect'].bottom + 30
        for button, text in [(self.start_button, self.get_text('start')), 
                           (self.stop_button, self.get_text('stop'))]:
            is_start = button == self.start_button
            is_enabled = (is_start and not self.search_running) or (not is_start and self.search_running)
            is_hovered = button.collidepoint(pygame.mouse.get_pos())
            
            if is_enabled:
                if is_start:
                    color = self.HOVER_GREEN if is_hovered else self.GREEN
                else:
                    color = self.HOVER_RED if is_hovered else self.RED
            else:
                color = self.GRAY
            
            # Draw button with slight shadow
            shadow_rect = button.inflate(2, 2)
            pygame.draw.rect(self.screen, self.GRAY, shadow_rect, border_radius=6)
            pygame.draw.rect(self.screen, color, button, border_radius=6)
            
            text_surface = self.render_text(text, self.WHITE)
            text_rect = text_surface.get_rect(center=button.center)
            self.screen.blit(text_surface, text_rect)
        
        # Add notification text under buttons with more space - split into two lines
        notification_text1 = self.render_text(self.get_text('sound_notification_1'), self.BLACK)
        notification_text2 = self.render_text(self.get_text('sound_notification_2'), self.BLACK)
        notification_rect1 = notification_text1.get_rect(centerx=self.width//2, y=button_y + 50)
        notification_rect2 = notification_text2.get_rect(centerx=self.width//2, y=button_y + 70)
        self.screen.blit(notification_text1, notification_rect1)
        self.screen.blit(notification_text2, notification_rect2)
        
        # Draw log area with more space below notification (adjusted for two lines)
        log_y = notification_rect2.bottom + 20  # Changed from notification_rect to notification_rect2
        self.log_rect = pygame.Rect(self.center_x, log_y, self.field_width, 80)
        pygame.draw.rect(self.screen, self.LIGHT_BLUE, self.log_rect, border_radius=6)
        pygame.draw.rect(self.screen, self.GRAY, self.log_rect, 1, border_radius=6)
        
        # Draw log messages with subtle alternating backgrounds
        for i, message in enumerate(self.log_messages[-8:]):  # Show only last 8 messages
            y_pos = self.log_rect.y + 5 + i*20
            if i % 2 == 0:
                row_rect = pygame.Rect(self.log_rect.x + 2, y_pos, self.log_rect.width - 4, 20)
                pygame.draw.rect(self.screen, self.WHITE, row_rect)
            log_text = self.render_text(message, self.BLACK)
            self.screen.blit(log_text, (self.log_rect.x + 10, y_pos))
        
        # Draw footer with more space
        footer_y = self.height - 40  # Give more space from bottom
        url_text = self.render_text(self.url, self.URL_COLOR if not self.url_rect or not self.url_rect.collidepoint(pygame.mouse.get_pos()) else self.URL_HOVER_COLOR)
        footer_suffix = self.render_text(" - " + self.get_text('footer').split(' - ')[1], self.BLACK)
        
        total_width = url_text.get_width() + footer_suffix.get_width()
        start_x = (self.width - total_width) // 2
        
        # Draw URL with underline
        url_y = footer_y
        self.screen.blit(url_text, (start_x, url_y))
        self.url_rect = pygame.Rect(start_x, url_y, url_text.get_width(), url_text.get_height())
        
        # Draw underline and footer text
        if self.url_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.line(self.screen, self.URL_HOVER_COLOR,
                           (self.url_rect.left, self.url_rect.bottom),
                           (self.url_rect.right, self.url_rect.bottom),
                           2)
        else:
            pygame.draw.line(self.screen, self.URL_COLOR,
                           (self.url_rect.left, self.url_rect.bottom),
                           (self.url_rect.right, self.url_rect.bottom),
                           1)
        
        self.screen.blit(footer_suffix, (start_x + url_text.get_width(), url_y))
        
        # Draw language selector and dropdown LAST to appear on top
        # Language button
        pygame.draw.rect(self.screen, self.BLUE, self.language_button, border_radius=6)
        lang_text = self.render_text(self.current_language, self.WHITE)
        text_rect = lang_text.get_rect()
        text_x = self.language_button.centerx - text_rect.width // 2
        text_y = self.language_button.centery - text_rect.height // 2
        self.screen.blit(lang_text, (text_x, text_y))
        
        # Draw dropdown if open (on top of everything)
        if self.language_dropdown_open:
            # Add semi-transparent overlay behind dropdown
            overlay = pygame.Surface((self.width, self.height))
            overlay.fill(self.WHITE)
            overlay.set_alpha(128)
            self.screen.blit(overlay, (0, 0))
            
            # Draw dropdown background with shadow
            shadow_rect = self.dropdown_rect.inflate(4, 4)
            pygame.draw.rect(self.screen, (0, 0, 0, 30), shadow_rect, border_radius=6)  # Shadow
            pygame.draw.rect(self.screen, self.WHITE, self.dropdown_rect, border_radius=6)  # Background
            pygame.draw.rect(self.screen, self.GRAY, self.dropdown_rect, 1, border_radius=6)  # Border
            
            # Draw language options
            for i, lang in enumerate(self.languages):
                option_rect = pygame.Rect(
                    self.dropdown_rect.x,
                    self.dropdown_rect.y + i * 25,
                    self.dropdown_rect.width,
                    25
                )
                
                # Draw option background
                if option_rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(self.screen, self.LIGHT_BLUE, option_rect, border_radius=3)
                elif lang == self.current_language:
                    pygame.draw.rect(self.screen, (245, 247, 250), option_rect, border_radius=3)
                
                # Draw language text
                lang_text = self.render_text(lang, self.BLACK)
                text_y = option_rect.y + (option_rect.height - lang_text.get_height()) // 2
                self.screen.blit(lang_text, (option_rect.x + 8, text_y))
        
        pygame.display.flip()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Handle URL click
            if self.url_rect and self.url_rect.collidepoint(event.pos):
                webbrowser.open(f"https://{self.url}")
            
            # Handle language selector
            if self.language_button.collidepoint(event.pos):
                self.language_dropdown_open = not self.language_dropdown_open
            elif self.language_dropdown_open:
                # Calculate rectangles for each language option
                for i, lang in enumerate(self.languages):
                    lang_rect = pygame.Rect(
                        self.dropdown_rect.x,
                        self.dropdown_rect.y + i * 25,  # 25 pixels height per option
                        self.dropdown_rect.width,
                        25
                    )
                    if lang_rect.collidepoint(event.pos):
                        self.current_language = lang
                        self.language_dropdown_open = False
                        self.update_language()  # Update all text when language changes
                        break
                else:
                    # Click outside dropdown closes it
                    self.language_dropdown_open = False
            
            # Handle input field selection
            for field_name, field in self.fields.items():
                if field['rect'].collidepoint(event.pos):
                    self.active_field = field_name
                    break
            else:
                self.active_field = None
            
            # Handle button clicks
            if self.start_button.collidepoint(event.pos) and not self.search_running:
                self.start_search()
            elif self.stop_button.collidepoint(event.pos) and self.search_running:
                self.stop_search()
        
        elif event.type == pygame.KEYDOWN:
            if self.active_field:
                if event.key == pygame.K_BACKSPACE:
                    self.fields[self.active_field]['text'] = self.fields[self.active_field]['text'][:-1]
                else:
                    self.fields[self.active_field]['text'] += event.unicode

    def start_search(self):
        if not all(self.fields[field]['text'] for field in self.fields):
            self.status = "Error: Please fill in all fields"
            return
        
        self.save_config()
        self.search_running = True
        self.status = "Running..."
        
        # Start the search in a separate thread
        self.search_thread = threading.Thread(target=self.run_search)
        self.search_thread.daemon = True
        self.search_thread.start()

    def stop_search(self):
        self.search_running = False
        self.status = "Stopping..."

    def run_search(self):
        config = {
            "personal_info": {
                field: self.fields[field]['text']
                for field in self.fields
            }
        }
        
        try:
            self.run_browser_automation(config)
        except Exception as e:
            self.log_message(f"Error: {str(e)}")
        finally:
            self.search_running = False
            self.status = "Ready to start"

    def run_browser_automation(self, config):
        # Create screenshots directories
        for directory in ["screenshots", "error_screenshots"]:
            if not os.path.exists(directory):
                os.makedirs(directory)
        
        with sync_playwright() as p:
            browser = None
            context = None
            try:
                self.log_message("[DEBUG] Starting browser automation...")
                
                # Simplified path handling
                playwright_paths = get_playwright_path()
                launch_args = {
                    'headless': False,
                    'args': ['--disable-redirect-limits']
                }
                
                if playwright_paths:
                    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = playwright_paths['browser_path']
                
                browser = p.chromium.launch(**launch_args)
                
                self.log_message("[DEBUG] Creating new context...")
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
                )
                page = context.new_page()
                
                self.log_message("[DEBUG] Navigating to form page...")
                page.goto(
                    'https://rvsq.gouv.qc.ca/prendrerendezvous/Principale.aspx',
                    timeout=60000,
                    wait_until='networkidle'
                )
                
                self.log_message("[DEBUG] Accepting cookies...")
                page.locator('#btnToutAccepter').click()
                
                self.log_message("[DEBUG] Filling form fields...")
                personal_info = config['personal_info']
                page.fill('#ctl00_ContentPlaceHolderMP_AssureForm_FirstName', personal_info['first_name'])
                page.fill('#ctl00_ContentPlaceHolderMP_AssureForm_LastName', personal_info['last_name'])
                page.fill('#ctl00_ContentPlaceHolderMP_AssureForm_NAM', personal_info['nam'])
                page.fill('#ctl00_ContentPlaceHolderMP_AssureForm_CardSeqNumber', personal_info['card_seq_number'])
                
                # Fill birth date fields
                page.fill('#ctl00_ContentPlaceHolderMP_AssureForm_Day', personal_info['birth_day'])
                page.select_option('#ctl00_ContentPlaceHolderMP_AssureForm_Month', personal_info['birth_month'])
                page.fill('#ctl00_ContentPlaceHolderMP_AssureForm_Year', personal_info['birth_year'])
                
                self.log_message("[DEBUG] Checking consent checkbox...")
                page.check('#AssureForm_CSTMT')
                
                self.log_message("[DEBUG] Waiting for Continue button...")
                page.wait_for_selector('#ctl00_ContentPlaceHolderMP_myButton:not([disabled])')
                
                self.log_message("[DEBUG] Clicking Continue button...")
                page.click('#ctl00_ContentPlaceHolderMP_myButton')
                
                self.log_message("[DEBUG] Waiting for navigation...")
                page.wait_for_load_state('networkidle')
                
                self.log_message("[DEBUG] Checking if user has a family doctor...")
                
                # Wait a moment for the page to load
                page.wait_for_load_state('networkidle')
                page.wait_for_timeout(2000)
                
                # Check for family doctor
                has_family_doctor = page.locator("a.h-SelectAssureBtn.ctx-changer[data-type='1']").is_visible()
                no_family_doctor = page.locator("text=pas de médecin de famille").is_visible()
                
                if no_family_doctor:
                    self.log_message("[DEBUG] No family doctor detected, proceeding with appointment search...")
                    self.log_message("[DEBUG] Clicking proximity button for no family doctor case...")
                    page.click("a.h-SelectAssureBtn.ctx-changer[data-type='3']")
                elif has_family_doctor:
                    self.log_message("[DEBUG] Family doctor detected, proceeding with appointment search...")
                    page.click("a.h-SelectAssureBtn.ctx-changer[data-type='1']")
                else:
                    self.log_message("[DEBUG] Could not determine family doctor status")
                    return
                
                self.log_message("[DEBUG] Waiting for dropdown...")
                page.wait_for_selector('#consultingReason', state='visible', timeout=60000)
                page.wait_for_timeout(2000)
                
                self.log_message("[DEBUG] Selecting 'Consultation Urgente'...")
                page.click('#consultingReason')
                page.select_option('#consultingReason', 'ac2a5fa4-8514-11ef-a759-005056b11d6c')
                
                if not has_family_doctor:
                    self.log_message("[DEBUG] Setting 50km radius...")
                    page.wait_for_selector('#perimeterCombo', state='visible')
                    page.wait_for_timeout(1000)
                
                self.log_message("[DEBUG] Clicking 'Rechercher' button...")
                page.click('button:has-text("Rechercher")')
                page.wait_for_load_state('networkidle')
                
                if has_family_doctor:
                    self.log_message("[DEBUG] Clicking GMF button...")
                    page.click('div.thumbnail.tmbArrow.tmbBtn.h-butType2dot2:has-text("Prendre rendez-vous avec un professionnel de la santé de mon groupe de médecine de famille (GMF)")')
                    
                    self.log_message("[DEBUG] Clicking 'Rechercher' again...")
                    page.click('button:has-text("Rechercher")')
                    page.wait_for_load_state('networkidle')
                    page.click('div.thumbnail.tmbArrow.tmbBtn.h-butType3:has-text("Prendre rendez-vous dans une clinique à proximité")')
                
                elif not has_family_doctor:
                    page.wait_for_load_state('networkidle')
                
                    self.log_message("[DEBUG] Clicking 'Rechercher' again...")
                    page.click('button:has-text("Rechercher")')
                    page.wait_for_load_state('networkidle')
                
                
                
                try:
                    page.select_option('#perimeterCombo', '4')
                except:
                    try:
                        page.click('#perimeterCombo')
                        page.select_option('#perimeterCombo', value='4')
                    except:
                        page.evaluate('document.getElementById("perimeterCombo").value = "4"')

                while self.search_running:  # Check if we should continue running
                    try:
                        self.log_message("[DEBUG] Searching for slots...")
                        page.click('button.h-SearchButton.btn.btn-primary:has-text("Rechercher")')
                        page.wait_for_load_state('networkidle')
                        page.wait_for_timeout(2000)
                        
                        no_slots_element = page.locator('#clinicsWithNoDisponibilities')
                        no_slots_text = page.locator('text=Aucun rendez-vous rpondant')
                        no_slots_full_text = page.locator('text=Aucun rendez-vous répondant à vos critères de recherche n\'est disponible pour le moment.')
                        clinic_section = page.locator('text=Les cliniques suivantes offrent des disponibilités pour votre rendez-vous :')
                        
                        has_negative_indicators = (
                            no_slots_text.is_visible() or 
                            no_slots_element.is_visible() or
                            no_slots_full_text.is_visible()
                        )
                        
                        if has_negative_indicators:
                            self.log_message("[DEBUG] No slots available")
                        elif clinic_section.is_visible():
                            self.log_message("🎉 SLOT FOUND! 🎉")
                            winsound.Beep(1000, 500)
                            winsound.Beep(2000, 500)
                            
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            screenshot_path = os.path.join("screenshots", f"slot_found_{timestamp}.png")
                            page.screenshot(path=screenshot_path, full_page=True)
                            self.log_message(f"Screenshot saved: {screenshot_path}")
                        
                        if not self.search_running:
                            break
                            
                        page.wait_for_timeout(5000)
                        
                    except Exception as e:
                        self.log_message(f"Error during search: {str(e)}")
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        error_path = os.path.join("error_screenshots", f"error_{timestamp}.png")
                        page.screenshot(path=error_path, full_page=True)
                        break
                    
            except Exception as e:
                self.log_message(f"\n[ERROR] An error occurred: {str(e)}")
                if page:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    error_path = os.path.join("error_screenshots", f"error_{timestamp}.png")
                    page.screenshot(path=error_path, full_page=True)
            finally:
                if context:
                    context.close()
                if browser:
                    browser.close()

    def update(self):
        # Update cursor blink
        current_time = pygame.time.get_ticks()
        if current_time - self.cursor_timer > self.CURSOR_BLINK_TIME:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = current_time

    def update_language(self):
        """Update all text elements when language changes"""
        for field_name in self.fields:
            self.fields[field_name]['label'] = self.get_text(field_name)
            self.fields[field_name]['placeholder'] = self.get_text(f'placeholder_{field_name}')
        self.status = self.get_text('ready')

def main():
    app = AppGUI()
    clock = pygame.time.Clock()
    
    while app.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                app.running = False
            app.handle_event(event)
        
        app.update()  # Add this line to update cursor blink
        app.draw()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
