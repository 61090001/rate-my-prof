from django.urls import path

from . import views

urlpatterns = [
    path('university/create', views.createUniversity),
    path('professor/create', views.createProfessor),
    path('course/create', views.createCourse),
    path('rating/create', views.createRating),
    path('professor/get', views.getProfessors),
    path('coursecode/get/<int:professor_id>', views.getCourseCode),
    path('rating/get/<int:professor_id>', views.getRatings),
]
