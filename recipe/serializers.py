from rest_framework import serializers

from core.models import Ingredient, Recipe, Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag object"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)
        
class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for Ingredient object"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name')
        read_only_fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe object"""

    ingredients = serializers.PrimaryKeyRelatedField(
        many = True,
        queryset = Ingredient.objects.all()
    )

    tags = serializers.PrimaryKeyRelatedField(
        many = True,
        queryset = Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'time_minutes', 'price', 'ingredients', 'tags', 'link')
        read_only_fields = ('id',)


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for Recipe Detail object"""

    ingredients = IngredientSerializer(many = True, read_only = True)
    tags = TagSerializer(many = True, read_only = True)