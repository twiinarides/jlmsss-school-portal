import re

with open('school_website/settings.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_tweaks = """JAZZMIN_UI_TWEAKS = {
    "theme": "lumen",
    "dark_mode_theme": None,
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "sidebar": "sidebar-dark-success",
    "sidebar_fixed": True,
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,
    "accent": "accent-success",
    "brand_small_text": False,
    "brand_colour": "navbar-success",
    "footer_small_text": False,
    "actions_sticky_top": True,
}"""

content = re.sub(r'JAZZMIN_UI_TWEAKS\s*=\s*\{.*?\}(?=\n\n# =)', new_tweaks, content, flags=re.DOTALL)

with open('school_website/settings.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Updated JAZZMIN_UI_TWEAKS.')
