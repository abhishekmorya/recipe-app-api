from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Ingredient, Recipe, Tag
from recipe import serializers


class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
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


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database"""

    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage Ingredients in database"""

    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage Recipes in the database"""

    serializer_class = serializers.RecipeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Recipe.objects.all()

    def get_queryset(self):
        """Retrieve recipes only for authenticated users"""

        return self.queryset.filter(user = self.request.user)

    def get_serializer_class(self):
        """Return serializer for detail serializer for retrieve action"""

        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        return serializer.save(user = self.request.user)

    @action(methods=['POST'], detail = True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Uploadd an image to a recipe"""

        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data = request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status = status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )