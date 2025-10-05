# 📰 NewsAI - Real-Time Smart News Summarizer

![NewsAI Banner](https://img.shields.io/badge/AI-Powered-blue) ![Version](https://img.shields.io/badge/version-1.0.0-orange)

An intelligent news aggregator and analyzer that uses AI to fetch, categorize, summarize, and analyze sentiment of news articles in real-time. Built with modern NLP models and a beautiful, responsive interface.

---

## 🌟 Features

### 🤖 AI-Powered Analysis
- **Smart Summarization** - Uses BART transformer model to create concise, intelligent summaries
- **Sentiment Analysis** - Analyzes emotional tone (Positive/Negative/Neutral) using DistilBERT
- **Auto-Categorization** - Automatically classifies articles into 8 topics
- **Confidence Scoring** - Shows AI confidence levels for transparency

### 📊 Real-Time Data
- **Multiple News Sources** - BBC News scraping + NewsAPI integration
- **Live Updates** - Refresh to get latest articles
- **Trending Topics** - See what's making headlines across categories

### 🎨 Modern Interface
- **Beautiful UI** - Gradient backgrounds, smooth animations, professional design
- **Responsive Design** - Works flawlessly on mobile, tablet, and desktop
- **Interactive Dashboard** - Real-time statistics and sentiment breakdown
- **Smart Filtering** - Search, category, and sentiment filters

### 🔊 Accessibility
- **Text-to-Speech** - Listen to any article summary
- **Keyboard Navigation** - Full keyboard support
- **Screen Reader Friendly** - ARIA labels and semantic HTML

---

## 🚀 Quick Start

### Option 1: Standalone Web App (No Installation)

1. **Download** the `index.html` file
2. **Open** in any modern web browser
3. **Done!** The app works instantly with simulated AI analysis

### Option 2: Full Backend Setup (Production)

#### Prerequisites
- Python 3.8 or higher
- 4GB RAM minimum
- 5GB free disk space (for AI models)

#### Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/newsai.git
cd newsai

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download AI models (one-time, ~5-10 minutes)
python -c "from transformers import pipeline; pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english'); pipeline('summarization', model='facebook/bart-large-cnn')"

# 5. Run the application
cd backend
python app.py

# 6. Open browser
# Navigate to: http://localhost:5000
```

#### Optional: Add NewsAPI Key

```bash
# Get free API key from https://newsapi.org
echo "NEWSAPI_KEY=your_api_key_here" > .env
```

### Option 3: Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access at http://localhost:5000
```

---

## 📁 Project Structure

```
newsai/
├── backend/
│   └── app.py                 # Flask API server
├── frontend/
│   └── index.html             # Web interface
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container configuration
├── docker-compose.yml         # Docker Compose setup
├── setup_and_run.py          # Automated setup script
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

---

## 🎯 How It Works

### Architecture Overview

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Frontend  │ ───► │   Flask API  │ ───► │ News Sources│
│  (HTML/JS)  │      │   (Python)   │      │ (BBC/NewsAPI)│
└─────────────┘      └──────────────┘      └─────────────┘
       │                     │
       │                     ▼
       │             ┌──────────────┐
       │             │  NLP Models  │
       │             │ BART + BERT  │
       │             └──────────────┘
       │                     │
       └─────────────────────┘
              (Processed Data)
```

### AI Pipeline

1. **Fetch** - Scrape/API call to get raw news articles
2. **Categorize** - Classify into topics using keyword matching
3. **Analyze Sentiment** - Use DistilBERT for emotional analysis
4. **Summarize** - Apply BART model for intelligent summarization
5. **Display** - Present results in beautiful UI with filters

---

## 🛠️ Technologies Used

### Backend
- **Python 3.10** - Core programming language
- **Flask** - Web framework for API
- **Transformers** - Hugging Face library for NLP
- **BART** - Summarization model
- **DistilBERT** - Sentiment analysis model
- **BeautifulSoup4** - Web scraping
- **Requests** - HTTP library

### Frontend
- **HTML5** - Semantic markup
- **Tailwind CSS** - Utility-first styling
- **Vanilla JavaScript** - No frameworks, pure JS
- **Web Speech API** - Text-to-speech

### DevOps
- **Docker** - Containerization
- **Gunicorn** - WSGI HTTP server
- **GitHub Actions** - CI/CD (optional)

---

## 📊 API Documentation

### Endpoints

#### `GET /api/news`
Fetch and process news articles

**Query Parameters:**
- `source` (optional): `bbc` or `newsapi` (default: `bbc`)
- `category` (optional): news category (default: `general`)
- `max` (optional): maximum articles (default: `10`)

**Response:**
```json
{
  "articles": [
    {
      "id": 1,
      "title": "Article Title",
      "summary": "AI-generated summary...",
      "category": "Technology",
      "sentiment": "positive",
      "sentimentScore": 0.92,
      "source": "BBC News",
      "url": "https://...",
      "publishedAt": "2 hours ago"
    }
  ],
  "count": 10,
  "timestamp": "2025-10-05T12:00:00"
}
```

#### `GET /api/health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "models_loaded": true,
  "timestamp": "2025-10-05T12:00:00"
}
```

---

## 🎨 Screenshots

### Desktop View
![Desktop Dashboard](https://via.placeholder.com/800x400/4F46E5/FFFFFF?text=Dashboard+View)

### Mobile View
![Mobile View](https://via.placeholder.com/400x800/7C3AED/FFFFFF?text=Mobile+View)

### Article Card
![Article Card](https://via.placeholder.com/600x300/2563EB/FFFFFF?text=Article+Card)

---

## 🚢 Deployment

### Deploy to Render (Free)

1. Fork this repository
2. Go to [render.com](https://render.com)
3. Create new Web Service
4. Connect your repository
5. Set environment: **Docker**
6. Deploy!

### Deploy to Railway (Free $5 Credit)

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Deploy to Heroku

```bash
# Login and create app
heroku login
heroku create newsai-app
heroku stack:set container
git push heroku main
```

### Deploy to AWS Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize and deploy
eb init -p docker newsai
eb create newsai-env
eb open
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `NEWSAPI_KEY` | API key from newsapi.org | No | None |
| `PORT` | Server port | No | 5000 |
| `DEBUG` | Debug mode | No | False |

### Customization

#### Change News Categories

Edit `backend/app.py`, line ~120:

```python
topic_keywords = {
    'YourCategory': ['keyword1', 'keyword2', ...],
    # Add more categories
}
```

#### Adjust AI Models

Edit `backend/app.py`, line ~30:

```python
# Use different models
self.sentiment_analyzer = pipeline("sentiment-analysis", model="your-model")
self.summarizer = pipeline("summarization", model="your-model")
```

---

## 🐛 Troubleshooting

### Common Issues

**Problem:** Models taking too long to download
- **Solution:** First run downloads ~2GB. Use good internet. Wait 5-10 minutes.

**Problem:** Out of memory error
- **Solution:** Need at least 4GB RAM. Close other applications or use smaller models.

**Problem:** News not loading
- **Solution:** Check internet connection. BBC may be blocked in some regions. Try NewsAPI.

**Problem:** Port already in use
- **Solution:** Change port: `python app.py --port 8080`

### Debug Mode

```bash
# Enable detailed logging
export DEBUG=True
python app.py
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Check code style
flake8 backend/
black backend/

