import helpers
from django.core.management.base import BaseCommand
from django.conf import settings

STATICFILES_VENDOR_DIR = getattr(settings, "STATICFILES_VENDOR_DIR")

VENDOR_STATICFILES = {
    "saas-theme.min.css":"https://raw.githubusercontent.com/codingforentrepreneurs/SaaS-Foundations/refs/heads/main/src/staticfiles/theme/saas-theme.min.css",
    "flowbite.min.css":"https://cdn.jsdelivr.net/npm/flowbite@4.0.1/dist/flowbite.min.css",
    "flowbite.min.js":"https://cdn.jsdelivr.net/npm/flowbite@4.0.1/dist/flowbite.min.js",
    "flowbite.min.js.map": "https://cdn.jsdelivr.net/npm/flowbite@4.0.1/dist/flowbite.min.js.map"
}

class Command(BaseCommand):
    def handle(self, *args, **options):
        completed_urls = []
        for name , url in VENDOR_STATICFILES.items():
            out_path = STATICFILES_VENDOR_DIR / name
            dl_succes = helpers.download_to_local(url, out_path)
            if dl_succes:
                completed_urls.append(url)
            else:
                self.stdout.write(self.style.ERROR(f"Failed to download {url}"))

        if set(completed_urls) == set(VENDOR_STATICFILES.values()):
            self.stdout.write(self.style.SUCCESS("All files downloaded successfully"))
        else:
            self.stdout.WARNING(self.style.ERROR("Not all files downloaded successfully"))