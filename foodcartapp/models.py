from django.db import models
from django.db.models import F, Sum
from django.core.validators import MinValueValidator
from django.utils import timezone

from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):

    def with_cost(self):
        cost_of_order = self.filter(status='OPEN').annotate(cost_of_order=Sum(F('products__cost')))
        return cost_of_order

    def get_restaurants_for_order(self):
        restaurant_menu_items = RestaurantMenuItem.objects.all()
        all_restaurants = set()
        for item in restaurant_menu_items:
            all_restaurants.add(item.restaurant)
        for order in self:
            order_restaurants = all_restaurants
            for product in order.products.all():
                current_restaurants = set()
                for restaurant_menu_item in restaurant_menu_items:
                    if product.product == restaurant_menu_item.product:
                        current_restaurants.add(restaurant_menu_item.restaurant)
                order_restaurants = order_restaurants & current_restaurants
            order.restaurants = order_restaurants
        return self


class Order(models.Model):
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'

    STATUSES = [
        (OPEN, 'Необработанный'),
        (CLOSED, 'Обработанный'),
    ]
    OFFLINE = 'OFFLINE'
    ONLINE = 'ONLINE'
    UNDEFINED = 'UNDEFINED'
    PAYMENT_METHODS = [
        (OFFLINE, 'Наличными'),
        (ONLINE,  'Онлайн'),
        (UNDEFINED, 'Нужно уточнить'),
    ]
    firstname = models.CharField('Имя', max_length=200)
    lastname = models.CharField('Фамилия', max_length=200)
    phonenumber = PhoneNumberField('Номер телефона', db_index=True)
    address = models.CharField('Адрес', max_length=200)
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUSES,
        default=OPEN,
        db_index=True,
        )
    comment = models.TextField('Комментарий', blank=True)
    registrated_at = models.DateTimeField(
        'Дата создания',
        default=timezone.now,
        db_index=True,
        )
    called_at = models.DateTimeField(
        'Дата звонка',
        null=True,
        blank=True,
        db_index=True,
        )
    delivered_at = models.DateTimeField(
        'Дата доставки',
        null=True,
        blank=True,
        db_index=True,
        )
    payment_method = models.CharField(
        'Способ оплаты',
        max_length=20,
        choices=PAYMENT_METHODS,
        default=UNDEFINED,
        db_index=True,
        )
    available_restaurants = models.ManyToManyField(
        Restaurant,
        verbose_name='Доступные рестораны',
        blank=True,
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.SET_NULL,
        related_name='orders',
        verbose_name='Выбранный ресторан',
        null=True,
        blank=True,
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'{self.firstname} {self.lastname} {self.address}'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Позиция в заказе',
        )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name='Продукт',
        )
    quantity = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(limit_value=1)],
        )
    cost = models.DecimalField(
        'Cтоимость позиции в заказе',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
