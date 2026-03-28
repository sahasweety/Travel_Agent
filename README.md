# 🌍 AI Travel Planning System

An intelligent AI-powered travel planning system that generates personalized itineraries using advanced language models, real-time location data, and web research.

**Status**: ✅ Production Ready | 🚀 Fully Functional

## ✨ Features

- ✅ **AI-Powered Itineraries** - Gemini Pro or Claude 3 via OpenRouter
- ✅ **Smart Location Discovery** - Real-time search with proximity sorting
- ✅ **Multiple Place Suggestions** - Hotels, restaurants, attractions, activities, shopping, healthcare (8+ per category)
- ✅ **Distance-Based Sorting** - Places automatically sorted by proximity to destination
- ✅ **Rich Place Details** - Phone, website, opening hours, ratings, addresses
- ✅ **Budget-Aware Planning** - Custom budgets from ₹10K to ₹1,00,000+
- ✅ **Web Intelligence** - Real-time travel information via Tavily API
- ✅ **No Quota Issues** - OpenRouter API support with unlimited usage
- ✅ **Fallback Mechanisms** - Continues even if APIs hit rate limits
- ✅ **Free Map Data** - OpenStreetMap (no API key needed)
- ✅ **Streamlit UI** - Beautiful, user-friendly interface
- ✅ **Day-by-Day Schedules** - Detailed timing and recommendations

## Project Structure

```
├── app.py                    # Main travel planning system & FastAPI backend
├── st_app.py                 # Streamlit web interface
├── TravelMapView.tsx         # React map component
├── requirements.txt          # Python dependencies
└── .env                      # Environment variables
```

## Prerequisites

- Python 3.8+
- **Either one of:**
  - ✅ OpenRouter API key (Recommended) - Use Gemini Pro with unlimited quota
  - ✅ Google Gemini API key (Free tier has limits)
- Tavily API key (for web research)
- Git (for cloning and contributing)

## Setup

### 1. Clone Repository

```bash
git clone https://github.com/sahasweety/Travel_Agent.git
cd Travel_Agent
```

### 2. Create Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Get API Keys

#### 🚀 Option A: OpenRouter API (Recommended - No Quota Limits)

1. Visit: https://openrouter.ai
2. Sign up for free account
3. Go to: https://openrouter.ai/keys
4. Copy your API key

**Pricing**: Pay only for what you use (~₹8-80 per travel plan)

#### 🔵 Option B: Google Gemini API (Free Tier with Rate Limits)

1. Visit: https://makersuite.google.com/app/apikey
2. Create or select project
3. Click "Create API key"
4. Copy your API key

**⚠️ Note**: Free tier has quota limits (60 requests/min, 1500 requests/day)

#### 🔍 Get Tavily API Key

1. Visit: https://tavily.com
2. Sign up and log in
3. Copy your API key from dashboard

### 5. Configure Environment Variables

Create `.env` file in project root:

```env
# Required
TAVILY_API_KEY=your_tavily_api_key_here

# Choose one (OpenRouter recommended)
OPENROUTER_API_KEY=your_openrouter_api_key_here
# OR
GOOGLE_API_KEY1=your_google_gemini_api_key_here
```

**⚠️ Important**: Never commit `.env` to git (already in .gitignore)

### 6. Run the Application

```bash
# Start Streamlit UI
streamlit run st_app.py

# Opens at http://localhost:8501
```

## Usage

### 📱 Streamlit Web Interface (Recommended)

```bash
streamlit run st_app.py
```

Visit `http://localhost:8501` and:
1. Enter departure city (e.g., Delhi)
2. Enter destination city (e.g., Mumbai)
3. Select travel dates
4. Choose number of travelers
5. Select budget range
6. Click "Generate Travel Plan" 👈

**You'll get:**
- Complete AI-generated itinerary
- Hotels, restaurants, attractions sorted by distance
- Budget breakdown
- Practical tips
- Contact details & operating hours for all places

### 🐍 Python API

Generate travel plans programmatically:

```python
from app import plan_trip
import asyncio

trip_request = {
    "from": "Delhi (DEL)",
    "to": "Mumbai (BOM)",
    "departureDate": "2025-12-20",
    "returnDate": "2025-12-25",
    "passengers": "2",
    "budget": "mid"
}

result = plan_trip(trip_request)

if result['success']:
    print(result['comprehensive_plan'])
    print(result['maps_results'])  # Nearby places with distances
else:
    print(f"Error: {result['error']}")
```

### 💾 Save Travel Plan to File

```bash
python app.py
```

Generates `travel_plan.txt` with complete plan including all location data.

## 📁 Project Structure

