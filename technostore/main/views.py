from django.shortcuts import render, redirect
from django.http import HttpResponse
from main.models import TechnoAdmin
from main.models import NewCategory
from main.models import Tag
from main.models import Color
from django.contrib.auth.hashers import make_password,check_password
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string
from main.models import Product
from django.contrib import messages
from django.utils.translation import activate
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from random import sample
from django.utils.text import slugify
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from main.models import Contact
from collections import OrderedDict



#  paypal paymenti qurasdira bilmedim  vaxt catmadi 
import paypalrestsdk
from django.shortcuts import render, redirect
from django.conf import settings

paypalrestsdk.configure({  
    "mode": "sandbox",  
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})





def sepet(request):
    products_in_cart = request.session.get('sepet', [])
    total_price = sum(float(product['sale_price']) for product in products_in_cart)

    return render(request, 'main/shop-cart.html', {'products_in_cart': products_in_cart, 'total_price': total_price})








def sepete_ekle(request, product_id):
    product = Product.objects.get(id=product_id)
    products_in_cart = request.session.get('sepet', [])
    products_in_cart.append({'id': product.id, 'title': product.title, 'primary_photo_url': product.primary_photo.url, 'sale_price': str(product.sale_price)})

    request.session['sepet'] = products_in_cart
    return redirect('home')






def sepetten_cikar(request, product_id):
    products_in_cart = request.session.get('sepet', [])
    for index, product in enumerate(products_in_cart):
        if product['id'] == product_id:
            del products_in_cart[index]
            break
    request.session['sepet'] = products_in_cart
    return redirect('sepet')






def change_language(request, language_code):
    activate(language_code)
    response = redirect(request.META.get('HTTP_REFERER'))
    response.set_cookie('django_language', language_code)
    return response






