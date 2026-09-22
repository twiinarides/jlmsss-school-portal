from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from school.models import Gallery, GalleryCategory


class Command(BaseCommand):
    help = "Import images from the project's 'raw media' folder into the Gallery." \

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=50,
            help="Maximum number of images to import.",
        )

    def handle(self, *args, **options):
        limit: int = int(options.get("limit") or 50)

        base_dir = Path(settings.BASE_DIR)
        raw_dir = base_dir / "raw media"

        if not raw_dir.exists() or not raw_dir.is_dir():
            self.stdout.write(self.style.ERROR(f"Raw media folder not found: {raw_dir}"))
            return

        allowed_ext = {".jpg", ".jpeg", ".png", ".webp"}
        excluded_substrings = {
            "badge",
        }

        default_category, _ = GalleryCategory.objects.get_or_create(
            name="General",
            defaults={
                "slug": "general",
                "is_active": True,
            },
        )

        imported = 0
        skipped = 0

        for p in sorted(raw_dir.iterdir()):
            if imported >= limit:
                break

            if not p.is_file():
                continue

            ext = p.suffix.lower()
            if ext not in allowed_ext:
                continue

            name_lower = p.name.lower()
            if any(s in name_lower for s in excluded_substrings):
                skipped += 1
                continue

            title = p.stem.replace("_", " ").strip()

            if Gallery.objects.filter(title__iexact=title).exists():
                skipped += 1
                continue

            g = Gallery(title=title, category_id=default_category.pk)
            g.save()

            with p.open("rb") as f:
                g.image.save(p.name, File(f), save=True)

            imported += 1

        self.stdout.write(self.style.SUCCESS(f"Imported: {imported}"))
        self.stdout.write(self.style.WARNING(f"Skipped: {skipped}"))
