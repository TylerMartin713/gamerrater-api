from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from raterapi.models.reviews import Review
from raterapi.models.games import Game
from django.contrib.auth.models import User


class ReviewViewSet(ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request):
        """Handle POST operations for creating a review

        Returns:
            Response -- JSON serialized review instance
        """
        try:
            game = Game.objects.get(pk=request.data["game_id"])

            # Check if user already reviewed this game
            existing_review = Review.objects.filter(
                game=game, player=request.auth.user
            ).first()

            if existing_review:
                # Update existing review
                existing_review.review = request.data["review"]
                existing_review.save()
                serializer = ReviewSerializer(existing_review)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # Create new review
                review = Review()
                review.game = game
                review.player = request.auth.user
                review.review = request.data["review"]
                review.save()

                serializer = ReviewSerializer(review)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Game.DoesNotExist:
            return Response(
                {"message": "Game not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        """Handle GET requests for all reviews of a specific game

        Returns:
            Response -- JSON serialized array of reviews
        """
        try:
            game_id = request.query_params.get("game_id", None)
            if game_id:
                reviews = Review.objects.filter(game_id=game_id).order_by("-created_on")
            else:
                reviews = Review.objects.all().order_by("-created_on")

            serializer = ReviewSerializer(reviews, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single review

        Returns:
            Response -- JSON serialized review
        """
        try:
            review = Review.objects.get(pk=pk)
            serializer = ReviewSerializer(review)
            return Response(serializer.data)
        except Review.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """Handle PUT requests for updating a review

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            review = Review.objects.get(pk=pk)

            # Check if user owns this review
            if review.player != request.auth.user:
                return Response(
                    {"message": "You can only edit your own reviews"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            review.review = request.data["review"]
            review.save()

            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except Review.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a review

        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            review = Review.objects.get(pk=pk)

            # Check if user owns this review
            if review.player != request.auth.user:
                return Response(
                    {"message": "You can only delete your own reviews"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            review.delete()
            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except Review.DoesNotExist:
            return Response(
                {"message": "Review not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as ex:
            return Response(
                {"message": ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ReviewSerializer(serializers.ModelSerializer):
    """JSON serializer for reviews"""

    player = serializers.SerializerMethodField()
    game_title = serializers.CharField(source="game.title", read_only=True)

    def get_player(self, obj):
        """Get player information"""
        return {
            "id": obj.player.id,
            "username": obj.player.username,
            "first_name": obj.player.first_name,
            "last_name": obj.player.last_name,
        }

    class Meta:
        model = Review
        fields = (
            "id",
            "game",
            "game_title",
            "player",
            "review",
            "created_on",
        )
