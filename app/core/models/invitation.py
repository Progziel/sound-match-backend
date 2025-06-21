# from django.db import models
# from django.contrib.auth import get_user_model
# from .user import User

# class Room(models.Model):
#     name = models.CharField(max_length=100, unique=True)
#     invited_by = models.ForeignKey(
#         get_user_model(),
#         on_delete=models.SET_NULL,
#         null=True, blank=True,
#     )
#     invitation_to = models.ForeignKey(
#         get_user_model(),
#         on_delete=models.SET_NULL,
#         null=True, blank=True,
#     )
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.name

# class Message(models.Model):
#     room = models.ForeignKey(
#         Room,
#         on_delete=models.CASCADE,
#         related_name='messages',
#     )
#     user = models.ForeignKey(
#         get_user_model(),
#         on_delete=models.SET_NULL,
#         null=True, blank=True,
#     )
#     email = models.CharField(max_length=100)
#     content = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ['timestamp']

#     def __str__(self):
#         return f"{self.email}: {self.content[:50]}"