from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from django.conf import settings

from core.models import Ingredient, Recipe
from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')

class PublicIngredientsApiTest(TestCase):
    """Test the publicly available ingredients api"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving Ingredients"""

        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTest(TestCase):
    """Tests the authorized users Ingredients API"""

    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            'abhishek@gmail.com',
            'password1234'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test retrieving a list of ingredients"""

        Ingredient.objects.create(user = self.user, name = 'Tomato')
        Ingredient.objects.create(user = self.user, name = 'Potato')

        res = self.client.get(INGREDIENT_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many = True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test the ingredients for the authenticated user are returned"""

        user2 = get_user_model().objects.create_user(
            'test@mail.com',
            'password1233'
        )

        Ingredient.objects.create(user = user2, name = 'Vinager')
        ingredient = Ingredient.objects.create(user = self.user, name = 'Tomato')

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        """Test create a new ingredient"""

        payload = {'name': 'Cabbage'}
        self.client.post(INGREDIENT_URL, payload)

        exists = Ingredient.objects.filter(
            user = self.user,
            name = payload['name'],
        ).exists()

        self.assertTrue(exists, 'Test Creating successful ingredient')

    def test_create_ingredient_invalid(self):
        """Test creating invalid ingredient"""

        payload = {'name': ''}
        res = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST, 'Test Create Invalid Ingredient')

    def test_retrieve_ingredients_assigned_to_recipe(self):
        """Test filtering by ingredients by those assigned to recipes"""

        ingredient1 = Ingredient.objects.create(user = self.user, name = 'Apple')
        ingredient2 = Ingredient.objects.create(user = self.user, name = 'Turkey')
        recipe = Recipe.objects.create(
            user = self.user,
            title = 'Apple Crumble',
            time_minutes = 23,
            price = 40.00
        )
        recipe.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_ingredients_assigned_unique(self):
        """Test filtering ingredients by assigned returns unique items"""

        ingredient = Ingredient.objects.create(user = self.user, name = 'Eggs')
        Ingredient.objects.create(user = self.user, name = 'Cheese')

        recipe1 = Recipe.objects.create(
            user = self.user,
            title = 'Eggs benadict',
            time_minutes = 15,
            price = 30.00
        )
        recipe1.ingredients.add(ingredient)
        recipe2 = Recipe.objects.create(
            user = self.user,
            title = 'Coriander Eggs on toast',
            time_minutes = 20,
            price = 35.00
        )
        recipe2.ingredients.add(ingredient)

        res = self.client.get(
            INGREDIENT_URL,
            {'assigned_only': 1}
        )
        self.assertEqual(len(res.data), 1)
    