# Run linter
pylint backend/
```

---

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 NewsAI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Acknowledgments

- **Hugging Face** - For amazing NLP models
- **Tailwind CSS** - For beautiful styling utilities
- **NewsAPI** - For news data access
- **BBC News** - For public news content
- **OpenAI** - For inspiration in AI applications

---

## 📧 Contact

**Project Maintainer:** Your Name  
**Email:** your.email@example.com  
**GitHub:** [@yourusername](https://github.com/yourusername)  
**LinkedIn:** [Your Name](https://linkedin.com/in/yourprofile)

---

## 🔮 Roadmap

### Version 1.1 (Coming Soon)
- [ ] Multi-language support
- [ ] Save favorite articles
- [ ] Export to PDF
- [ ] Email digest feature
- [ ] Dark mode toggle

### Version 1.2
- [ ] User authentication
- [ ] Personalized news feed
- [ ] Advanced analytics
- [ ] Mobile app (React Native)

### Version 2.0
- [ ] Real-time WebSocket updates
- [ ] Social media integration
- [ ] AI chatbot for news queries
- [ ] Custom RSS feed support

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/newsai&type=Date)](https://star-history.com/#yourusername/newsai&Date)

---

## 📈 Project Stats

![GitHub stars](https://img.shields.io/github/stars/yourusername/newsai?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/newsai?style=social)
![GitHub issues](https://img.shields.io/github/issues/yourusername/newsai)
![GitHub pull requests](https://img.shields.io/github/issues-pr/yourusername/newsai)

---

<div align="center">



</div>
