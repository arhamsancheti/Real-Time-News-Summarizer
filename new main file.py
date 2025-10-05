import requests
from bs4 import BeautifulSoup
from transformers import pipeline
from collections import defaultdict
import re
from datetime import datetime
from gtts import gTTS
import os

class NewsAnalyzer:
    def __init__(self):
        # Initialize sentiment analysis and summarization pipelines
        print("Loading NLP models...")
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        
    def fetch_news_from_newsapi(self, api_key, category='general', country='us', max_articles=10):
        """Fetch news from NewsAPI"""
        url = f'https://newsapi.org/v2/top-headlines?country={country}&category={category}&apiKey={api_key}'
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for article in data.get('articles', [])[:max_articles]:
                if article.get('title') and article.get('description'):
                    articles.append({
                        'title': article['title'],
                        'description': article['description'],
                        'content': article.get('content', ''),
                        'url': article['url'],
                        'source': article['source']['name'],
                        'published_at': article['publishedAt']
                    })
            
            return articles
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []
    
    def scrape_news_from_bbc(self, max_articles=5):
        """Scrape news from BBC News as fallback/supplement"""
        url = 'https://www.bbc.com/news'
        articles = []
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find article headlines (BBC structure may change)
            headlines = soup.find_all('h2', {'data-testid': 'card-headline'})[:max_articles]
            
            for headline in headlines:
                title = headline.get_text().strip()
                link_tag = headline.find_parent('a')
                link = 'https://www.bbc.com' + link_tag['href'] if link_tag and link_tag.get('href', '').startswith('/') else link_tag.get('href', '')
                
                if title:
                    articles.append({
                        'title': title,
                        'description': title,  # Use title as description for scraped content
                        'content': '',
                        'url': link,
                        'source': 'BBC News',
                        'published_at': datetime.now().isoformat()
                    })
        except Exception as e:
            print(f"Error scraping BBC: {e}")
        
        return articles
    
    def summarize_text(self, text, max_length=130, min_length=30):
        """Summarize text using transformer model"""
        try:
            # Clean and prepare text
            text = text.strip()
            if len(text.split()) < 50:
                return text  # Too short to summarize
            
            # Truncate if too long (BART has token limits)
            words = text.split()
            if len(words) > 500:
                text = ' '.join(words[:500])
            
            summary = self.summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
            return summary[0]['summary_text']
        except Exception as e:
            print(f"Summarization error: {e}")
            return text[:200] + "..."  # Fallback to truncation
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of text"""
        try:
            result = self.sentiment_analyzer(text[:512])[0]  # Limit to 512 tokens
            return result['label'], result['score']
        except Exception as e:
            print(f"Sentiment analysis error: {e}")
            return "NEUTRAL", 0.5
    
    def categorize_by_topics(self, articles):
        """Categorize articles by detected topics/keywords"""
        topic_keywords = {
            'Politics': ['election', 'government', 'president', 'congress', 'policy', 'minister'],
            'Technology': ['tech', 'ai', 'software', 'computer', 'digital', 'cyber', 'startup'],
            'Business': ['market', 'economy', 'business', 'finance', 'stock', 'company', 'trade'],
            'Health': ['health', 'medical', 'disease', 'hospital', 'vaccine', 'covid'],
            'Sports': ['sport', 'game', 'team', 'player', 'match', 'championship'],
            'Entertainment': ['movie', 'music', 'celebrity', 'film', 'actor', 'show'],
            'Science': ['science', 'research', 'study', 'scientist', 'discovery'],
            'Environment': ['climate', 'environment', 'energy', 'pollution', 'weather']
        }
        
        categorized = defaultdict(list)
        
        for article in articles:
            text = (article['title'] + ' ' + article['description']).lower()
            matched_category = 'General'
            max_matches = 0
            
            for category, keywords in topic_keywords.items():
                matches = sum(1 for keyword in keywords if keyword in text)
                if matches > max_matches:
                    max_matches = matches
                    matched_category = category
            
            categorized[matched_category].append(article)
        
        return dict(categorized)
    
    def generate_report(self, articles, format='bullet'):
        """Generate formatted news report"""
        if not articles:
            return "No articles to summarize."
        
        # Categorize and analyze
        categorized = self.categorize_by_topics(articles)
        
        report = []
        report.append(f"📰 NEWS SUMMARY - {datetime.now().strftime('%B %d, %Y %H:%M')}")
        report.append("=" * 60)
        
        for category, category_articles in categorized.items():
            report.append(f"\n🔹 {category.upper()} ({len(category_articles)} articles)")
            report.append("-" * 60)
            
            for i, article in enumerate(category_articles, 1):
                # Get sentiment
                sentiment, score = self.analyze_sentiment(article['description'])
                sentiment_emoji = "😊" if sentiment == "POSITIVE" else "😟" if sentiment == "NEGATIVE" else "😐"
                
                # Summarize
                full_text = article['content'] or article['description']
                summary = self.summarize_text(full_text)
                
                if format == 'bullet':
                    report.append(f"\n{i}. {article['title']}")
                    report.append(f"   Source: {article['source']} | Sentiment: {sentiment_emoji} {sentiment} ({score:.2f})")
                    report.append(f"   Summary: {summary}")
                    report.append(f"   Link: {article['url']}")
                else:
                    report.append(f"\n{article['title']} ({article['source']})")
                    report.append(f"Sentiment: {sentiment_emoji} {sentiment}")
                    report.append(f"{summary}")
        
        return "\n".join(report)
    
    def text_to_speech(self, text, filename='news_summary.mp3', lang='en'):
        """Convert text to speech and save as MP3"""
        try:
            # Clean text for TTS (remove emojis and special characters)
            clean_text = re.sub(r'[^\w\s.,!?-]', '', text)
            clean_text = re.sub(r'http\S+', '', clean_text)  # Remove URLs
            
            tts = gTTS(text=clean_text, lang=lang, slow=False)
            tts.save(filename)
            print(f"Audio saved as {filename}")
            return filename
        except Exception as e:
            print(f"Text-to-speech error: {e}")
            return None


# Example usage
if __name__ == "__main__":
    analyzer = NewsAnalyzer()
    
    # Option 1: Use NewsAPI (requires API key from newsapi.org)
    API_KEY = "your_newsapi_key_here"  # Get free key from https://newsapi.org
    
    print("Fetching news...")
    # articles = analyzer.fetch_news_from_newsapi(API_KEY, category='technology', max_articles=5)
    
    # Option 2: Scrape BBC News (no API key needed)
    articles = analyzer.scrape_news_from_bbc(max_articles=5)
    
    if articles:
        print(f"\nFetched {len(articles)} articles\n")
        
        # Generate text report
        report = analyzer.generate_report(articles, format='bullet')
        print(report)
        
        # Save report to file
        with open('news_report.txt', 'w', encoding='utf-8') as f:
            f.write(report)
        print("\n✅ Report saved to news_report.txt")
        
        # Optional: Generate audio summary
        # audio_file = analyzer.text_to_speech(report)
        # if audio_file:
        #     print(f"✅ Audio summary created: {audio_file}")
        #     # You can play it with: os.system(f"start {audio_file}")  # Windows
    else:
        print("No articles fetched. Check your API key or internet connection.")