from django.test import TestCase
from django.urls import reverse


class OpenGraphDefaultTests(TestCase):
    def test_homepage_has_default_open_graph_metadata(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'property="og:title"')
        self.assertContains(response, 'property="og:description"')
        self.assertContains(response, 'property="og:url" content="http://testserver/"')
        self.assertContains(response, 'property="og:image"')
        self.assertContains(response, 'property="og:type" content="website"')
