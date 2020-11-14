from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#from webdriver_manager.chrome import ChromeDriverManager 
import time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __rep__(self):
        return 'Task %r' % self.id


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        task_content = request.form['content']
        new_task = Todo(content=task_content)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return "There was an issue adding your task"
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template("index.html", tasks=tasks)


@app.route("/delete/<int:id>")
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return "There was a problem deleting that task"


@app.route("/update/<int:id>", methods=["POST", "GET"])
def update(id):
    task_to_update = Todo.query.get_or_404(id)
    if request.method == "POST":
        task_to_update.content = request.form['content']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return "There was a problem updating that task"
    else:
        return render_template("update.html", task=task_to_update)

#####################################################


@app.route("/checkprice", methods=["POST"])
def checkPrice():
    options = Options()
    options.headless = True
    browser = webdriver.Firefox(
        options=options, executable_path=r'C:/Users/Olga/Documents/geckodriver.exe')
    url = request.args.get('url')
    htmlTag = request.args.get('tag')
    print(url, htmlTag)
    browser.get(url)
    time.sleep(5)  # js loading page waiting
    html = browser.page_source
    soup = BeautifulSoup(html, 'lxml')
    result = soup.findAll(attrs={"class": htmlTag})
    print(result)
    return jsonify(price=result[0].get_text())

@app.route("/doctoravailable", methods=["GET"])
def doctorAvailable():
    chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.binary_location = '/app/.apt/usr/bin/google_chrome'
    #browser = webdriver.Chrome(ChromeDriverManager().install()) doesnt work on heroku
    browser = webdriver.Chrome(executable_path="app/.chromedriver/bin/chromedriver", chrome_options=chrome_options)
    #url = request.args.get('url')
    #htmlTag = request.args.get('tag')
    #print(url, htmlTag)
    url = "https://gorzdrav.spb.ru/service-free-schedule#%5B%7B%22district%22:%2217%22%7D,%7B%22lpu%22:%22265%22%7D,%7B%22speciality%22:%222080%22%7D,%7B%22doctor%22:%22138%22%7D%5D"
    htmlTag = "datepicker-slot"
    browser.get(url)
    time.sleep(5)  # js loading page waiting
    html = browser.page_source
    soup = BeautifulSoup(html, 'lxml')
    result = soup.findAll(attrs={"class": htmlTag})
    print(result) 
    browser.quit()
    return jsonify(slot=result[0].get_text())


if __name__ == "__main__":
    app.run(debug=True)
