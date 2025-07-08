from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from raterapi.models.games import Game
from raterapi.models.categories import Category


class GameViewSet(ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    """games view set"""

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        game = Game()
        game.title = request.data["title"]
        game.description = request.data["description"]
        game.designer = request.data["designer"]
        game.year_released = request.data["year_released"]
        game.number_of_players = request.data["number_of_players"]
        game.estimated_time_to_play = request.data["estimated_time_to_play"]
        game.age_recommendation = request.data["age_recommendation"]
        game.player = request.auth.user

        try:
            game.save()

            # Handle categories if provided
            if "categories" in request.data:
                for category_id in request.data["categories"]:
                    category = Category.objects.get(pk=category_id)
                    game.categories.add(category)

            serializer = GameSerializer(game)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single item

        Returns:
            Response -- JSON serialized instance
        """
        try:
            game = Game.objects.get(pk=pk)
            serializer = GameSerializer(game)
            return Response(serializer.data)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """Handle PUT requests

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            game = Game.objects.get(pk=pk)
            game.title = request.data["title"]
            game.description = request.data["description"]
            game.designer = request.data["designer"]
            game.year_released = request.data["year_released"]
            game.number_of_players = request.data["number_of_players"]
            game.estimated_time_to_play = request.data["estimated_time_to_play"]
            game.age_recommendation = request.data["age_recommendation"]

            # Handle categories if provided
            if "categories" in request.data:
                game.categories.clear()  # Remove existing categories
                for category_id in request.data["categories"]:
                    category = Category.objects.get(pk=category_id)
                    game.categories.add(category)

            game.save()
        except Game.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return HttpResponseServerError(ex)

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single item

        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            game = Game.objects.get(pk=pk)
            game.delete()
            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except Game.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response(
                {"message": ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def list(self, request):
        """Handle GET requests for all items

        Returns:
            Response -- JSON serialized array
        """
        try:
            # Check if user wants only their games
            my_games = request.query_params.get("my_games", None)

            if my_games == "true":
                games = Game.objects.filter(player=request.auth.user).order_by(
                    "-created_on"
                )
            else:
                games = Game.objects.all().order_by("-created_on")

            serializer = GameSerializer(games, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)


class GameSerializer(serializers.ModelSerializer):
    """JSON serializer for games"""

    categories = serializers.SerializerMethodField()
    player = serializers.PrimaryKeyRelatedField(read_only=True)

    def get_categories(self, obj):
        """Get the full category information"""
        return [
            {"id": category.id, "label": category.label}
            for category in obj.categories.all()
        ]

    class Meta:
        model = Game
        fields = (
            "id",
            "title",
            "description",
            "designer",
            "year_released",
            "number_of_players",
            "estimated_time_to_play",
            "age_recommendation",
            "player",
            "categories",
            "created_on",
        )
