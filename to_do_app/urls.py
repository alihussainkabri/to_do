from django.urls import path
from to_do_app import views
urlpatterns = [
    path('',views.index,name='index'),
    path('login/',views.signin,name='signin'),
    path('signup/',views.signup,name='signup'),
    path('signout/',views.signout,name='signout'),
    path('index/',views.page,name='page'),
    path('add_task/',views.add_task,name='add_task'),
    path('ajax/status',views.ajax_status,name='ajax_status'),
    path('ajax/status/reactivate',views.ajax_status_reactivate,name='ajax_status_reactivate'),
    path('ajax/status/delete',views.ajax_status_delete,name='ajax_status_delete'),
    path('ajax/task_details/',views.ajax_task_details,name='ajax_task_details'),
]