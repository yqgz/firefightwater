"""firefightwater URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from firefightwater import views

# app_name = 'firefightwater'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.project, name='project'),
    path('project_add/', views.project_add, name='project_add'),
    path('project_save/<int:pk>/', views.project_save, name='project_save'),
    path('introduction/<int:pk>/', views.introduction, name='introduction'),
    path('introduction_edit/<int:pk>/', views.introduction_edit, name='introduction_edit'),
    path('module/<int:pk>/<int:md>/', views.module, name='module'),
    path('excel/<int:pk>/', views.excel, name='excel'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('nestedheader/', views.nestedheader, name='nestedheader'),
    path('test_page/', views.test_page, name='test_page'),
    path('gas_test/', views.gas_test, name='gas_test'),
    path('sprinkle_test/', views.sprinkle_test, name='sprinkle_test'),
    path('column_dropdown/get_column/<int:id>', views.get_column, name='get_column'),
    # path('<int:pk>/<int:md>/Auto/', views.Auto, name='Auto'),
    # path('<int:pk>/Cooling/', views.excel, name='Cooling'),
    # path('<int:pk>/Extinguisher/', views.excel, name='Extinguisher'),
    # path('<int:pk>/Gas/', views.excel, name='Gas'),
    # path('<int:pk>/Indoor/', views.excel, name='Indoor'),
    # path('<int:pk>/Outdoor/', views.excel, name='Outdoor'),
    # path('<int:pk>/Sprinkle/', views.excel, name='Sprinkle'),
    # path('<int:pk>/SystemWater/', views.excel, name='SystemWater'),
    # path('<int:pk>/Transfer/', views.excel, name='Transfer'),
    # path('<int:pk>/WaterPool/', views.excel, name='WaterPool'),
]
