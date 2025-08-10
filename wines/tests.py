from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from wines.models import Wine, WineReview
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile
from PIL import Image
import logging

logger = logging.getLogger("test_logger")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("test_results.log", mode='w', encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

User = get_user_model()

class WineTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(email="admin@test.com", password="adminpass")
        self.user = User.objects.create_user(email="user@test.com", password="userpass")
        self.admin_token = str(RefreshToken.for_user(self.admin).access_token)
        self.user_token = str(RefreshToken.for_user(self.user).access_token)

        self.wine = Wine.objects.create(
            title="Test Wine",
            vintage="2020",
            price=15.99,
            wine_type="Red",
            country="France",
            capacity=0.75
        )

# get wine

    def test_list_wines(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        response = self.client.get(reverse("wines:wine-list"))
        logger.info("TEST: test_list_wines")
        logger.info("Request: GET /wines/")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.data}\n")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_wine_by_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        url = reverse("wines:wine-detail", args=[self.wine.id])
        response = self.client.get(url)
        logger.info("TEST: test_get_wine_by_id")
        logger.info(f"Request: GET {url}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.data}\n")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_wine_non_existing(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        url = reverse("wines:wine-detail", args=[99999])
        response = self.client.get(url)
        logger.info("TEST: test_get_wine_non_existing")
        logger.info(f"Request: GET {url}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.data}\n")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

# add wine

    def test_create_wine_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        url = reverse("wines:wine-list")
        data = {
            "title": "New Wine",
            "vintage": "2019",
            "price": 22.5,
            "wine_type": "White",
            "country": "Italy",
            "capacity": 0.75
        }
        response = self.client.post(url, data)
        logger.info("TEST: test_create_wine_admin_only")
        logger.info(f"Request: POST {url}")
        logger.info(f"Request body: {data}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.data}\n")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_wine_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        url = reverse("wines:wine-list")
        data = {
            "title": "Unauthorized Wine",
            "vintage": "2018"
        }
        response = self.client.post(url, data)
        logger.info("TEST: test_create_wine_unauthorized")
        logger.info(f"Request: POST {url}")
        logger.info(f"Request body: {data}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.data}\n")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_wine_future_vintage(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        url = reverse("wines:wine-list")
        data = {
            "title": "Future Wine",
            "vintage": "2035",
            "price": 50.0,
            "wine_type": "Red",
            "country": "Spain",
            "capacity": 0.75
        }
        response = self.client.post(url, data)
        logger.info("TEST: test_create_wine_future_vintage")
        logger.info(f"Request: POST {url}")
        logger.info(f"Request body: {data}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.data}\n")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

# update wine

    def test_update_wine_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        url = reverse("wines:wine-detail", args=[self.wine.id])
        data = {
            "title": "Updated Wine",
            "vintage": "2018",
            "price": 18.0,
            "wine_type": "White",
            "country": "Italy",
            "capacity": 1.0
        }
        response = self.client.put(url, data)
        logger.info("TEST: test_update_wine_admin")
        logger.info(f"Request: PUT {url}")
        logger.info(f"Request body: {data}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.data}\n")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Wine")

    def test_patch_wine_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        url = reverse("wines:wine-detail", args=[self.wine.id])
        data = {"price": 20.0}
        response = self.client.patch(url, data)
        logger.info("TEST: test_patch_wine_admin")
        logger.info(f"Request: PATCH {url}")
        logger.info(f"Request body: {data}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.data}\n")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data["price"]), 20.0)

    def test_update_wine_user_forbidden(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        url = reverse("wines:wine-detail", args=[self.wine.id])
        data = {
            "title": "User Updated Wine",
            "vintage": "2015",
            "price": 12.0,
            "wine_type": "Red",
            "country": "USA",
            "capacity": 0.75
        }
        response = self.client.put(url, data)
        logger.info("TEST: test_update_wine_user_forbidden")
        logger.info(f"Request: PUT {url}")
        logger.info(f"Request body: {data}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.data}\n")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_wine_user_forbidden(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        url = reverse("wines:wine-detail", args=[self.wine.id])
        data = {"price": 10.0}
        response = self.client.patch(url, data)
        logger.info("TEST: test_patch_wine_user_forbidden")
        logger.info(f"Request: PATCH {url}")
        logger.info(f"Request body: {data}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.data}\n")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_wine_admin_future_vintage(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        url = reverse("wines:wine-detail", args=[self.wine.id])
        data = {
            "title": "Future Update",
            "vintage": "2035",
            "price": 30.0,
            "wine_type": "Red",
            "country": "France",
            "capacity": 0.75
        }
        response = self.client.put(url, data)
        logger.info("TEST: test_update_wine_admin_future_vintage")
        logger.info(f"Request: PUT {url}")
        logger.info(f"Request body: {data}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.data}\n")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

# delete wine

    def test_delete_wine_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        url = reverse("wines:wine-detail", args=[self.wine.id])
        response = self.client.delete(url)
        logger.info("TEST: test_delete_wine")
        logger.info(f"Request: DELETE {url}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {getattr(response, 'data', 'No content')}\n")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_wine_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        url = reverse("wines:wine-detail", args=[self.wine.id])
        response = self.client.delete(url)
        logger.info("TEST: test_delete_wine_user_forbidden")
        logger.info(f"Request: DELETE {url}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {getattr(response, 'data', 'No content')}\n")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_wine_non_existing_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        url = reverse("wines:wine-detail", args=[99999])
        response = self.client.delete(url)
        logger.info("TEST: test_delete_wine_non_existing_admin")
        logger.info(f"Request: DELETE {url}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {getattr(response, 'data', 'No content')}\n")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

# review 

    def test_add_review(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        url = reverse("wines:wine-add-review", args=[self.wine.id])
        data = {"rating": 4, "comment": "Wow"}
        response = self.client.post(url, data, format="json")
        logger.info("TEST: test_add_review")
        logger.info(f"Request: POST {url} | Data: {data}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {getattr(response, 'data', 'No content')}\n")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WineReview.objects.count(), 1)
        review = WineReview.objects.first()
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.wine, self.wine)
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.comment, "Wow")

    def test_delete_review(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        review = WineReview.objects.create(
            wine=self.wine,
            user=self.user,
            rating=5,
            comment="Ideal"
        )
        url = reverse("wines:wine-delete-review", args=[self.wine.id])
        response = self.client.delete(url)
        logger.info("TEST: test_delete_review")
        logger.info(f"Request: DELETE {url}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {getattr(response, 'data', 'No content')}\n")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(WineReview.objects.count(), 0)

    def test_delete_non_existing_review(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        delete_url = reverse("wines:wine-delete-review", args=[99999])
        res = self.client.delete(delete_url)
        logger.info("TEST: test_delete_non_existing_review")
        logger.info(f"Request: DELETE {delete_url}")
        logger.info(f"Response status: {res.status_code}")
        logger.info(f"Response body: {getattr(res, 'data', 'No content')}\n")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_review_twice_same_user(self):
        user = User.objects.create_user(email="test@example.com", password="pass1234")
        wine = Wine.objects.create(
            title="Test Wine 2",
            vintage="2020",
            price=15.99,
            wine_type="Red",
            country="France",
            capacity=0.75
        )
        token = str(RefreshToken.for_user(user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        url = reverse("wines:wine-add-review", args=[wine.id])
        payload = {"rating": 5, "comment": "Excellent wine!"}
        response1 = self.client.post(url, payload)
        logger.info("TEST: test_add_review_twice_same_user - first add")
        logger.info(f"Request: POST {url} | Data: {payload}")
        logger.info(f"Response status: {response1.status_code}")
        logger.info(f"Response body: {getattr(response1, 'data', 'No content')}\n")
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        response2 = self.client.post(url, payload)
        logger.info("TEST: test_add_review_twice_same_user - second add")
        logger.info(f"Request: POST {url} | Data: {payload}")
        logger.info(f"Response status: {response2.status_code}")
        logger.info(f"Response body: {getattr(response2, 'data', 'No content')}\n")
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(WineReview.objects.filter(wine=wine, user=user).count(), 1)

# favorites

    def test_save_unsave_favorites(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        save_url = reverse("wines:wine-save", args=[self.wine.id])
        unsave_url = reverse("wines:wine-unsave", args=[self.wine.id])

        save_response = self.client.post(save_url)
        logger.info("TEST: test_save_unsave_favorites (SAVE)")
        logger.info(f"Request: POST {save_url}")
        logger.info(f"Response status: {save_response.status_code}")
        logger.info(f"Response body: {save_response.data}")
        self.assertEqual(save_response.status_code, status.HTTP_200_OK)

        unsave_response = self.client.post(unsave_url)
        logger.info("TEST: test_save_unsave_favorites (UNSAVE)")
        logger.info(f"Request: POST {unsave_url}")
        logger.info(f"Response status: {unsave_response.status_code}")
        logger.info(f"Response body: {unsave_response.data}\n")
        self.assertEqual(unsave_response.status_code, status.HTTP_200_OK)

#image

    def test_upload_wine_image(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        url = reverse("wines:wine-upload-image", args=[self.wine.id])
        with tempfile.NamedTemporaryFile(suffix=".jpg") as tmp:
            image = Image.new("RGB", (100, 100))
            image.save(tmp, format="JPEG")
            tmp.seek(0)
            uploaded = SimpleUploadedFile("wine.jpg", tmp.read(), content_type="image/jpeg")
            response = self.client.post(url, {"image": uploaded}, format="multipart")
        logger.info("TEST: test_upload_wine_image")
        logger.info(f"Request: POST {url}")
        logger.info("Request body: [multipart image]")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.data}\n")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_wine_image_user_forbidden(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        url = reverse("wines:wine-upload-image", args=[self.wine.id])
        with tempfile.NamedTemporaryFile(suffix=".jpg") as tmp:
            image = Image.new("RGB", (100, 100))
            image.save(tmp, format="JPEG")
            tmp.seek(0)
            uploaded = SimpleUploadedFile("wine.jpg", tmp.read(), content_type="image/jpeg")
            response = self.client.post(url, {"image": uploaded}, format="multipart")
        logger.info("TEST: test_update_wine_image_user_forbidden")
        logger.info(f"Request: POST {url}")
        logger.info("Request body: [multipart image]")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.data}\n")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)



    def test_swagger_ui_accessible(self):
        url = "/api/doc/swagger/"
        response = self.client.get(url)
        logger.info("TEST: test_swagger_ui_accessible")
        logger.info(f"Request: GET {url}")
        logger.info(f"Response status: {response.status_code}")
        logger.info("Response body: [HTML content hidden]\n")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    
