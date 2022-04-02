import uuid
from datetime import timedelta

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from shortuuid import ShortUUID

from playpro.abstract import TimestampAbstractModel


def avatar_upload_path(user, filename):
    return f"users/{user.id}/{uuid.uuid4()}"


def create_notification_channel():
    return ShortUUID(alphabet=settings.NOTIFICATION_CHARSET).random(length=10)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email, and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        school, _ = School.objects.get_or_create(name="sampleschool")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("user_type", User.UserType.STAFF.value)
        extra_fields.setdefault("school", school)
        extra_fields.setdefault("school_email", email)
        extra_fields.setdefault("dob", timezone.now())
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class UserAvatar(models.Model):
    image = models.ImageField(upload_to="avatars/")


class User(TimestampAbstractModel, AbstractBaseUser, PermissionsMixin):
    class UserType(models.IntegerChoices):
        STUDENT = 0, _("Student")
        STAFF = 1, _("Staff")

    first_name = models.CharField(_("first name"), max_length=255)
    last_name = models.CharField(_("last name"), max_length=255)
    email = models.EmailField(_("email address"), max_length=255, unique=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    user_type = models.IntegerField(choices=UserType.choices)
    dob = models.DateField()
    school = models.ForeignKey("School", on_delete=models.CASCADE)
    school_email = models.EmailField()
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    avatar = models.ForeignKey(UserAvatar, on_delete=models.SET_NULL, null=True)
    nickname = models.CharField(max_length=510)
    epic_games_id = models.CharField(max_length=255, blank=True, default="")
    ea_games_id = models.CharField(max_length=255, blank=True, default="")
    ps_network_id = models.CharField(max_length=255, blank=True, default="")
    riot_id = models.CharField(max_length=255, blank=True, default="")
    last_email_reset = models.DateTimeField(auto_now=True)
    graduation_year = models.CharField(max_length=4)
    notifications_channel = models.CharField(
        default=create_notification_channel(), max_length=10
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    @property
    def resend_activation_mail_available(self):
        return (
            self.last_email_reset
            + timedelta(minutes=getattr(settings, "EMAIL_RESEND_DELAY"))
            <= timezone.now()
        )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.nickname = f"{self.first_name}-{self.last_name}"
            self.avatar = UserAvatar.objects.first()
        super().save(*args, **kwargs)

    def is_in_team(self, team):
        from tournaments.models import TournamentTeamMember

        return TournamentTeamMember.objects.filter(
            user=self, team=team, invitation_accepted=True
        ).exists()


class School(models.Model):
    name = models.CharField(max_length=255)
