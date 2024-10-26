from flask import Flask, render_template, request, redirect, url_for, session
import requests as r
import bs4
from datetime import datetime
import time
import schedule
import matplotlib.pyplot as plt
import os
from threading import Thread
import pyttsx3


#   SAMPLE KEYS   B0D841Z76B            
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Specify the path to the product data file                 
PRODUCT_DATA_FILE = os.path.join(os.path.dirname(__file__), 'product_data.txt')

Price = []
product_dict = {}
def inputProduct():
    global product_dict
    with open(PRODUCT_DATA_FILE, 'r') as f:
        for line in f.readlines():
            key, value_pro = line.strip().split(' ', 1)
            product_dict[key] = value_pro

   # print(f"Starting Tracking products')
    #robo = pyttsx3.init()
    #print("h")
    #robo.say(f"i am starting Tracking the products")
    #robo.runAndWait()

def PriceTracker():
    global product_dict
    current_time = datetime.now().strftime('%H:%M:%S')
    # robo1 = pyttsx3.init()
    # print("ukllflklekk ")    
    # #robo1.say(f"Tracking prices at {current_time}")
    # robo1.runAndWait()


    for prodt in product_dict:
        url = f'https://www.amazon.in/dp/{prodt}'

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }

        res = r.get(url, headers=headers)

        html_code = bs4.BeautifulSoup(res.content, 'html.parser')

        price = html_code.find(attrs={'class': 'a-price-whole'})
        if price:
            price_value = price.text.strip().replace(',', '').replace('.', '')
            print("j")
            AI = pyttsx3.init()
            AI.say(f"At the time of {current_time} The price of {product_dict[prodt]} is {price_value}")
            AI.runAndWait()
            Price.append(int(price_value))

def ploting():
    if Price:
        x = range(1, len(Price) + 1)
        y = Price
        plt.clf()  # Clear the current figure
        plt.plot(x, y, marker='o')
        plt.xlabel('Time Interval')
        plt.ylabel('Price')
        #plt.ylim(0 , 200000)
        plt.title('Price Tracking')
        plt.pause(0.1)

def scrapingANDploting():
    while True:
        inputProduct()  # Load product data from the file
        PriceTracker()
        ploting()
        time.sleep(10)  # Wait 10 seconds before the next scrape

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/track', methods=['POST'])
def track_prices():
    if request.method == 'POST':
        product_ids = request.form.getlist('ProductID[]')
        product_names = request.form.getlist('ProductName[]')

        # Write product data to a file
        with open(PRODUCT_DATA_FILE, 'w') as f:
            for product_id, product_name in zip(product_ids, product_names):
                f.write(f'{product_id} {product_name}\n')

        # Start the price tracking thread
        session['tracking'] = True  # Set session variable to track status
        Thread(target=scrapingANDploting, daemon=True).start()  # Run the tracking function in a separate thread
        return redirect(url_for('index'))

@app.route('/stop')
def stop_tracking():
    session['tracking'] = False  # Change tracking status to False
   # return redirect(url_for('index'))
    return "<h1> TRACING IS STOP <h1/>"


if __name__ == '__main__':
    plt.ion()  # Enable interactive mode for matplotlib
    plt.show()  # Show the plot
    app.run(debug=True)
