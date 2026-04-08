import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Objectifs nutritionnels
    calories_cibles = models.PositiveIntegerField(null=True, blank=True)
    proteines_cibles = models.PositiveIntegerField(null=True, blank=True)
    glucides_cibles = models.PositiveIntegerField(null=True, blank=True)
    lipides_cibles = models.PositiveIntegerField(null=True, blank=True)
    fibres_cibles = models.PositiveIntegerField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'Utilisateur'

    def __str__(self):
        return self.email
    
class Foyer(models.Model):
        nom = models.CharField(max_length=255)
        code = models.CharField(max_length=10, unique=True)
        created_at = models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return self.nom
    
class MembreFoyer(models.Model):
        ROLE_CHOICES = [
            ('admin', 'Admin'),
            ('membre', 'Membre')
            ]
        
        user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
        foyer = models.ForeignKey(Foyer, on_delete=models.CASCADE, related_name='membres')
        role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='membre')
        joined_at = models.DateTimeField(auto_now_add=True)

        class Meta:
            unique_together = ('user', 'foyer')

        def __str__(self):
             return f"{self.user.email} - {self.foyer.nom}"