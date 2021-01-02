from django.test import Client, TestCase


class TestTranslationContextMiddleware(TestCase):
    def test_sets_language_context(self):
        c = Client()
        response = c.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("garnett_languages" in response.context.keys())
        self.assertTrue("garnett_current_language" in response.context.keys())
