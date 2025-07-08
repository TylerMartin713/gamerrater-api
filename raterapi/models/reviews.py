from django.db import models
from django.contrib.auth.models import User
from .games import Game


class Review(models.Model):
    game = models.ForeignKey(
        Game, on_delete=models.CASCADE, related_name="user_reviews"
    )
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.player.username} for {self.game.title}"

    class Meta:
        # Ensure a user can only review a game once
        unique_together = ("game", "player")
