from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('news/', views.news_list, name='news_list'),
    path('news/<slug:slug>/', views.news_detail, name='news_detail'),
    path('announcements/', views.announcements, name='announcements'),
    path('gallery/', views.gallery, name='gallery'),
    path('student-life/', views.student_life, name='student_life'),
    path('student-leaders/', views.student_leaders, name='student_leaders'),
    path('staff/', views.staff_list, name='staff'),
    path('departments/', views.departments, name='departments'),
    path('events/', views.events, name='events'),
    path('contact/', views.contact, name='contact'),
    path('page/<slug:slug>/', views.page_detail, name='page_detail'),
    path('academics/', views.academics, name='academics'),
    path('about/', views.about_us, name='about_us'),
    path('login/', views.dotshule_login, name='dotshule_login'),
]

