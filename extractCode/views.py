from django.shortcuts import render
from google_api import authenticate_gmail, get_latest_code, get_household_link
import subprocess
import os

def netflix_otp_extractor(request):
    otp = ''
    houseHold_link = ''
    message=''
    if request.method == "POST":
        email = request.POST.get("email")
        service = authenticate_gmail()

        # Get OTP link
        otp = get_latest_code(service, email)
        if otp:
            print("OTP code in views:", otp)

        # If no OTP, try household link
        if not otp:
            houseHold_link = get_household_link(service, email)
            if houseHold_link:
                print("Household link found:", houseHold_link)

        # If both not found
        if not otp and not houseHold_link:
            message = "No OTP found neither household link. Try again..."

    return render(request, "extractCode/Netflix_Otp.html", {
        "selenium_output": otp,
        "houseHold_output": houseHold_link,
        "message": message
    })