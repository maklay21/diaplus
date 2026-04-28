from django.views.generic import DetailView, TemplateView, CreateView, UpdateView
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.contrib.auth import login, authenticate
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.views import View
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.core.files.storage import default_storage

from .models import Product, Manufacturer, ProductType
from .forms import ProductForm, LoginForm
from .logging_config import logger


class LoginView(View):

    template_name = 'auth/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('product_list')

    def dispatch(self, request, *args, **kwargs):

        if request.user.is_authenticated:
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):

        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):

        form = self.form_class(request, data=self.request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username', '')
            password = form.cleaned_data.get('password', '')

            if not username or not password:
                messages.error(request, 'Требуется имя пользователя и пароль')
                return render(request, self.template_name, {'form': form})

            user = authenticate(
                request=request,
                username=username,
                password=password
            )

            if user:
                login(request, user)
                messages.success(request,f'Добро пожаловать, {username}!')
                return redirect(self.success_url)
            else:
                logger.warning(f'Пользователь {request.user} ввел неверный логин или пароль: {username} - {password}')
                messages.error(request, 'Неверное имя пользователя ии пароль')
        else:
            messages.error(request,'Неверное имя пользователя или пароль')

        return render(request, self.template_name, {'form': form})


class LogoutView(BaseLogoutView):

    next_page = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):

        if request.user.is_authenticated:
            messages.info(request, 'Вы вышли из системы')
        return super().dispatch(request, *args, **kwargs)


class HomeView(View):
    def get(self, request):
        return render(request, 'pages/home.html')


class ProductListView(View):

    paginate_by = 10

    def get(self, request):

        search_query = request.GET.get('search', '')
        selected_manufacturer = request.GET.get('manufacturer', '')
        selected_type = request.GET.get('product_type', '')
        sort_by = request.GET.get('sort', '-created_at')
        order = request.GET.get('order', 'asc')
        page_number = request.GET.get('page', 1)

        products = Product.objects.select_related('manufacturer', 'product_type')

        # Поиск
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) |
                Q(manufacturer__name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        # Фильтрация
        if selected_manufacturer and selected_manufacturer.isdigit():
            products = products.filter(manufacturer_id=int(selected_manufacturer))

        if selected_type and selected_type.isdigit():
            products = products.filter(product_type_id=int(selected_type))

        # Сортировка
        if sort_by:
            if order == 'desc':
                sort_by = f'-{sort_by}'
            products = products.order_by(sort_by)

        # Пагинация
        paginator = Paginator(products, self.paginate_by)
        page_obj = paginator.get_page(page_number)

        context = {
            'products': page_obj,
            'page_obj': page_obj,
            'search_query': search_query,
            'selected_manufacturer': selected_manufacturer,
            'selected_type': selected_type,
            'current_sort': sort_by.lstrip('-'),
            'current_order': order,
        }

        # Проверяем AJAX запрос
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(request, 'catalog/products_table.html', context)

        # Для обычных запросов
        manufacturers = Manufacturer.objects.all()
        product_types = ProductType.objects.all()
        context.update({
            'manufacturers': manufacturers,
            'product_types': product_types,
        })
        return render(request, 'catalog/product_list.html', context)


class ProductDetailView(DetailView):

    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'


class ProductCreateView(LoginRequiredMixin, CreateView):

    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_add.html'
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):

        # Сохраняем товар
        response = super().form_valid(form)

        messages.success(
            self.request,
            f'Товар {self.object.name} успешно добавлен в каталог!'
        )

        logger.info(f'Пользователь {self.request.user} добавил товар {self.object.name} в каталог')

        return response

    def form_invalid(self, form):

        messages.error(
            self.request,
            'Не удалось добавить товар. Пожалуйста, проверьте введенные данные'
        )
        return super().form_invalid(form)


@method_decorator(require_POST, name='dispatch')
class ProductDeleteView(LoginRequiredMixin, View):

    def post(self, request, pk):
        try:
            # Получаем товар
            product = get_object_or_404(Product, pk=pk)

            # Сохраняем имя для ответа
            product_name = str(product)

            # Удаляем изображение
            if product.image and default_storage.exists(product.image.name):
                default_storage.delete(product.image.name)

            # Удаляем товар
            product.delete()

            logger.info(f'Товар "{product_name}" успешно удален пользователем {request.user}')

            return JsonResponse({
                'success': True,
                'message': f'Товар "{product_name}" успешно удален'
            })

        except Exception as e:
            logger.error(f'Ошибка при удалении: {str(e)}')
            return JsonResponse({
                'success': False,
                'message': 'Ошибка при удалении'
            }, status=500)


class ProductEditView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_edit.html'
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        logger.info(f'Товар "{self.object.name}" успешно обновлен пользователем {self.request.user}')
        messages.success(self.request, f'Товар "{self.object.name}" успешно обновлен!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Не удалось обновить товар. Пожалуйста, проверьте введенные данные')
        return super().form_invalid(form)


@method_decorator(require_POST, name='dispatch')
class AddManufacturerView(LoginRequiredMixin, View):

    def post(self, request):
        name = request.POST.get('name', '').strip()
        country = request.POST.get('country', '').strip()

        if name:
            Manufacturer.objects.create(
                name=name,
                country=country
            )

            messages.success(
                self.request,
                'Новый производитель успешно добавлен!'
            )

            logger.info(
                f'Пользователь {self.request.user} добавил нового производителя. Наименование: {name}, страна: {country}')
        else:
            messages.warning(
                self.request,
                'Не удалось добавить производителя. Пожалуйста, проверьте введенные данные'
            )

        return redirect('product_add')


@method_decorator(require_POST, name='dispatch')
class AddProductTypeView(LoginRequiredMixin, View):

    def post(self, request):
        name = request.POST.get('name', '').strip()

        if name:
            ProductType.objects.create(
                name=name
            )

            messages.success(
                self.request,
                'Новый вид товара успешно добавлен!'
            )

            logger.info(
                f'Пользователь {self.request.user} добавил нового производителя. Наименование: {name}')
        else:
            messages.warning(
                self.request,
                'Не удалось добавить вид товара. Пожалуйста, проверьте введенные данные'
            )

        return redirect('product_add')


class AboutView(TemplateView):
    template_name = 'pages/about.html'


class ContactsView(TemplateView):
    template_name = 'pages/contacts.html'