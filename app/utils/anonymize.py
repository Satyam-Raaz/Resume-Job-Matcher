import re

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE = re.compile(r"\+?\d[\d\s().-]{8,}\d")


def anonymize(text: str) -> str:
    """Remove contact details. Extend to strip names, gender, age, photos."""
    text = EMAIL.sub("[EMAIL]", text)
    return PHONE.sub("[PHONE]", text)
