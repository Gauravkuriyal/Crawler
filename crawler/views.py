from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from django.http import JsonResponse, HttpResponseBadRequest
from django.core.exceptions import ValidationError

# Create your views here.

# from .models import *
# from .serializers import *


@api_view(["POST", "GET"])
def crawler(request):
    try:
        emails = set()
        phoneNumbers = set()
        if request.method == "POST":
            crawlerSelector = request.data.get("crawlerSelector","link")
            from crawler.crawlerV2 import site_crawler, file_crawler, crawl_urls_for_files
            from crawler.utlisFunction import handle_uploaded_file, filter_valid_phone_numbers

            # file_upload = request.data.get("file_upload", None)
            if crawlerSelector == "link":
                site_url = request.data.get("site_url", None)
                emails, phoneNumbers = site_crawler(site_url)
            elif crawlerSelector == "file":
                files = request.FILES.getlist('file_upload')
                for file in files:
                    try:
                        handle_uploaded_file(file)
                        Nemails, NphoneNumbers = file_crawler(f'media/{file.name}')
                        emails = emails.union(Nemails)
                        phoneNumbers = NphoneNumbers.union(NphoneNumbers)
                    except ValidationError as e:
                        pass
            
            elif crawlerSelector == "linkfile":
                urls = request.data.get('linkfile_urls')
                # for file in files:
                # print(urls)
                try:
                    urls = urls.split(",")
                    # print(urls)
                    Nemails, NphoneNumbers = crawl_urls_for_files(urls)
                    # handle_uploaded_file(file)
                    # Nemails, NphoneNumbers = file_crawler(f'media/{file.name}')
                    emails = emails.union(Nemails)
                    phoneNumbers = NphoneNumbers.union(NphoneNumbers)
                except ValidationError as e:
                    pass

            # print("Before validation : ",phoneNumbers)
            # phoneNumbers = filter_valid_phone_numbers(phoneNumbers)
            # print("After validation : ",phoneNumbers)
            context = {
                "data" : True,
                "emails" : emails,
                "phoneNumbers" : phoneNumbers
            }
            return render(request,"crawler.html",context)
            return JsonResponse({
                "status": "success", 
                "message": "something went wrong", 
                "data": {
                    "emails" : emails or None,
                    "phoneNumbers" : phoneNumbers or None,
                }
            })
        context = {
            "data" : False
        }
    except Exception as e:
        print(e)
        print("exception")
        context = {
            "data" : False
        }
        return render(request,"crawler.html",context)
        # return JsonResponse({"status": "failure", "message": "something went wrong"})

    return render(request,"crawler.html")
