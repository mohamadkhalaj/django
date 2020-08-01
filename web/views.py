from django.shortcuts import render
from django.http import JsonResponse
from json import JSONEncoder
from .models import Expense, Income, Token, User
import datetime
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

@csrf_exempt
def submit_expense(request):
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
