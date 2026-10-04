from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.http import HttpResponse
from django.test import TestCase


class SignupViewTests(TestCase):
	@patch('accounts.views.SignupForm')
	def test_username_integrity_error_is_shown_on_the_form(self, signup_form_class):
		form = signup_form_class.return_value
		form.is_valid.return_value = True
		form.cleaned_data = {'username': 'already-taken'}
		form.save.side_effect = IntegrityError
		manager_result = SimpleNamespace(exists=lambda: True)

		with patch('accounts.views.get_user_model', return_value=get_user_model()), patch.object(
			get_user_model().objects, 'filter', return_value=manager_result
		), patch('accounts.views.render', return_value=HttpResponse()):
			response = self.client.post('/accounts/signup/', {})

		self.assertEqual(response.status_code, 200)
		form.add_error.assert_called_once_with(
			'username', 'Tên đăng nhập này đã được sử dụng.'
		)