def product_detail(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    return render(request, 'main/single-product.html', {'product': product})







def home(request):

    products   = Product.objects.all().order_by('-id')[:12]

    all_products = list(Product.objects.all())
    random_products = sample(all_products, min(len(all_products), 12)) 
    categories = NewCategory.objects.filter(parent=None)[:5]
    return render(request, 'main/home.html', {'products': products,'random_products': random_products, 'categories': categories})







def shop(request, category_slug):
    category = get_object_or_404(NewCategory, slug=category_slug)
    products = Product.objects.filter(Q(parent_category=category) | Q(sub_category=category) | Q(sub_sub_category=category))

    colors = Color.objects.filter(product__in=products).distinct()


    unique_colors = {}
    for color in colors:
        if color.color not in unique_colors:
            unique_colors[color.color] = color


    unique_colors_ordered = OrderedDict(sorted(unique_colors.items()))


    brands = Product.objects.filter(Q(parent_category=category) | Q(sub_category=category) | Q(sub_sub_category=category)).values_list('brand', flat=True).distinct()



    unique_brands = {}
    for brand in brands:
        if brand not in unique_brands:
            unique_brands[brand] = brand


    unique_brands_ordered = OrderedDict(sorted(unique_brands.items()))


    page_number = request.GET.get('page', 1)
    paginator = Paginator(products, 6)

    try:
        page_products = paginator.page(page_number)
    except PageNotAnInteger:
        page_products = paginator.page(1)
    except EmptyPage:
        page_products = paginator.page(paginator.num_pages)

    return render(request, 'main/shop.html', {'products': page_products, 'colors': unique_colors_ordered.values(), 'brands': unique_brands_ordered.items()})







# home page header category tree ajax 
def get_categories(request, category_slug):
    if category_slug == 'all-categories':
        all_categories = NewCategory.objects.all()
        categories_html = render_to_string('main/categories.html', {'categories': all_categories})
    else:
        category = NewCategory.objects.get(slug=category_slug)
        categories_html = render_to_string('main/categories.html', {'category': category})

    return JsonResponse({'categories_html': categories_html})




# send mail
def contact_form(request):
    if request.method == 'POST':
        name = request.POST.get('name-contact', '')
        lastname = request.POST.get('password-contact', '')
        subject = request.POST.get('subject-contact', '')
        comment = request.POST.get('comment-contact', '')

        contact = Contact(name=name, lastname=lastname, subject=subject, comment=comment)
        contact.save()


        sender_email = settings.EMAIL_HOST_USER  
        send_mail(subject, comment, sender_email, ['seymurss2002@gmail.com'])
        
    
    return render(request, 'main/contact.html')







# home page category filter  product
def fetch_products(request):
    category_slug = request.GET.get('category_slug')

    if category_slug:
        selected_category = get_object_or_404(NewCategory, slug=category_slug)
        filter_products = Product.objects.filter(parent_category=selected_category)[:8]
    else:
        filter_products = Product.objects.all()

    product_html = render_to_string('main/prj.html', {'filter_products': filter_products})
    return JsonResponse({'product_html': product_html})





# order page 
def order(request):
    return render(request,'dashboard/dashboard-order.html')




 # customer page 
def allcustomer(request):
    return render(request,'dashboard/dashboard-all-customer.html')




# search product function
def search(request):    
    search_query = request.GET.get('search', '')
    search_products = Product.objects.filter(
        Q(title__icontains=search_query) |
        Q(parent_category__title__icontains=search_query) |
        Q(sub_category__title__icontains=search_query) |
        Q(sub_sub_category__title__icontains=search_query)
    ).distinct()

    paginator = Paginator(search_products, 12)  

    page_number = request.GET.get('page')
    try:
        search_products = paginator.page(page_number)
    except PageNotAnInteger:
        search_products = paginator.page(1)
    except EmptyPage:
        search_products = paginator.page(paginator.num_pages)

    return render(request, 'main/search.html', {'search_products': search_products, 'search_query': search_query})






# contact page function
def contact(request):
    return render(request,'main/contact.html')






# delete product 
def delete_product(request, product_id):
    if request.method == 'POST':
        try:
            product = Product.objects.get(id=product_id)
            product.delete()
            messages.success(request, 'Ürün başarıyla silindi.')
        except Product.DoesNotExist:
            messages.error(request, 'Ürün bulunamadı.')
        return redirect('allproduct') 
    else:
        return redirect('allproduct') 




# update product 
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        brand = request.POST.get('brand')
        slug = slugify(title)
        product_count = request.POST.get('product_count')
        sku = request.POST.get('sku')
        regularr_price = request.POST.get('regular_price')
        sale_price = request.POST.get('sale_price')
        description = request.POST.get('description')
        
        product.title = title
        product.brand = brand
        product.slug  = slug
        product.product_count = product_count
        product.sku   = sku
        product.regular_price = regularr_price
        product.sale_price = sale_price
        product.description = description
        
        if 'primary_photo' in request.FILES:
          product.primary_photo = request.FILES['primary_photo']
        if 'photo1' in request.FILES:
          product.photo1 = request.FILES['photo1']
        if 'photo2' in request.FILES:
          product.photo2 = request.FILES['photo2']
        if 'photo3' in request.FILES:
          product.photo3 = request.FILES['photo3']
        if 'photo4' in request.FILES:
          product.photo4 = request.FILES['photo4']  

        product.save()
        
        return redirect('allproduct')
    
    else:
      
        return render(request, 'dashboard/update.html', {'product': product})
    




def update_data(request, product_id):
    product = Product.objects.get(id=product_id)
    categories = NewCategory.objects.all()
    return render(request, 'dashboard/update.html', {'product': product, 'categories' : categories })





# all product
def allproduct(request):
    if request.method == 'POST':
        parent_category_id = request.POST.get('parent_category')
        sub_category_id = request.POST.get('sub_category')
        sub_sub_category_id = request.POST.get('sub_sub_category')

        if parent_category_id and sub_category_id and sub_sub_category_id:
            products = Product.objects.filter(
                parent_category_id=parent_category_id,
                sub_category__id=sub_category_id,
                sub_sub_category_id=sub_sub_category_id
            )
        elif parent_category_id and sub_category_id:
            products = Product.objects.filter(
                parent_category_id=parent_category_id,
                sub_category__id=sub_category_id
            )
        elif parent_category_id:
            products = Product.objects.filter(
                parent_category_id=parent_category_id
            )
        else:
            products = Product.objects.all()

        categories = NewCategory.objects.all()
        return render(request, 'dashboard/dashboard-all-product.html', {'products': products, 'categories': categories})
    else:
        categories = NewCategory.objects.all()
        products = Product.objects.all() 
        return render(request, 'dashboard/dashboard-all-product.html', {'categories': categories, 'products': products})






#admin page add product page function
def addproduct(request):
    categories = NewCategory.objects.all()
    return render(request, 'dashboard/dashboard-add-product.html', {'categories': categories})




#admin page  add category  function
def add_category(request):
    if request.method == 'POST':
        category_title = request.POST.get('title')
        category_keywords = request.POST.get('categoryType')
        category_description = request.POST.get('categoryType')  
        category_icon = request.POST.get('icon')
        category_slug = request.POST.get('slug')

        parent_id = request.POST.get('parent')  

        if parent_id:
            parent_category = NewCategory.objects.get(pk=parent_id)
        else:
            parent_category = None

        new_category = NewCategory.objects.create(
            title=category_title,
            category_keywords=category_keywords,
            category_description=category_description,
            icon=category_icon,
            slug=category_slug,
            parent=parent_category
        )

        return redirect('add_category')

    categories = NewCategory.objects.all()
    return render(request, 'dashboard/dashboard-category.html', {'categories': categories})





#admin page Category sort function
def category(request):
    categories = NewCategory.objects.all()
    return render(request, 'dashboard/dashboard-category.html', {'categories': categories})





# selected category delete function
def delete_selected_categories(request):
    if 'selected_categories' in request.POST:
        selected_category_ids = request.POST.getlist('selected_categories')
        NewCategory.objects.filter(id__in=selected_category_ids).delete()
    return redirect('category')



# ajax auto category  add product selected functons
def get_sub_categories(request, parent_id):
    parent_category = NewCategory.objects.get(pk=parent_id)
    sub_categories = parent_category.get_children()
    data = {'sub_categories': [{'id': sub_category.id, 'title': sub_category.title} for sub_category in sub_categories]}
    return JsonResponse(data)


def get_sub_sub_categories(request, sub_category_id):
    sub_category = NewCategory.objects.get(pk=sub_category_id)
    sub_sub_categories = sub_category.get_children()
    data = {'sub_sub_categories': [{'id': sub_sub_category.id, 'title': sub_sub_category.title} for sub_sub_category in sub_sub_categories]}
    return JsonResponse(data)





# Admin manager Class  and functions
class TechnoAdminManager:
    @staticmethod
    # admin panel username ve password  
    def add_techno_admin(request):
        username = 'seymur'
        password = 'seymur2002'
        email = 'seymur@gmail.com'

        hashed_password = make_password(password)
        TechnoAdmin.objects.create(username=username, password=hashed_password, email=email)
        return HttpResponse("admin elave edildi !")




# admin login
    @staticmethod
    def login(request):
        error_message = None

        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            try:
                techno_admin = TechnoAdmin.objects.get(username=username)

                if check_password(password, techno_admin.password):
                    request.session['is_logged_in'] = True
                    return redirect('login')
                else:
                    error_message = "Invalid Username/Password"
            except ObjectDoesNotExist:
                error_message = "Invalid Username/Password"
        return render(request, "dashboard/admin.html", {'error_message': error_message})




# admin log out
    @staticmethod
    def adminlogout(request):
        request.session['is_logged_in'] = False
        logout(request)
        return redirect('home')



# add product 
def add_product(request):
    if request.method == 'POST':

        title = request.POST.get('title')
        brand = request.POST.get('brand')

        slug = slugify(title)
        product_count = request.POST.get('product_count')
        sku = request.POST.get('sku')
        stock_status = request.POST.get('stock_status')
        regular_price = request.POST.get('regular_price')
        sale_price = request.POST.get('sale_price')
        
        parent_category_id = request.POST.get('parent_category')
        sub_category_id = request.POST.get('sub_category')
        sub_sub_category_id = request.POST.get('sub_sub_category')
        

        parent_category_obj = NewCategory.objects.get(id=parent_category_id)
        sub_category_obj = NewCategory.objects.get(id=sub_category_id)
        sub_sub_category_obj = NewCategory.objects.get(id=sub_sub_category_id)

        description = request.POST.get('description')
        primary_photo = request.FILES.get('primary_photo')
        photo1 = request.FILES.get('photo1')
        photo2 = request.FILES.get('photo2')
        photo3 = request.FILES.get('photo3')
        photo4 = request.FILES.get('photo4')


        product_tags = request.POST.get('product_tags', '')
        tags_list = product_tags.split('|')
        print(tags_list)

        product_color = request.POST.get('product_colors', '')
        color_list = product_color.split('|')
        print(color_list)

 
        product = Product.objects.create(
            title=title,
            brand=brand,
            slug=slug,
            product_count=product_count,
            sku=sku,
            stock_status=stock_status,
            regular_price=regular_price,
            sale_price=sale_price,
            
            parent_category=parent_category_obj,
            sub_category=sub_category_obj,
            sub_sub_category=sub_sub_category_obj,

            description=description,
            primary_photo=primary_photo,
            photo1=photo1,
            photo2=photo2,
            photo3=photo3,
            photo4=photo4
        )

        for tag in tags_list:
            product.tags.create(tag=tag)

        for color in color_list:
            product.colors.create(color=color)


        messages.success(request, 'Product added successfully.')


        return redirect('allproduct')  

    else:

        categories = NewCategory.objects.all()
        return render(request, 'dashboard/dashboard-add-product.html', {'categories': categories}) 
    
