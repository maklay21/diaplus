from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contacts/', views.ContactsView.as_view(), name='contacts'),
    path('product/add/', views.ProductCreateView.as_view(), name='product_add'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('product/edit/<int:pk>/', views.ProductEditView.as_view(), name='product_edit'),
    path('product/delete/<int:pk>/', views.ProductDeleteView.as_view(), name='product_delete'),
    path('add-manufacturer/', views.AddManufacturerView.as_view(), name='add_manufacturer'),
    path('add-product-type/', views.AddProductTypeView.as_view(), name='add_product_type'),
    path('management/control_panel/login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]