from multiprocessing import AuthenticationError
from typing import Any, Dict, Optional
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView, CreateView, FormView, DetailView
from .forms import CheckoutForm, CustomerregisForm, CustomerloginForm, ForgotPasswordForm, PasswordResetForm
from django.urls import reverse_lazy, reverse
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from .utils import password_reset_token
from django.core.mail import send_mail
from django.http import JsonResponse
from django.conf import settings
import razorpay


# Create your views here.
class Ecommixin(object):
    def dispatch(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id")

        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():

                cart_obj.customer = request.user.customer
                cart_obj.save()

        return super().dispatch(request, *args, **kwargs)


class HomeView(Ecommixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        all_products = Product.objects.all().order_by("-id")
        paginator = Paginator(all_products, 25)
        page_number = self.request.GET.get("page")
        product_list = paginator.get_page(page_number)

        context['product_list'] = product_list
        return context


class AboutView(Ecommixin, TemplateView):
    template_name = 'about.html'


class ContactView(Ecommixin, TemplateView):
    template_name = 'contact.html'


class CategoryView(Ecommixin, TemplateView):
    template_name = 'category.html'

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        context['allcate'] = Category.objects.all()
        context['cartproducts'] = CartProduct.objects.all()
        return context


class ProductdetailView(Ecommixin, TemplateView):
    template_name = 'productdetails.html'

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs['slug']
        product = Product.objects.get(slug=slug)
        product.view_count += 1
        product.save()
        context['product'] = product
        return context


class AddtocartView(Ecommixin, TemplateView):
    template_name = 'addtocart.html'
    success_url = reverse_lazy('ecommapp:home')

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        # get product  id from requested url
        product_id = self.kwargs["pro_id"]
        # get product
        product_obj = Product.objects.get(id=product_id)

        # check if cart exist
        cart_id = self.request.session.get("cart_id", None)
        print("ggggggggggggggg", cart_id)
        if cart_id:
            check = Cart.objects.filter(id=cart_id)
            print(check, cart_id)
            if len(check) > 0:
                cart = Cart.objects.get(id=cart_id)
                this_product_in_cart = cart.cartproduct_set.filter(
                    product=product_obj)
                if len(this_product_in_cart) > 0:
                    print("ggggggggggggggg")
                    cartproduct = this_product_in_cart.last()
                    cartproduct.quantity += 1
                    cartproduct.sub_total += product_obj.selling_price
                    cartproduct.save()
                    cart.total += product_obj.selling_price
                    cart.save()
                else:
                    print("ggggggggggggggg")
                    cartproduct = CartProduct.objects.create(
                        cart=cart, product=product_obj, rate=product_obj.selling_price, sub_total=product_obj.selling_price, quantity=1)
                    cart.total += product_obj.selling_price
                    cart.save()
            else:
                print("ggggggggggggggg")
                Cart_Obj = Cart.objects.create(total=0)
                self.request.session.__setitem__("cart_id", Cart_Obj.id)
        else:
            print("ggggggggggggggg")
            Cart_Obj = Cart.objects.create(total=0)
            self.request.session.__setitem__("cart_id", Cart_Obj.id)
        return context


class MycartView(Ecommixin, TemplateView):

    template_name = 'mycart.html'

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)

        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = None
        context['cart'] = cart

        return context


def ManagecartView(request, **kwargs,):
    cp_id = kwargs['cp_id']
    action = kwargs['cp_action']
    cart_product_obj = CartProduct.objects.get(id=cp_id)
    cart_obj = cart_product_obj.cart
    if action == 2:
        cart_product_obj.quantity += 1
        cart_product_obj.sub_total += cart_product_obj.rate
        cart_product_obj.save()
        cart_obj.total += cart_product_obj.rate
        cart_obj.save()
    elif action == 1:
        cart_product_obj.quantity -= 1
        cart_product_obj.sub_total -= cart_product_obj.rate
        cart_product_obj.save()
        cart_obj.total -= cart_product_obj.rate
        cart_obj.save()
        if cart_product_obj.quantity == 0:
            cart_obj.total -= cart_product_obj.sub_total
            cart_product_obj.delete()

        else:
            pass
        cart_obj.save()

    return redirect('ecomapp:mycart')


class MycheckView(Ecommixin, CreateView):
    template_name = 'checkout.html'
    form_class = CheckoutForm
    success_url = reverse_lazy("ecomapp:home")



    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.customer:
            pass
        else:
            return redirect("/login/?next=/checkout/")
        return super().dispatch(request, *args, **kwargs)

    
    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id")
        if cart_id:

            cart_obj = Cart.objects.get(id=cart_id)
        else:
            cart_obj = None

        context['cart'] = cart_obj
        return context

    def form_valid(self, form):
        cart_id = self.request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            form.instance.cart = cart_obj
            form.instance.discount = 0
            form.instance.subtotal = cart_obj.total
            form.instance.total = cart_obj.total
            form.instance.order_status = 'ORDER RECEVIED'
            del self.request.session["cart_id"]
            Cart_Obj = Cart.objects.create(total=0)
            self.request.session.__setitem__("cart_id", Cart_Obj.id)
            pm= form.cleaned_data.get('paymentmethod')
            order=form.save()
            if pm == 'RAZORPAY':
                return redirect(reverse("ecomapp:razorpayrequest") + '?o_id=' +str(order.id))
        else:
            return redirect("ecomapp:home")
        pm= form.cleaned_data.get('paymentmethod')
        order=form.save()
        if pm == 'RAZORPAY':
             return redirect(reverse("ecomapp:razorpayrequest") + '?o_id=' +str(order.id))
        return super().form_valid(form)

   
class CustomerregisView(CreateView):
    template_name = 'customerregister.html'
    form_class = CustomerregisForm
    success_url = reverse_lazy('ecomapp:home')

    def form_valid(self, form, **kwargs):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        email = form.cleaned_data.get('email')
        user = User.objects.create_user(username, email, password)
        form.instance.user = user
        login(self.request, user)

        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id")
        return super().form_valid(form)
    # def get_success_url(self) :
    #    if 'next' in self.request.GET:
    #        next_url=self.request.GET.get('next')
    #        return next_url
    #    else:
    #        self.success_url


class CustomerlogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('ecomapp:home')


class Customerloginview(FormView):
    template_name = 'customerlogin.html'
    form_class = CustomerloginForm
    success_url = reverse_lazy('ecomapp:home')

    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        psword = form.cleaned_data["password"]

        usr = authenticate(username=uname, password=psword)

        if usr is not None and Customer.objects.filter(user=usr).exists():
            login(self.request, usr)

        else:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Invalid credentials"})

        return super().form_valid(form)

    # def get_success_url(self) :
    #    if 'next' in self.request.GET:
    #        next_url=self.request.GET.get('next')
    #        return next_url
    #    else:
    #        self.success_url


class profileView(TemplateView):
    template_name = 'customerprofile.html'
    success_url = reverse_lazy('ecomapp:home')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            pass
        else:

            return redirect('/adminlogin/')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        customer = self.request.user.customer
        context['customer'] = customer
        orders = Order.objects.filter(cart__customer=customer).order_by("-id")
        context['orders'] = orders
        return context


class OrderdetailView(DetailView):
    template_name = 'customerorderdetail.html'
    model = Order
    context_object_name = 'ord_obj'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            order_id = self.kwargs["pk"]
            order = Order.objects.get(id=order_id)
            if request.user.customer != order.cart.customer:
                return redirect("ecomapp:profile")
        else:

            return redirect('/login/?next=/profile/')
        return super().dispatch(request, *args, **kwargs)


class SearchView(TemplateView):
    template_name = 'search.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        kw = self.request.GET.get('keyword')
        results = Product.objects.filter(Q(title__icontains=kw) | Q(
            descripitation__icontains=kw) | Q(return_policy__icontains=kw))
        context['results'] = results

        return context
#


class ForgotPasswordView(FormView):
    template_name = 'forgotpassword.html'
    form_class = ForgotPasswordForm
    success_url = "/forgot-password/?m=s"

    def form_valid(self, form) -> HttpResponse:
        email = form.cleaned_data.get("email")
        print(email, "------------------------...")
        url = self.request.META['HTTP_HOST']
        # get customer and then user
        customer = Customer.objects.get(user__email=email)
        user = customer.user
        # send mail to the user with email
        text_content = 'Please Click the link below to reset your password. '
        html_content = url + "/password-reset/" + email + \
            "/" + password_reset_token.make_token(user) + "/"
        send_mail(
            'Password Reset Link | Django Ecommerce',
            text_content + html_content,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        return super().form_valid(form)


class PasswordResetView(FormView):
    template_name = "passwordreset.html"
    form_class = PasswordResetForm
    success_url = "/login/"

    def dispatch(self, request, *args, **kwargs):
        email = self.kwargs.get("email")
        user = User.objects.get(email=email)
        token = self.kwargs.get("token")
        if user is not None and password_reset_token.check_token(user, token):
            pass
        else:
            return redirect(reverse("ecomapp:passworforgot") + "?m=e")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        password = form.cleaned_data['new_password']
        email = self.kwargs.get("email")
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()
        return super().form_valid(form)


class Razorpay(View):
   
   def get(self, request,*args, **kwargs):
    o_id=request.GET.get('o_id')
    order=Order.objects.get(id=o_id)
    # user=razorpay.Client(auth=(settings.RAZOR_KEY_ID ,settings.RAZOR_KEY_SECRET))
    # payment=user.order.create({"amount":Cart.total,"currency":'INR','payment_capture':1})
    print('*********************1223333334455')
    order.razorpay_order_id=['order_id.id']
    order.save()
    context={
        "order": order,
        # 'payment':payment

    }

    return render(request, 'razorpayment.html',context)
