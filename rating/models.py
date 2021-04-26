from django.db import models

# Create your models here.

class University(models.Model):
    name = models.CharField(max_length=128, unique=True)

class Professor(models.Model):
    name = models.CharField(max_length=64, unique=True)

    university = models.ForeignKey(University, null=True, on_delete=models.CASCADE)

class Course(models.Model):
    code = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=255, unique=True)

    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.CASCADE)

class Rating(models.Model):
    # Constant grades
    A = "A"
    BP = "BP"
    B = "B"
    CP = "CP"
    C = "C"
    DP = "DP"
    D = "D"
    F = "F"
    GRADE_CHOICES = (
        (A, "A"),
        (BP, "BP"),
        (B, "B"),
        (CP, "CP"),
        (C, "C"),
        (DP, "DP"),
        (D, "D"),
        (F, "F")
    )

    rating = models.FloatField()
    difficulty = models.FloatField()
    takeagain = models.BooleanField(default=True)
    credit = models.BooleanField(default=True)
    textbook = models.BooleanField(default=True)
    attendance = models.BooleanField(default=True)
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, default=A)
    comments = models.TextField()

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
