from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>Калькулятор</h1>
    <form method="post">
        <input type="text" name="num1" placeholder="Число 1" required>
        <input type="text" name="num2" placeholder="Число 2" required>
        <button type="submit">Сложить</button>
    </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)
