from flask import Flask, session, redirect, url_for, escape, request, render_template
import cartAPI


# configuration
DATABASE = 'addtocart.db'


app = Flask(__name__)


def connect_db():
        return sqlite3.connect(app.config['DATABASE'])

        
def login(email, password):
        cartAPI.sessionKey = cartAPI.login(email, password)      


@app.route('/', methods=['GET', 'POST'])
def index():
        if len(cartAPI.sessionKey) == 0:
                redirect(url_for('login_page'))
        itemList = cartAPI.getFavourites(cartAPI.sessionKey)
        count = len(itemList)
        if request.method == 'POST':
                productId = request.form['item']             
                amount = cartAPI.modifyBasket(cartAPI.sessionKey, productId)
        cartSummary = cartAPI.getShoppingCartSummary(cartAPI.sessionKey)
        return render_template('index.html', itemList=itemList, count=count, cartSummary=cartSummary)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
        if request.method == 'POST':
                email = request.form['email']
                password = request.form['password']
                login(email, password)
                return redirect(url_for('index'))
        return render_template('login.html')


@app.route('/cart')
def cart():
	cartItems = cartAPI.getShoppingCart(cartAPI.sessionKey)
	cartSummary = cartAPI.getShoppingCartSummary(cartAPI.sessionKey)
	count = len(cartItems)
	return render_template('cart.html', cartItems=cartItems, count=count, cartSummary=cartSummary)


@app.errorhandler(404)
def not_found(error):
        return render_template('error.html'), 404     


@app.route('/logout')
def logout():
        # remove the username from the session if it's there
        cartAPI.sessionKey = ''
        return redirect(url_for('index'))

   	
if __name__ == '__main__':
	app.debug = True	
	app.run()
