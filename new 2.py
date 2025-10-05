# ============================================================================
# COMPLETE NEWS SUMMARIZER - FULL STACK APPLICATION
# ============================================================================
# This includes: Backend API (Flask) + Frontend (HTML/JS) + Deployment Config
# ============================================================================

# ============================================================================
# FILE 1: backend/app.py - Flask API Server
# ============================================================================
"""
Flask API backend for News Summarizer
Run with: python app.py
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from transformers import pipeline
from collections import defaultdict
import re
from datetime import datetime
import os
import logging

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsAnalyzer:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        if not self.initialized:
            logger.info("Loading NLP models... This may take a minute.")
            try:
                self.sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
                self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
                self.initialized = True
                logger.info("Models loaded successfully!")
            except Exception as e:
                logger.error(f"Error loading models: {e}")
                self.initialized = False
    
    def fetch_news_from_newsapi(self, api_key, category='general', country='us', max_articles=10):
        """Fetch news from NewsAPI"""
        url = f'https://newsapi.org/v2/top-headlines?country={country}&category={category}&apiKey={api_key}'
        
        try:
            response = requests.get(url, timeout=10)
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
            logger.error(f"NewsAPI error: {e}")
            return []
    
    def scrape_news_from_bbc(self, max_articles=10):
        """Scrape news from BBC News"""
        url = 'https://www.bbc.com/news'
        articles = []
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find article headlines
            headlines = soup.find_all('h2', attrs={'data-testid': 'card-headline'})[:max_articles]
            
            for headline in headlines:
                title = headline.get_text().strip()
                link_tag = headline.find_parent('a')
                link = ''
                if link_tag and link_tag.get('href'):
                    href = link_tag['href']
                    link = 'https://www.bbc.com' + href if href.startswith('/') else href
                
                if title and len(title) > 10:
                    articles.append({
                        'title': title,
                        'description': title,
                        'content': '',
                        'url': link,
                        'source': 'BBC News',
                        'published_at': datetime.now().isoformat()
                    })
            
            logger.info(f"Scraped {len(articles)} articles from BBC")
            return articles
        except Exception as e:
            logger.error(f"BBC scraping error: {e}")
            return []
    
    def analyze_sentiment(self, text):
        """Analyze sentiment"""
        if not self.initialized:
            return "neutral", 0.5
        
        try:
            result = self.sentiment_analyzer(text[:512])[0]
            label = result['label'].lower()
            score = result['score']
            
            # Map to our sentiment labels
            if label == 'positive':
                return 'positive', score
            elif label == 'negative':
                return 'negative', score
            else:
                return 'neutral', score
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return "neutral", 0.5
    
    def summarize_text(self, text, max_length=130, min_length=30):
        """Summarize text"""
        if not self.initialized:
            return text[:200] + "..."
        
        try:
            text = text.strip()
            words = text.split()
            
            if len(words) < 50:
                return text
            
            if len(words) > 500:
                text = ' '.join(words[:500])
            
            summary = self.summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
            return summary[0]['summary_text']
        except Exception as e:
            logger.error(f"Summarization error: {e}")
            return text[:200] + "..."
    
    def categorize_article(self, text):
        """Categorize article by keywords"""
        topic_keywords = {
            'Technology': ['tech', 'ai', 'software', 'computer', 'digital', 'cyber', 'startup', 'app'],
            'Business': ['market', 'economy', 'business', 'finance', 'stock', 'company', 'trade', 'bank'],
            'Health': ['health', 'medical', 'disease', 'hospital', 'vaccine', 'doctor', 'patient'],
            'Sports': ['sport', 'game', 'team', 'player', 'match', 'championship', 'win', 'score'],
            'Entertainment': ['movie', 'music', 'celebrity', 'film', 'actor', 'show', 'star'],
            'Science': ['science', 'research', 'study', 'scientist', 'discovery', 'experiment'],
            'Environment': ['climate', 'environment', 'energy', 'pollution', 'weather', 'carbon'],
            'Politics': ['election', 'government', 'president', 'congress', 'policy', 'minister', 'vote']
        }
        
        text_lower = text.lower()
        max_matches = 0
        category = 'General'
        
        for cat, keywords in topic_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            if matches > max_matches:
                max_matches = matches
                category = cat
        
        return category
    
    def process_articles(self, articles):
        """Process articles with NLP"""
        processed = []
        
        for i, article in enumerate(articles):
            try:
                # Combine title and description for analysis
                full_text = f"{article['title']}. {article['description']}"
                
                # Get category
                category = self.categorize_article(full_text)
                
                # Get sentiment
                sentiment, score = self.analyze_sentiment(full_text)
                
                # Summarize content if available
                summary = article['description']
                if article.get('content') and len(article['content']) > 100:
                    summary = self.summarize_text(article['content'])
                
                processed.append({
                    'id': i + 1,
                    'title': article['title'],
                    'summary': summary,
                    'category': category,
                    'sentiment': sentiment,
                    'sentimentScore': score,
                    'source': article['source'],
                    'url': article['url'],
                    'publishedAt': self._format_time(article['published_at'])
                })
            except Exception as e:
                logger.error(f"Error processing article: {e}")
                continue
        
        return processed
    
    def _format_time(self, timestamp):
        """Format timestamp to relative time"""
        try:
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                dt = timestamp
            
            now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
            diff = now - dt
            
            hours = diff.total_seconds() / 3600
            if hours < 1:
                return f"{int(diff.total_seconds() / 60)} minutes ago"
            elif hours < 24:
                return f"{int(hours)} hours ago"
            else:
                return f"{int(hours / 24)} days ago"
        except:
            return "recently"

# Initialize analyzer
analyzer = NewsAnalyzer()

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/')
def index():
    """Serve frontend"""
    return send_from_directory('frontend', 'index.html')

@app.route('/api/news', methods=['GET'])
def get_news():
    """Fetch and process news"""
    try:
        # Get parameters
        source = request.args.get('source', 'bbc')  # 'bbc' or 'newsapi'
        category = request.args.get('category', 'general')
        max_articles = int(request.args.get('max', 10))
        
        # Fetch news
        if source == 'newsapi':
            api_key = os.environ.get('NEWSAPI_KEY', '')
            if not api_key:
                return jsonify({'error': 'NewsAPI key not configured'}), 400
            articles = analyzer.fetch_news_from_newsapi(api_key, category, max_articles=max_articles)
        else:
            articles = analyzer.scrape_news_from_bbc(max_articles=max_articles)
        
        if not articles:
            return jsonify({'error': 'No articles found'}), 404
        
        # Process articles
        processed = analyzer.process_articles(articles)
        
        return jsonify({
            'articles': processed,
            'count': len(processed),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'models_loaded': analyzer.initialized,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


# ============================================================================
# FILE 2: frontend/index.html - Frontend Application
# ============================================================================
"""
Save this as frontend/index.html
"""

HTML_CONTENT = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NewsAI - Real-Time Smart Summarizer</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .fade-in { animation: fadeIn 0.5s ease-out; }
    </style>
</head>
<body class="bg-gradient-to-br from-slate-50 to-slate-100 min-h-screen">
    <!-- Header -->
    <header class="bg-white shadow-md sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 py-6">
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <div class="bg-gradient-to-br from-blue-500 to-purple-600 p-3 rounded-xl">
                        <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"/>
                        </svg>
                    </div>
                    <div>
                        <h1 class="text-3xl font-bold text-gray-900">NewsAI</h1>
                        <p class="text-sm text-gray-600">Real-Time Smart Summarizer</p>
                    </div>
                </div>
                <button id="refreshBtn" class="flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">
                    <svg id="refreshIcon" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                    </svg>
                    Refresh
                </button>
            </div>
        </div>
    </header>

    <div class="max-w-7xl mx-auto px-4 py-8">
        <!-- Stats Dashboard -->
        <div id="statsContainer" class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <!-- Stats will be dynamically inserted -->
        </div>

        <!-- Filters -->
        <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-8">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Search</label>
                    <input type="text" id="searchInput" placeholder="Search articles..." 
                           class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Category</label>
                    <select id="categoryFilter" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                        <option value="all">All Categories</option>
                    </select>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Sentiment</label>
                    <select id="sentimentFilter" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                        <option value="all">All</option>
                        <option value="positive">Positive</option>
                        <option value="neutral">Neutral</option>
                        <option value="negative">Negative</option>
                    </select>
                </div>
            </div>
        </div>

        <!-- Loading Indicator -->
        <div id="loadingIndicator" class="hidden flex items-center justify-center py-20">
            <svg class="w-12 h-12 animate-spin text-blue-600" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
        </div>

        <!-- Articles Container -->
        <div id="articlesContainer" class="grid grid-cols-1 gap-6">
            <!-- Articles will be dynamically inserted -->
        </div>

        <!-- Empty State -->
        <div id="emptyState" class="hidden text-center py-20">
            <svg class="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"/>
            </svg>
            <h3 class="text-xl font-semibold text-gray-700 mb-2">No articles found</h3>
            <p class="text-gray-500">Try adjusting your filters or search terms</p>
        </div>
    </div>

    <script>
        let allArticles = [];
        const API_URL = '/api';

        // Fetch news from backend
        async function fetchNews() {
            const loadingIndicator = document.getElementById('loadingIndicator');
            const articlesContainer = document.getElementById('articlesContainer');
            const refreshIcon = document.getElementById('refreshIcon');
            
            loadingIndicator.classList.remove('hidden');
            articlesContainer.innerHTML = '';
            refreshIcon.classList.add('animate-spin');
            
            try {
                const response = await fetch(`${API_URL}/news?source=bbc&max=15`);
                const data = await response.json();
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                allArticles = data.articles;
                updateStats();
                updateCategoryFilter();
                displayArticles();
            } catch (error) {
                console.error('Error fetching news:', error);
                articlesContainer.innerHTML = `
                    <div class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
                        <p class="text-red-800 font-medium">Failed to load news</p>
                        <p class="text-red-600 text-sm mt-2">${error.message}</p>
                    </div>
                `;
            } finally {
                loadingIndicator.classList.add('hidden');
                refreshIcon.classList.remove('animate-spin');
            }
        }

        // Update stats dashboard
        function updateStats() {
            const stats = {
                total: allArticles.length,
                positive: allArticles.filter(a => a.sentiment === 'positive').length,
                neutral: allArticles.filter(a => a.sentiment === 'neutral').length,
                negative: allArticles.filter(a => a.sentiment === 'negative').length
            };
            
            document.getElementById('statsContainer').innerHTML = `
                <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-gray-600 text-sm">Total Articles</p>
                            <p class="text-3xl font-bold text-gray-900">${stats.total}</p>
                        </div>
                        <svg class="w-10 h-10 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
                        </svg>
                    </div>
                </div>
                <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-gray-600 text-sm">Positive</p>
                            <p class="text-3xl font-bold text-green-600">${stats.positive}</p>
                        </div>
                        <svg class="w-10 h-10 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                    </div>
                </div>
                <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-gray-600 text-sm">Neutral</p>
                            <p class="text-3xl font-bold text-gray-600">${stats.neutral}</p>
                        </div>
                        <svg class="w-10 h-10 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5"/>
                        </svg>
                    </div>
                </div>
                <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-gray-600 text-sm">Negative</p>
                            <p class="text-3xl font-bold text-red-600">${stats.negative}</p>
                        </div>
                        <svg class="w-10 h-10 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                    </div>
                </div>
            `;
        }

        // Update category filter options
        function updateCategoryFilter() {
            const categories = [...new Set(allArticles.map(a => a.category))].sort();
            const categoryFilter = document.getElementById('categoryFilter');
            categoryFilter.innerHTML = '<option value="all">All Categories</option>';
            categories.forEach(cat => {
                categoryFilter.innerHTML += `<option value="${cat}">${cat}</option>`;
            });
        }

        // Display articles
        function displayArticles() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const categoryFilter = document.getElementById('categoryFilter').value;
            const sentimentFilter = document.getElementById('sentimentFilter').value;
            
            const filtered = allArticles.filter(article => {
                const matchesSearch = article.title.toLowerCase().includes(searchTerm) || 
                                    article.summary.toLowerCase().includes(searchTerm);
                const matchesCategory = categoryFilter === 'all' || article.category === categoryFilter;
                const matchesSentiment = sentimentFilter === 'all' || article.sentiment === sentimentFilter;
                return matchesSearch && matchesCategory && matchesSentiment;
            });
            
            const container = document.getElementById('articlesContainer');
            const emptyState = document.getElementById('emptyState');
            
            if (filtered.length === 0) {
                container.innerHTML = '';
                emptyState.classList.remove('hidden');
                return;
            }
            
            emptyState.classList.add('hidden');
            container.innerHTML = filtered.map(article => createArticleCard(article)).join('');
        }

        // Create article card HTML
        function createArticleCard(article) {
            const categoryColors = {
                'Technology': 'bg-blue-100 text-blue-800',
                'Business': 'bg-purple-100 text-purple-800',
                'Environment': 'bg-green-100 text-green-800',
                'Health': 'bg-pink-100 text-pink-800',
                'Sports': 'bg-orange-100 text-orange-800',
                'Politics': 'bg-indigo-100 text-indigo-800',
                'Science': 'bg-teal-100 text-teal-800',
                'Entertainment': 'bg-rose-100 text-rose-800',
                'General': 'bg-gray-100 text-gray-800'
            };
            
            const sentimentColors = {
                'positive': 'bg-green-100 text-green-800 border-green-300',
                'negative': 'bg-red-100 text-red-800 border-red-300',
                'neutral': 'bg-gray-100 text-gray-800 border-gray-300'
            };
            
            const sentimentIcons = {
                'positive': '😊',
                'negative': '😟',
                'neutral': '😐'
            };
            
            return `
                <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-lg transition-shadow fade-in">
                    <div class="flex items-start justify-between mb-3">
                        <div class="flex gap-2 flex-wrap">
                            <span class="px-3 py-1 rounded-full text-xs font-medium ${categoryColors[article.category] || categoryColors['General']}">
                                ${article.category}
                            </span>
                            <span class="px-3 py-1 rounded-full text-xs font-medium border ${sentimentColors[article.sentiment]}">
                                ${sentimentIcons[article.sentiment]} ${article.sentiment.charAt(0).toUpperCase() + article.sentiment.slice(1)} 
                                (${(article.sentimentScore * 100).toFixed(0)}%)
                            </span>
                        </div>
                        <button onclick="speakArticle('${article.id}')" class="p-2 hover:bg-gray-100 rounded-lg transition-colors" title="Listen to summary">
                            <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"/>
                            </svg>
                        </button>
                    </div>
                    <h2 class="text-xl font-bold text-gray-900 mb-3">${article.title}</h2>
                    <p class="text-gray-700 mb-4 leading-relaxed">${article.summary}</p>
                    <div class="flex items-center justify-between text-sm text-gray-500">
                        <span class="font-medium">${article.source}</span>
                        <span>${article.publishedAt}</span>
                    </div>
                </div>
            `;
        }

        // Text to speech
        function speakArticle(articleId) {
            const article = allArticles.find(a => a.id == articleId);
            if (!article) return;
            
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
                const text = `${article.title}. ${article.summary}`;
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = 0.9;
                window.speechSynthesis.speak(utterance);
            }
        }

        // Event listeners
        document.getElementById('refreshBtn').addEventListener('click', fetchNews);
        document.getElementById('searchInput').addEventListener('input', displayArticles);
        document.getElementById('categoryFilter').addEventListener('change', displayArticles);
        document.getElementById('sentimentFilter').addEventListener('change', displayArticles);

        // Initial load
        fetchNews();
    </script>
</body>
</html>
'''

# ============================================================================
# FILE 3: requirements.txt
# ============================================================================
REQUIREMENTS = """flask==3.0.0
flask-cors==4.0.0
requests==2.31.0
beautifulsoup4==4.12.2
transformers==4.35.0
torch==2.1.0
sentencepiece==0.1.99
gunicorn==21.2.0
"""