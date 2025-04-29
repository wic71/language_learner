from django.conf import settings
from django.db import models

from core.languages import LANGUAGE_CHOICES


# ---------------------------------------
# Kurs: Övergripande information
# ---------------------------------------
class Course(models.Model):
    """En språkkurs som användare kan skapa och gå med i."""

    name = models.CharField(max_length=255, verbose_name="Kursnamn (på basspråket)")
    description = models.TextField(
        blank=True, verbose_name="Beskrivning (på basspråket)"
    )
    language = models.CharField(
        max_length=10, choices=LANGUAGE_CHOICES, verbose_name="Språk att lära sig"
    )
    base_language = models.CharField(
        max_length=10, choices=LANGUAGE_CHOICES, verbose_name="Basspråk"
    )
    is_public = models.BooleanField(default=False, verbose_name="Publik kurs")
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_courses",
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="joined_courses", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def completed_modules_count(self):
        return self.usermodules.filter(completed=True).count()

    class Meta:
        verbose_name = "Kurs"
        verbose_name_plural = "Kurser"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.name} ({self.get_language_display()})"


# ---------------------------------------
# Moduler: Sektioner inom en kurs
# ---------------------------------------
class Module(models.Model):
    """En modul innehåller text och delmoment inom en kurs."""

    course = models.ForeignKey(
        'Course', on_delete=models.CASCADE, related_name='modules'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=8000)
    text = models.TextField(max_length=8000)
    order = models.PositiveIntegerField(default=1)
    excluded_words = models.CharField(
        max_length=2000,
        blank=True,
        help_text="Komma-separerad lista av ord som inte ska skapa Word-objekt.",
    )

    class Meta:
        ordering = ["order"]
        verbose_name = "Modul"
        verbose_name_plural = "Moduler"

    def __str__(self):
        return f"{self.course.name} – {self.title}"


# ---------------------------------------
# Meningar: Bryter ner modultexten
# ---------------------------------------
class Sentence(models.Model):
    """En mening extraherad från en moduls text."""

    module = models.ForeignKey(
        Module, related_name="sentences", on_delete=models.CASCADE
    )
    text = models.TextField(max_length=1000, blank=True)
    translation = models.TextField(blank=True)
    audio = models.FileField(upload_to="sentence_audio/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Mening"
        verbose_name_plural = "Meningar"

    def __str__(self):
        return f"Sentence {self.order} in {self.module.title}"


# ---------------------------------------
# Ord: Alla unika ord i en modul
# ---------------------------------------
class Word(models.Model):
    """Ett unikt ord från en modul, kopplat till exempelmening."""

    module = models.ForeignKey(Module, related_name="words", on_delete=models.CASCADE)
    text = models.CharField(max_length=100, blank=True)
    translation = models.CharField(max_length=255, blank=True)
    example_sentence = models.ForeignKey(
        Sentence,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="example_words",
    )
    image = models.ImageField(upload_to="word_images/", blank=True, null=True)
    audio = models.FileField(upload_to="word_audio/", blank=True, null=True)

    class Meta:
        verbose_name = "Ord"
        verbose_name_plural = "Ord"
        ordering = ['text']

    def __str__(self):
        return self.text


class UserModule(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    module = models.ForeignKey(
        "Module", on_delete=models.CASCADE, related_name="usermodules"
    )
    unlocked = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    unlocked_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(
        auto_now_add=True
    )  # Sätts automatiskt när relationen skapas
    completed_at = models.DateTimeField(
        null=True, blank=True
    )  # Sätts när eleven slutför modulen

    class Meta:
        unique_together = ('user', 'module')
        verbose_name = "Användarmodul"
        verbose_name_plural = "Användarmoduler"
        ordering = ['started_at']

    def __str__(self):
        return f"{self.user.username} - {self.module.title} ({'Upplåst' if self.unlocked else 'Låst'})"
