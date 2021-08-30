from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Ingredient, Tag
from recipe import serializers


class BaseRecipeAttViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    """Base viewset for user owned recipe attributes"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authentication user only"""
        return self.queryset.filter(user = self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Create a new Object"""
        return serializer.save(user = self.request.user)


class TagViewSet(BaseRecipeAttViewSet):
    """Manage tags in the database"""

    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseRecipeAttViewSet):
    """Manage Ingredients in database"""

    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer