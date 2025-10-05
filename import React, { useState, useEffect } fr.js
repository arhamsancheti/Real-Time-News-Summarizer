import React, { useState, useEffect } from 'react';
import { Newspaper, TrendingUp, Smile, Frown, Meh, RefreshCw, Volume2, Search, Filter } from 'lucide-react';

const NewsSummarizerApp = () => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [sentimentFilter, setSentimentFilter] = useState('all');

  // Mock news data with sentiment analysis
  const mockNewsData = [
    {
      id: 1,
      title: "AI Breakthrough: New Model Achieves Human-Level Reasoning",
      summary: "Researchers have developed an advanced AI system that demonstrates unprecedented reasoning capabilities, potentially revolutionizing problem-solving across industries.",
      category: "Technology",
      sentiment: "positive",
      sentimentScore: 0.92,
      source: "Tech Daily",
      url: "#",
      publishedAt: "2 hours ago"
    },
    {
      id: 2,
      title: "Global Markets Show Mixed Results Amid Economic Uncertainty",
      summary: "Stock markets worldwide experienced volatility today as investors react to mixed economic indicators and ongoing geopolitical tensions.",
      category: "Business",
      sentiment: "neutral",
      sentimentScore: 0.55,
      source: "Financial Times",
      url: "#",
      publishedAt: "4 hours ago"
    },
    {
      id: 3,
      title: "Climate Summit Ends Without Major Agreement",
      summary: "International leaders failed to reach consensus on critical climate action measures, raising concerns about meeting emission reduction targets.",
      category: "Environment",
      sentiment: "negative",
      sentimentScore: 0.78,
      source: "World News",
      url: "#",
      publishedAt: "6 hours ago"
    },
    {
      id: 4,
      title: "New Medical Treatment Shows Promise in Clinical Trials",
      summary: "A groundbreaking therapy for chronic conditions has demonstrated significant positive results in phase 3 trials, offering hope to millions of patients.",
      category: "Health",
      sentiment: "positive",
      sentimentScore: 0.88,
      source: "Medical Journal",
      url: "#",
      publishedAt: "8 hours ago"
    },
    {
      id: 5,
      title: "Championship Game Ends in Dramatic Fashion",
      summary: "The finals concluded with a last-second victory that will be remembered as one of the greatest moments in sports history.",
      category: "Sports",
      sentiment: "positive",
      sentimentScore: 0.85,
      source: "Sports Network",
      url: "#",
      publishedAt: "10 hours ago"
    },
    {
      id: 6,
      title: "Government Announces New Infrastructure Plan",
      summary: "Officials unveiled a comprehensive infrastructure development initiative aimed at modernizing transportation and communication systems.",
      category: "Politics",
      sentiment: "neutral",
      sentimentScore: 0.62,
      source: "National Press",
      url: "#",
      publishedAt: "12 hours ago"
    }
  ];

  useEffect(() => {
    fetchNews();
  }, []);

  const fetchNews = () => {
    setLoading(true);
    setTimeout(() => {
      setArticles(mockNewsData);
      setLoading(false);
    }, 1000);
  };

  const getSentimentIcon = (sentiment) => {
    switch(sentiment) {
      case 'positive': return <Smile className="w-5 h-5 text-green-500" />;
      case 'negative': return <Frown className="w-5 h-5 text-red-500" />;
      default: return <Meh className="w-5 h-5 text-gray-500" />;
    }
  };

  const getSentimentColor = (sentiment) => {
    switch(sentiment) {
      case 'positive': return 'bg-green-100 text-green-800 border-green-300';
      case 'negative': return 'bg-red-100 text-red-800 border-red-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      'Technology': 'bg-blue-100 text-blue-800',
      'Business': 'bg-purple-100 text-purple-800',
      'Environment': 'bg-green-100 text-green-800',
      'Health': 'bg-pink-100 text-pink-800',
      'Sports': 'bg-orange-100 text-orange-800',
      'Politics': 'bg-indigo-100 text-indigo-800'
    };
    return colors[category] || 'bg-gray-100 text-gray-800';
  };

  const categories = ['all', ...new Set(mockNewsData.map(a => a.category))];

  const filteredArticles = articles.filter(article => {
    const matchesCategory = selectedCategory === 'all' || article.category === selectedCategory;
    const matchesSearch = article.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         article.summary.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSentiment = sentimentFilter === 'all' || article.sentiment === sentimentFilter;
    return matchesCategory && matchesSearch && matchesSentiment;
  });

  const speakSummary = (text) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9;
      window.speechSynthesis.speak(utterance);
    }
  };

  const categoryStats = categories.slice(1).map(cat => ({
    category: cat,
    count: articles.filter(a => a.category === cat).length
  }));

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white shadow-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-3 rounded-xl">
                <Newspaper className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">NewsAI</h1>
                <p className="text-sm text-gray-600">Real-Time Smart Summarizer</p>
              </div>
            </div>
            <button
              onClick={fetchNews}
              disabled={loading}
              className="flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats Dashboard */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Articles</p>
                <p className="text-3xl font-bold text-gray-900">{articles.length}</p>
              </div>
              <TrendingUp className="w-10 h-10 text-blue-500" />
            </div>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Positive</p>
                <p className="text-3xl font-bold text-green-600">
                  {articles.filter(a => a.sentiment === 'positive').length}
                </p>
              </div>
              <Smile className="w-10 h-10 text-green-500" />
            </div>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Neutral</p>
                <p className="text-3xl font-bold text-gray-600">
                  {articles.filter(a => a.sentiment === 'neutral').length}
                </p>
              </div>
              <Meh className="w-10 h-10 text-gray-500" />
            </div>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Negative</p>
                <p className="text-3xl font-bold text-red-600">
                  {articles.filter(a => a.sentiment === 'negative').length}
                </p>
              </div>
              <Frown className="w-10 h-10 text-red-500" />
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Search className="w-4 h-4 inline mr-1" />
                Search
              </label>
              <input
                type="text"
                placeholder="Search articles..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Filter className="w-4 h-4 inline mr-1" />
                Category
              </label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {categories.map(cat => (
                  <option key={cat} value={cat}>
                    {cat.charAt(0).toUpperCase() + cat.slice(1)}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Sentiment
              </label>
              <select
                value={sentimentFilter}
                onChange={(e) => setSentimentFilter(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All</option>
                <option value="positive">Positive</option>
                <option value="neutral">Neutral</option>
                <option value="negative">Negative</option>
              </select>
            </div>
          </div>
        </div>

        {/* Articles Grid */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <RefreshCw className="w-12 h-12 animate-spin text-blue-600" />
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6">
            {filteredArticles.map(article => (
              <div
                key={article.id}
                className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex gap-2">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getCategoryColor(article.category)}`}>
                      {article.category}
                    </span>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getSentimentColor(article.sentiment)}`}>
                      <span className="flex items-center gap-1">
                        {getSentimentIcon(article.sentiment)}
                        {article.sentiment.charAt(0).toUpperCase() + article.sentiment.slice(1)}
                        ({(article.sentimentScore * 100).toFixed(0)}%)
                      </span>
                    </span>
                  </div>
                  <button
                    onClick={() => speakSummary(article.title + '. ' + article.summary)}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                    title="Listen to summary"
                  >
                    <Volume2 className="w-5 h-5 text-gray-600" />
                  </button>
                </div>
                
                <h2 className="text-xl font-bold text-gray-900 mb-3">
                  {article.title}
                </h2>
                
                <p className="text-gray-700 mb-4 leading-relaxed">
                  {article.summary}
                </p>
                
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <span className="font-medium">{article.source}</span>
                  <span>{article.publishedAt}</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {filteredArticles.length === 0 && !loading && (
          <div className="text-center py-20">
            <Newspaper className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-700 mb-2">No articles found</h3>
            <p className="text-gray-500">Try adjusting your filters or search terms</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default NewsSummarizerApp;