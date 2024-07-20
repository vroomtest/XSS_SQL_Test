from flask import Flask, render_template, request
import re

app = Flask(__name__)

def is_xss_attack(search_term):
    xss_patterns = [
        r'<script.*?>.*?</script.*?>',  
        r'<.*?on.*?=.*?>',  
        r'<.*?>'  
    ]
    for pattern in xss_patterns:
        if re.search(pattern, search_term, re.IGNORECASE):
            return True
    return False

def is_sql_injection(search_term):
    sql_patterns = [
        r'\' OR \'1\'=\'1',  
        r'\' OR 1=1',  
        r'--',  
        r';',  
        r'\'',  
    ]
    for pattern in sql_patterns:
        if re.search(pattern, search_term, re.IGNORECASE):
            return True
    return False

@app.route('/', methods=['GET','POST'])
def home():
    if request.method == 'POST':
        password = request.form['search_term']
        if is_xss_attack(search_term):
            return render_template('index.html', error='Error with search term')
        if is_sql_injection(search_term):
            return render_template('index.html',error='Error with search term')
        return render_template('result.html', search_term=search_term)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

# @app.route('/')
# def home():
    # return render_template('index.html')

# @app.route('/search', methods=['POST'])
# def search():
    # search_term = request.form['search_term']

    # if is_xss_attack(search_term):
        # return render_template('index.html', error='XSS attack detected. Please enter a valid search term.')

    # if is_sql_injection(search_term):
        # return render_template('index.html', error='SQL injection attack detected. Please enter a valid search term.')

    # return render_template('result.html', search_term=search_term)

# if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000)
