from django.shortcuts import render, redirect
from django.urls import reverse
from . import models

# ------------------ CRUD VIEWS ------------------
def landing_view(request):
    stocks = get_stock_prices()
    return render(request, "base.html", {"stocks": stocks})

def list_view(request):
    all_cars = models.Car.objects.all()
    context = {'all_cars': all_cars}
    return render(request, 'cars/list.html', context)


def add_view(request):
    if request.POST:
        brand = request.POST['brand']
        year = int(request.POST['year'])
        models.Car.objects.create(brand=brand, year=year)
        return redirect(reverse('cars:list'))
    else:
        return render(request, 'cars/add.html')


def delete_view(request):
    if request.POST:
        car_id = request.POST['car_id']
        try:
            models.Car.objects.get(id=car_id).delete()
            return redirect(reverse('cars:list'))
        except:
            print("Car not found")
            return redirect(reverse('cars:delete'))
    else:
        return render(request, 'cars/delete.html')


# ------------------ AI CHATBOT VIEW ------------------

from groq import Groq
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Initialize Groq client with your API key
client = Groq(api_key="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")

@csrf_exempt
def car_chatbot(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    data = json.loads(request.body.decode("utf-8"))
    user_msg = data.get("message", "").strip()

    if not user_msg:
        return JsonResponse({"reply": "Please ask something about cars!"})

    # Fetch all cars from database to give AI context
    all_cars = models.Car.objects.all()
    car_list = [f"{car.brand} ({car.year})" for car in all_cars]
    cars_text = ", ".join(car_list) if car_list else "No cars in database yet."

    # Create prompt for AI
    prompt = (
        f"You are a friendly car expert AI assistant.\n"
        f"Current cars in database: {cars_text}\n"
        f"Answer the user's question about cars in a concise and helpful way.\n"
        f"User: {user_msg}\nAI:"
    )

    # Call Groq API
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    reply = response.choices[0].message.content
    return JsonResponse({"reply": reply})

import yfinance as yf

def get_stock_prices():
    # List of tickers you want
    tickers = ["TSLA", "BMW.DE", "F"]  # BMW.DE for German stock
    stock_data = []

    for ticker in tickers:
        stock = yf.Ticker(ticker)
        price = stock.history(period="1d")["Close"].iloc[-1]
        change = price - stock.history(period="2d")["Close"].iloc[-2]
        stock_data.append({
            "name": ticker,
            "price": round(price, 2),
            "change": round(change, 2)
        })

    return stock_data
