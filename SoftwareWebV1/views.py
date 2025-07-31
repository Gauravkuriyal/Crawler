from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.shortcuts import redirect

from django.http import JsonResponse, HttpResponseBadRequest

@api_view(["GET"])
def home(request):

    return redirect('crawlers/')
    return render(request,"index.html")
    return JsonResponse({
        "status" : "success",
        "message" : "Welcome"
    })