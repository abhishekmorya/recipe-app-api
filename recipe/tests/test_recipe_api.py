from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.utils import tag
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient
from recipe import serializers
from recipe.serializers import RecipeSerializer


RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Return recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_recipe(user, **params):
    """Create and return sample recipe"""

    defaults = {
        'title': 'Sample Recipe',
        'time_minutes': 10,
        'price': 5.00
    }

    defaults.update(params)
    return Recipe.objects.create(user = user, **defaults)


def sample_tag(user, name = 'Sample Tag'):
    """Create and return sample tag"""
    return Tag.objects.create(user = user, name = name)


def sample_ingredients(user, name ='Sample Ingredients'):
    """Create and return sample Ingredients"""
    return Ingredient.objects.create(user = user, name = name)


class PublicRecipeApiTest(TestCase):
    """Test unauthenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()
    
    def test_login_required(self):
        """Test that login is required for retrieving Recipes"""

        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTest(TestCase):
    """Test authorized Recipe API access"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'abhishek@gmail.com',
            'password1234'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_reciepes(self):
        """Test retrieving the recipes"""

        sample_recipe(user = self.user)
        sample_recipe(user = self.user)

        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test the ingredients for the authenticated user"""

        user2 = get_user_model().objects.create_user(
            'test@testmail.com',
            'password'
        )
        sample_recipe(user = user2)
        sample_recipe(user = self.user)
        
        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.all().filter(user = self.user)
        serializer = RecipeSerializer(recipes, many = True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""

        recipe = sample_recipe(user = self.user)
        recipe.tags.add(sample_tag(user = self.user))
        recipe.ingredients.add(sample_ingredients(user = self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = serializers.RecipeDetailSerializer(recipe)

        print(f"res: {res.data}")
        print(f"serializer: {serializer.data}")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)