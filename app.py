from flask import Flask, render_template, request
from utils.weaviate_queries import (
    get_email_count,
    get_top_senders,
    get_email_volume_over_time,
    get_common_words,
    search_emails
)

app = Flask(__name__)

@app.route('/')
def index():
    email_count = get_email_count()
    top_senders = get_top_senders()
    email_volume = get_email_volume_over_time()
    common_words = get_common_words()
    return render_template('index.html', 
                           email_count=email_count, 
                           top_senders=top_senders, 
                           email_volume=email_volume, 
                           common_words=common_words)

@app.route('/search')
def search():
    query = request.args.get('query', '')
    results = search_emails(query)
    return render_template('index.html', search_results=results)

if __name__ == '__main__':
    app.run(debug=True)
