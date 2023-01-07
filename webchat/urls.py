from django.urls import path
from webchat import views

urlpatterns = [
    # path('', views.index, name="webchat_index"), #后台首页
    path('', views.index, name="webchat_index"),
    path('runcode',views.runcode,name="web_runcode"),
]