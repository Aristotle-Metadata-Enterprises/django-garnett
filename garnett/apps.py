from django.apps import AppConfig


class AppConfig(AppConfig):
    name = "garnett"

    def ready(self):
        from django.conf import settings

        if getattr(settings, "GARNETT_PATCH_REVERSION", False):
            from garnett.reversion import patch_compare

            patch_compare()
