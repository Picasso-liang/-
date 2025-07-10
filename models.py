from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User


# Create your models here.
class Main(models.Model):
    question = models.CharField(max_length=255)
    answer = models.CharField(max_length=32)
    choice_a = models.CharField(max_length=255)
    choice_b = models.CharField(max_length=255)
    choice_c = models.CharField(max_length=255)
    choice_d = models.CharField(max_length=255)
    detail = models.CharField(max_length=255)
    hard = models.BigIntegerField()
    knowledge = models.ManyToManyField(to='Knowledge')


class Knowledge(models.Model):
    knowledge_pot = models.CharField(max_length=255)


class Message(models.Model):
    message = models.OneToOneField(User, on_delete=models.CASCADE)
    wrong = models.TextField(null=True)
    right = models.TextField(null=True)


class History(models.Model):
    name_user = models.CharField(max_length=255)
    user_question = models.TextField(null=True)
    question_answer = models.TextField(null=True)
    user_choice = models.TextField(null=True)
    question_detail = models.TextField(null=True)
    question_pk = models.TextField(null=True)


