from flask import Flask, render_template, request, jsonify
import requests
from flask_sqlalchemy import SQLAlchemy
import chardet

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news.db'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)

class NewsPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), default='general')

NEWS_API_KEY = 'your_api_key_here'  # Replace with your NewsAPI key
NEWS_API_URL = 'https://newsapi.org/v2/top-headlines'

def safe_render_template(template_name, **context):
    try:
        return render_template(template_name, **context)
    except UnicodeDecodeError:
        template_path = f"templates/{template_name}"
        with open(template_path, 'rb') as f:
            raw_content = f.read()
            encoding = chardet.detect(raw_content)['encoding'] or 'utf-8'
            content = raw_content.decode(encoding, errors='replace')
            return content

@app.route('/')
def index():
    default_category = 'general'
    preference = NewsPreference.query.first()
    if preference:
        default_category = preference.category
    return safe_render_template('index.html', default_category=default_category)

@app.route('/api/news')
def get_news():
    category = request.args.get('category', 'general')
    
    try:
        params = {
            'category': category,
            'country': 'us',
            'apiKey': NEWS_API_KEY
        }
        response = requests.get(NEWS_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        articles = data.get('articles', [])
        return jsonify({'articles': articles})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not NewsPreference.query.first():
            db.session.add(NewsPreference(category='general'))
            db.session.commit()
    app.run(debug=True)