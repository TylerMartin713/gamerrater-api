from django.db import models
from django.contrib.auth.models import User
from .categories import Category


class Game(models.Model):
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    designer = models.CharField(max_length=255)
    year_released = models.IntegerField()
    number_of_players = models.IntegerField()
    estimated_time_to_play = models.DecimalField(max_digits=5, decimal_places=2)
    age_recommendation = models.IntegerField()
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name="games")
    categories = models.ManyToManyField(
        Category, related_name="games", through="GameCategory"
    )
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["title"]


class GameCategory(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("game", "category")
        verbose_name_plural = "game categories"


class GamePicture(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="pictures")
    player = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="game_pictures"
    )
    image_path = models.CharField(max_length=500)
    caption = models.TextField(blank=True, null=True)
    uploaded_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Picture for {self.game.title} by {self.player.username}"

    class Meta:
        ordering = ["-uploaded_on"]


class GameRating(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="ratings")
    player = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="game_ratings"
    )
    rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 11)], help_text="Rating from 1-10"
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.player.username} rated {self.game.title}: {self.rating}/10"

    class Meta:
        unique_together = ("game", "player")
        ordering = ["-updated_on"]


class GameReview(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="reviews")
    player = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="game_reviews"
    )
    review = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review of {self.game.title} by {self.player.username}"

    class Meta:
        unique_together = ("game", "player")
        ordering = ["-updated_on"]
