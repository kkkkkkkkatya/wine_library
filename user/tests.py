from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
import logging

logger = logging.getLogger("test_logger")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("test_results.log", mode='w', encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


User = get_user_model()

class UserTests(APITestCase):
    def setUp(self):
        self.user_data = {
            "email": "test@example.com",
            "password": "StrongPass123"
        }
        self.user = User.objects.create_user(**self.user_data)
        self.token = RefreshToken.for_user(self.user)

# registration

    def test_register_valid_user(self):
        data = {"email": "new@example.com", "password": "NewStrongPass123"}
        response = self.client.post(reverse("user:create"), data)
        logger.info("TEST: test_register_valid_user")
        logger.info(f"Request body: {data}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.data}\n")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_with_taken_email(self):
        data = {"email": self.user_data["email"], "password": "NewStrongPass123"}
        response = self.client.post(reverse("user:create"), data)
        logger.info("TEST: test_register_with_taken_email")
        logger.info(f"Request body: {data}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.data}\n")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_with_invalid_emails(self):
        invalid_emails = ["test.com", "test@", "@test.com", ""]
        for email in invalid_emails:
            data = {"email": email, "password": "pass"}
            response = self.client.post(reverse("user:create"), data)
            logger.info("TEST: test_register_with_invalid_emails")
            logger.info(f"Request body: {data}")
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response body: {response.data}\n")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_with_empty_password(self):
        data = {"email": "newuser@example.com", "password": ""}
        response = self.client.post(reverse("user:create"), data)
        logger.info("TEST: test_register_with_empty_password")
        logger.info(f"Request body: {data}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.data}\n")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_with_short_password(self):
        data = {"email": "shortpass@example.com", "password": "1234"}
        response = self.client.post(reverse("user:create"), data)
        logger.info("TEST: test_register_with_short_password")
        logger.info(f"Request body: {data}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.data}\n")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_with_too_long_password(self):
        long_password = "a" * 129
        data = {"email": "longpass@example.com", "password": long_password}
        response = self.client.post(reverse("user:create"), data)
        logger.info("TEST: test_register_with_too_long_password")
        logger.info(f"Request body: {{'email': 'longpass@example.com', 'password': '<{len(long_password)} chars>'}}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.data}\n")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

# login

    def test_login_with_valid_credentials(self):
        data = self.user_data
        response = self.client.post(reverse("user:token_obtain_pair"), data)

        logger.info("TEST: test_login_with_valid_credentials")
        logger.info(f"Request body: {data}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.data}\n")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)


    def test_login_with_invalid_credentials(self):
        data = {"email": "wrong@example.com", "password": "WrongPass"}
        response = self.client.post(reverse("user:token_obtain_pair"), data)
        logger.info("TEST: test_login_with_invalid_credentials")
        logger.info(f"Request body: {data}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.data}\n")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_with_empty_fields(self):
        data = self.user_data
        response = self.client.post(reverse("user:token_obtain_pair"), {"email": "", "password": ""})
        logger.info("TEST: test_login_with_empty_fields")
        logger.info(f"Request body: {data}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.data}\n")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#token 

    def test_view_token_info(self):
        data = self.user_data
        response = self.client.post(reverse("user:token_obtain_pair"), data)
        logger.info("TEST: test_view_token_info")
        logger.info(f"Request body: {data}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.data}\n")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_token_refresh_and_verify(self):
        refresh = str(self.token)
        access = str(self.token.access_token)

        logger.info("TEST: test_token_refresh_and_verify")
        logger.info(f"Refresh token: {refresh}")
        logger.info(f"Access token: {access}")

        refresh_response = self.client.post(reverse("user:token_refresh"), {"refresh": refresh})
        logger.info(f"POST /token/refresh/ status: {refresh_response.status_code}")
        logger.info(f"POST /token/refresh/ response: {refresh_response.data}")

        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)

        verify_response = self.client.post(reverse("user:token_verify"), {"token": access})
        logger.info(f"POST /token/verify/ status: {verify_response.status_code}")
        logger.info(f"POST /token/verify/ response: {verify_response.data}\n")

        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)

    def test_token_verify_invalid(self):
        invalid_token = "invalid.token.string"
        response = self.client.post(reverse("user:token_verify"), {"token": invalid_token})
        logger.info("TEST: test_token_verify_invalid")
        logger.info(f"Request body: {{'token': '{invalid_token}'}}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.data}\n")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_invalid(self):
        invalid_refresh = "invalid.refresh.token"
        response = self.client.post(reverse("user:token_refresh"), {"refresh": invalid_refresh})
        logger.info("TEST: test_token_refresh_invalid")
        logger.info(f"Request body: {{'refresh': '{invalid_refresh}'}}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.data}\n")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_verify_unauthorized_user(self):
        token = str(RefreshToken.for_user(User(email="nouser@example.com")).access_token)
        response = self.client.post(reverse("user:token_verify"), {"token": token})
        logger.info("TEST: test_token_verify_unauthorized_user")
        logger.info(f"Generated token for non-existing user: {token}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.data}\n")
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_400_BAD_REQUEST])

