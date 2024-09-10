import weaviate
import os
from dotenv import load_dotenv
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64

load_dotenv()

client = weaviate.Client(os.getenv('WEAVIATE_URL'))

def get_email_count():
    result = client.query.aggregate('Email').with_meta_count().do()
    return result['data']['Aggregate']['Email'][0]['meta']['count']

def get_top_senders(limit=5):
    result = client.query.get('Email', ['sender']).with_additional(['id']).do()
    senders = [email['sender'] for email in result['data']['Get']['Email']]
    sender_counts = {}
    for sender in senders:
        sender_counts[sender] = sender_counts.get(sender, 0) + 1
    return sorted(sender_counts.items(), key=lambda x: x[1], reverse=True)[:limit]

def get_email_volume_over_time():
    result = client.query.get('Email', ['date']).with_additional(['id']).do()
    dates = [email['date'][:10] for email in result['data']['Get']['Email']]
    date_counts = {}
    for date in dates:
        date_counts[date] = date_counts.get(date, 0) + 1
    sorted_dates = sorted(date_counts.keys())
    return {
        'labels': sorted_dates,
        'data': [date_counts[date] for date in sorted_dates]
    }

def get_common_words():
    result = client.query.get('Email', ['body']).with_additional(['id']).do()
    text = ' '.join([email['body'] for email in result['data']['Get']['Email']])
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    
    img = io.BytesIO()
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout(pad=0)
    plt.savefig(img, format='png')
    img.seek(0)
    
    return base64.b64encode(img.getvalue()).decode()

def search_emails(query):
    result = client.query.get('Email', ['subject', 'body', 'sender', 'date']) \
        .with_bm25(query=query) \
        .with_limit(10) \
        .do()
    return result['data']['Get']['Email']
