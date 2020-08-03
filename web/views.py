from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from json import JSONEncoder
from django.utils.crypto import get_random_string
from django.views.decorators.http import require_POST
from postmarker.core import PostmarkClient
from .models import Expense, Income, Token, User, Passwordresetcodes
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from .utils import grecaptcha_verify, RateLimited


# Create your views here.


@csrf_exempt
def index(request):
    return render(request, 'index.html', context=None)


@csrf_exempt
def logout(request):
    return render(request, 'index.html', context=None)


@csrf_exempt
@require_POST
def login(request):
    # check if POST objects has username and password
    if request.POST.has_key('username') and request.POST.has_key('password'):
        username = request.POST['username']
        password = request.POST['password']
        this_user = get_object_or_404(User, username=username)
        if (check_password(password, this_user.password)):  # authentication
            this_token = get_object_or_404(Token, user=this_user)
            token = this_token.token
            context = {}
            context['result'] = 'ok'
            context['token'] = token
            # return {'status':'ok','token':'TOKEN'}
            return JsonResponse(context, encoder=JSONEncoder)
        else:
            context = {}
            context['result'] = 'error'
            # return {'status':'error'}
            return JsonResponse(context, encoder=JSONEncoder)


# register (web)

@csrf_exempt
def register(request):
    if 'requestcode' in request.POST:
        # is this spam? check reCaptcha
        if not grecaptcha_verify(request):  # captcha was not correct
            context = {
                'message': 'کپچای گوگل درست وارد نشده بود. شاید ربات هستید؟ کد یا کلیک یا تشخیص عکس زیر فرم را درست پر کنید. ببخشید که فرم به شکل اولیه برنگشته!'}  # TODO: forgot password
            return render(request, 'register.html', context)

        # duplicate email
        if User.objects.filter(email=request.POST['email']).exists():
            context = {
                'message': 'متاسفانه این ایمیل قبلا استفاده شده است. در صورتی که این ایمیل شما است، از صفحه ورود گزینه فراموشی پسورد رو انتخاب کنین. ببخشید که فرم ذخیره نشده. درست می شه'}  # TODO: forgot password
            # TODO: keep the form data
            return render(request, 'register.html', context)
        # if user does not exists
        if not User.objects.filter(username=request.POST['username']).exists():
            code = get_random_string(length=32)
            now = datetime.now()
            email = request.POST['email']
            password = make_password(request.POST['password'])
            username = request.POST['username']
            temporarycode = Passwordresetcodes(
                email=email, time=now, code=code, username=username, password=password)
            temporarycode.save()

            postmark = PostmarkClient(server_token='6d84aa49-8b38-412c-afb0-d44fe8ca8bd0')
            postmark.emails.send(
                From='bynq2@kleogb.com',
                To=email,
                Subject="فعالسازی اکانت بستون",
                HtmlBody=f"برای فعال کردن اکانت بستون خود روی لینک روبرو کلیک کنید: <a href=\"{request.build_absolute_uri('/register/')}?code={code}\">لینک فعالسازی</a>"
            )

            message = 'ایمیلی حاوی لینک فعال سازی اکانت به شما فرستاده شده، لطفا پس از چک کردن ایمیل، روی لینک کلیک کنید.'
            context = {
                'message': message}
            return render(request, 'index.html', context)
        else:
            context = {
                'message': 'متاسفانه این نام کاربری قبلا استفاده شده است. از نام کاربری دیگری استفاده کنید. ببخشید که فرم ذخیره نشده. درست می شه'}  # TODO: forgot password
            # TODO: keep the form data
            return render(request, 'register.html', context)
    elif 'code' in request.GET:  # user clicked on code
        code = request.GET['code']
        if Passwordresetcodes.objects.filter(
                code=code).exists():  # if code is in temporary db, read the data and create the user
            new_temp_user = Passwordresetcodes.objects.get(code=code)
            newuser = User.objects.create(username=new_temp_user.username, password=new_temp_user.password,
                                          email=new_temp_user.email)
            this_token = get_random_string(length=48)
            token = Token.objects.create(user=newuser, token=this_token)
            # delete the temporary activation code from db
            Passwordresetcodes.objects.filter(code=code).delete()
            context = {
                'message': 'اکانت شما ساخته شد. توکن شما {} است. آن را ذخیره کنید چون دیگر نمایش داده نخواهد شد! جدی!'.format(
                    token)}
            return render(request, 'index.html', context)
        else:
            context = {
                'message': 'این کد فعال سازی معتبر نیست. در صورت نیاز دوباره تلاش کنید'}
            return render(request, 'register.html', context)
    else:
        context = {'message': ''}
        return render(request, 'register.html', context)


@csrf_exempt
def submit_expense(request):
    """submit expense"""

    this_token = request.POST['token']
    this_user = User.objects.filter(token__token=this_token).get()

    if 'date' not in request.POST:
        date = datetime.datetime.now()
    else:
        date = request.POST['date']

    Expense.objects.create(user=this_user, amount=request.POST['amount'], date=date, text=request.POST['text'])
    return JsonResponse({
        "status": 200
    }, encoder=JSONEncoder)


@csrf_exempt
def submit_income(request):
    """submit income"""

    this_token = request.POST['token']
    this_user = User.objects.filter(token__token=this_token).get()

    if 'date' not in request.POST:
        date = datetime.datetime.now()
    else:
        date = request.POST['date']

    Income.objects.create(user=this_user, amount=request.POST['amount'], date=date, text=request.POST['text'])
    return JsonResponse({
        "status": 200
    }, encoder=JSONEncoder)
