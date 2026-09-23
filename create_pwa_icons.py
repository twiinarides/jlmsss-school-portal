"""
create_pwa_icons.py - Generate simple PWA icons if school-badge.png exists
Run: python create_pwa_icons.py
"""
import os
from pathlib import Path

static_dir = Path(__file__).parent / 'static' / 'img'
static_dir.mkdir(parents=True, exist_ok=True)

badge = static_dir / 'school-badge.png'

try:
    from PIL import Image

    if badge.exists():
        # Use existing badge
        img = Image.open(badge).convert('RGBA')
    else:
        # Create simple green square with text
        img = Image.new('RGBA', (512, 512), '#1a6b3a')

    # Create 192x192
    img192 = img.resize((192, 192), Image.LANCZOS)
    img192.save(static_dir / 'icon-192.png')
    print('Created icon-192.png')

    # Create 512x512
    img512 = img.resize((512, 512), Image.LANCZOS)
    img512.save(static_dir / 'icon-512.png')
    print('Created icon-512.png')

    print('PWA icons created successfully!')
except ImportError:
    print('Pillow not available. Creating placeholder icons manually...')
    # Copy school badge if exists, else skip
    if badge.exists():
        import shutil
        shutil.copy(badge, static_dir / 'icon-192.png')
        shutil.copy(badge, static_dir / 'icon-512.png')
        print('Copied school-badge.png as icons.')
    else:
        print('No badge found. PWA will work without icons.')
