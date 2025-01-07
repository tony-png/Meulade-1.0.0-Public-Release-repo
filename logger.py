import languages

default_message_queue  = []

def log_message(message):
    # Translate debug messages
    if message.startswith("[DEBUG]"):
        debug_key = message.lower().replace("[debug] ", "debug_")
        translated_message = get_text(debug_key,)
        if translated_message != debug_key:  # If translation exists
            message = f"[DEBUG] {translated_message}"
    
    default_message_queue.append(message)
    if len(default_message_queue) > 10:
        default_message_queue.pop(0)


def get_text(key):
    """Get translated text for current language"""
    return languages.translations.get('English', languages.translations['English']).get(key, key)