# get info

    def test_get_info_about_another_user(self):
        another_user = User.objects.create_user(email="other@example.com", password="OtherPass123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token.access_token}")
        url = reverse("user:manage", kwargs={"pk": another_user.id}) if "pk" in reverse("user:manage") else reverse("user:manage")
        response = self.client.get(url)
        logger.info("TEST: test_get_info_about_another_user")
        logger.info(f"Target user: {another_user.email}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.data}\n")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_get_user_info(self):
        data = self.user_data
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token.access_token}")
        response = self.client.get(reverse("user:manage"))
        logger.info("TEST: test_get_user_info")
        logger.info(f"Request body: {data}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.data}\n")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

# update info

    def test_update_user_info(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token.access_token}")
        data = {"email": "updated@example.com"}
        response = self.client.patch(reverse("user:manage"), data)
        logger.info("TEST: test_update_user_info")
        logger.info(f"Request body: {data}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.data}\n")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "updated@example.com")

    def test_update_user_info_unauthorized(self):
        data = self.user_data
        response = self.client.patch(reverse("user:manage"), {"email": "x@y.com"})
        logger.info("TEST: test_update_user_info_unauthorized")
        logger.info(f"Request body: {data}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.data}\n")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_info_about_another_user(self):
        another_user = User.objects.create_user(email="otherupdate@example.com", password="OtherPass123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token.access_token}")
        url = reverse("user:manage", kwargs={"pk": another_user.id}) if "pk" in reverse("user:manage") else reverse("user:manage")
        response = self.client.patch(url, {"email": "hacked@example.com"})
        logger.info("TEST: test_update_info_about_another_user")
        logger.info(f"Target user: {another_user.email}")
        logger.info(f"Request: {{'email': 'hacked@example.com'}}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.data}\n")
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_patch_info_about_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token.access_token}")
        data = {"email": "patched@example.com"}
        response = self.client.patch(reverse("user:manage"), data)
        logger.info("TEST: test_patch_info_about_user")
        logger.info(f"Request body: {data}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.data}\n")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "patched@example.com")

    def test_patch_info_about_another_user(self):
        another_user = User.objects.create_user(email="otherpatch@example.com", password="OtherPass123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token.access_token}")
        url = reverse("user:manage", kwargs={"pk": another_user.id}) if "pk" in reverse("user:manage") else reverse("user:manage")
        response = self.client.patch(url, {"email": "malicious@example.com"})
        logger.info("TEST: test_patch_info_about_another_user")
        logger.info(f"Target user: {another_user.email}")
        logger.info(f"Request: {{'email': 'malicious@example.com'}}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.data}\n")
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_update_with_invalid_email(self):
        user = User.objects.create_user(email="testupdate@example.com", password="TestPass123")
        token = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        url = reverse("user:manage", kwargs={"pk": user.id}) if "pk" in reverse("user:manage") else reverse("user:manage")
        payload = {"email": "invalid-email-format"}
        res = self.client.patch(url, payload)
        logger.info("TEST: test_update_with_invalid_email")
        logger.info(f"Target user: {user.email}")
        logger.info(f"Request: {payload}")
        logger.info(f"Response status: {res.status_code}")
        logger.info(f"Response body: {res.data}\n")
        self.assertIn(res.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY])