```
travel-agent/
├── app.py                      # Core travel system (500+ lines)
│   ├── TravelPlanningSystem   # Main class
│   ├── search_with_tavily()   # Web research
│   ├── search_with_maps()     # Location discovery
│   ├── generate_with_context() # AI generation
│   └── _generate_with_openrouter() # OpenRouter integration
│
├── st_app.py                   # Streamlit web interface
│   ├── Sidebar (Trip inputs)
│   ├── Main display (Results)
│   └── Formatted output sections
│
├── TravelMapView.tsx           # React map component
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (gitignored)
├── .gitignore                  # Git exclusions
├── README.md                   # This file
└── LICENSE                     # Project license
```

## 🔄 Recent Improvements (v2.0+)

✨ **Latest Enhancements:**
- 🎯 OpenRouter API support (unlimited quota!)
- 📍 Proximity-based location sorting
- 🏨 Up to 8 places per category (was 3)
- 📏 Distance calculation in kilometers
- 🛡️ Robust error handling & null checks
- ⏱️ Retry logic with exponential backoff
- 📋 Template fallback when APIs rate-limited
- 📱 Better Streamlit UI
- 🌐 Improved OpenStreetMap integration

## 📚 Example Response

```json
{
  "success": true,
  "destination": "Mumbai",
  "origin": "Delhi",
  "duration": 4,
  "budget": 25000,
  "travelers": 2,
  "comprehensive_plan": "📋 COMPLETE TRAVEL PLAN...\n\nDay 1: Arrival...",
  "maps_results": "🗺️ NEARBY PLACES...\n\n🏨 HOTELS\n1. Hotel Name\n   📏 Distance: 0.5 km...",
  "search_results": "Top destinations, costs, tips...",
  "generated_at": "2026-03-28T10:30:00"
}
```

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Areas for contribution:**
- Additional map data sources
- More language support
- Advanced filtering
- Mobile app version
- Database integration
- Docker containerization

## 📧 Contact & Support

- 👤 **Author**: sahasweety
- 🐙 **GitHub**: https://github.com/sahasweety/Travel_Agent
- 📮 **Issues**: Report bugs on GitHub Issues

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenRouter for seamless API aggregation
- OpenStreetMap for free location data
- Tavily for intelligent web search
- Google Gemini for AI capabilities
- Streamlit for the beautiful UI framework

---

**Built with ❤️ for wanderlust seekers | Last Updated: March 2026**

## 🏗️ System Architecture

### Three-Phase Processing

**Phase 1: Web Research** (Tavily API)
- Real-time travel information
- Attractions, activities, costs
- Budget estimates
- Safety tips, local customs
- Up to 10 research results

**Phase 2: Location Intelligence** (OpenStreetMap Nominatim - FREE)
- Hotels with ratings & distance sorting ⭐
- Restaurants with phone & hours 📞
- Tourist attractions with coordinates 📍
- Shopping areas & healthcare facilities 🏥
- **Up to 8 nearest places per category** (sorted by proximity)
- Rich metadata: address, phone, website, rating, distance

**Phase 3: AI Planning** (OpenRouter or Gemini)
- Synthesizes research + location data
- Generates detailed day-by-day itineraries
- Creates budget breakdowns
- Provides recommendations & backup plans

### API Integration Strategy

```
                    ┌─────────────────┐
                    │  Streamlit UI   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  TravelSystem   │
                    └────────┬────────┘
                             │
        ┌────────────────┬───┼───┬────────────────┐
        │                │   │   │                │
    ┌───▼──┐        ┌───▼──┐▼──▼──┐        ┌────▼───┐
    │Tavily│        │OpenStreetMap│        │OpenRouter
    │ API  │        │ or Gemini  │        │or Gemini
    └──────┘        └────────────┘        └─────────┘
```

### Error Handling & Resilience

✅ **Quota Exceeded (429)?**
- Automatic retry with exponential backoff
- Fallback to template-based plan
- Clear user guidance on upgrades

✅ **OpenStreetMap Errors?**
- Robust null-checking
- Graceful degradation
- Partial results continue

✅ **API Key Missing?**
- Clear error messages
- Guides on obtaining keys
- Validation on startup

### Data Flow

```
User Input (Destination, Dates, Budget)
          ↓
Tavily Search (Web Research)
          ↓
OpenStreetMap (Find nearby places)
          ↓
Sort by Distance (Proximity algorithm)
          ↓
OpenRouter/Gemini (Generate itinerary)
          ↓
Comprehensive Travel Plan Output
```

## 🗺️ Enhanced Location Search

### Smart Proximity Sorting

Places are **automatically sorted by distance** from your destination using the Haversine formula:

```
📍 Main Location: Mumbai Central
   Coordinates: 19.0133, 72.8325

🏨 HOTELS
1. The Oberoi Mumbai
   📏 Distance: 0.5 km ⬅️ Closest
   ☎️ +91-22-1234567
   🌐 www.oberoidelhi.com
   ⏰ 24/7
   ⭐ 4.8/5

2. Taj Hotel
   📏 Distance: 1.2 km
   ...

3. ITC Hotel
   📏 Distance: 2.1 km
   ...
```

