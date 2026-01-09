import re
import unicodedata

def slugify(value):
    """
    Converts to lowercase, removes non-word characters, and converts spaces to hyphens.
    Handles basic ASCII transliteration.
    """
    # Normalize unicode characters and encode/decode to convert to ASCII representation
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    # Remove non-alphanumeric, whitespace, or hyphen characters
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    # Replace whitespace/hyphen sequences with a single hyphen
    value = re.sub(r'[-\s]+', '-', value)
    return value