### Location Categories

- 🏨 **Hotels** - Accommodation with ratings
- 🍽️ **Restaurants & Cafes** - Dining options
- 🎭 **Top Attractions** - Must-see places
- 🎪 **Things To Do** - Activities & experiences
- 🛍️ **Shopping Areas** - Malls & markets
- 🏥 **Healthcare** - Hospitals & pharmacies

### Rich Data Enrichment

Each place includes:
- ✅ Distance from destination (km)
- ✅ Exact street address
- ✅ Phone number
- ✅ Website & social media
- ✅ Operating hours
- ✅ User ratings

## 📊 Technology Stack

**Backend:**
- Python 3.8+
- Streamlit (Web UI)
- OpenRouter API (AI) - Gemini Pro
- Google Gemini API (AI) - Alternative
- Tavily API (Web Search)
- OpenStreetMap Nominatim (Location Data)
- httpx (Async HTTP)

**Features:**
- Async/await for concurrent requests
- Exponential backoff for rate limits
- Haversine distance calculation
- Template fallback for quota limits
- Comprehensive error handling

## 💰 API Costs Comparison (in Indian Rupees)

| Service | Cost | Limits | Notes |
|---------|------|--------|-------|
| **OpenRouter (Recommended)** | ~₹8-80/plan | ✅ Unlimited | Pay-as-you-go, best value |
| **Google Gemini Free** | Free | ❌ 60 req/min | Rate limited, quota resets daily |
| **Google Gemini Paid** | ₹6.23/Million input tokens | ✅ Unlimited | Reliable for production (~₹0.062 per 1000 tokens) |
| **Tavily API** | Free tier available | Limited | Essential for web research |
| **OpenStreetMap** | Free | ✅ Unlimited | No API key needed |

**Recommendation**: Start with OpenRouter free trial, then evaluate based on usage.

**Approximate Monthly Costs (for 100 plans/month):**
- OpenRouter: ₹800-8000/month
- Google Gemini Paid: ₹100-500/month (based on usage)
- Combined: ₹1000-8500/month

## ⚠️ Troubleshooting

### "Quota exceeded" Error

**Problem**: Free tier Gemini API exhausted
**Solutions**:
1. ✅ Switch to OpenRouter API (recommended)
2. ⏱️ Wait 24 hours for quota reset
3. 💳 Upgrade to paid Gemini API plan
4. 🔄 Get new API key with fresh quota

### "OpenStreetMap Error"

**Problem**: Location data not found
**Solutions**:
1. Verify location spelling
2. Use full city name (not abbreviation)
3. Try alternative search terms
4. Check internet connection

### "API Key Invalid"

**Problem**: Authentication failed
**Solutions**:
1. Regenerate API key from provider
2. Copy exact key without spaces
3. Check `.env` file permissions
4. Verify `OPENROUTER_API_KEY=` format

### Streamlit Port Already in Use

```bash
# Use different port
streamlit run st_app.py --server.port 8502
```

## 🔒 Security Best Practices

- ✅ API keys stored in `.env` (never in code)
- ✅ `.env` added to `.gitignore` automatically
- ✅ Input validation on all user inputs
- ✅ Secure async error handling
- ✅ No credentials logged or printed
- ✅ HTTPS for API communications
- ✅ Regular dependency updates recommended

## 📝 Environment Variables Reference

```env
# Web Research (Required)
TAVILY_API_KEY=tvly-...

# AI Model (Choose ONE)
OPENROUTER_API_KEY=sk-or-v1-...    # Recommended
GOOGLE_API_KEY1=AIzaSy...            # Alternative

# Optional
DEBUG=false                           # For troubleshooting
STREAMLIT_LOGGER_LEVEL=info
```

## 🚀 Performance Metrics

- ⚡ Average plan generation: ~30-45 seconds
- 🗺️ Location search: ~5-8 seconds  
- 🔍 Web research: ~8-12 seconds
- 💾 Support up to 10 travelers per plan

## Example Output

The system generates:
- Executive summary
- Day-by-day itinerary with timings
- 3-4 accommodation options
- Transportation guide
- Restaurant recommendations
- Complete budget breakdown
- Practical tips
- Backup plans

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## License

MIT License

## Acknowledgments

Built after attending AI Labs '25 Mumbai organized by Hack2skill and Google Cloud.

Special thanks to:
- Siddharth for AI Agents session
- Romin for MCP with Google ADK workshop

## Resources

- [Medium Article](YOUR_MEDIUM_LINK) - Detailed tutorial
- [Google Maps Platform](https://developers.google.com/maps)
- [Gemini API Docs](https://ai.google.dev/gemini-api/docs)
- [Tavily API](https://tavily.com)

## Contact

For questions or feedback, connect on LinkedIn: [Your Profile]

---

Star this repo if you find it helpful!
