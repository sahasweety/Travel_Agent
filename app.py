import os
import asyncio
import time
from typing import Dict, Any
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class TravelPlanningSystem:
    def __init__(self):
        # Initialize API keys (Google Maps replaced with free OpenStreetMap)
        self.tavily_api_key = self._get_tavily_api_key()
        self.gemini_api_key = self._get_gemini_api_key()
        self.openrouter_api_key = self._get_openrouter_api_key()
        
        # Validate required API keys
        self._validate_api_keys()
        
        # Determine which AI service to use
        self.use_openrouter = bool(self.openrouter_api_key)
        self.model = None
        
        if self.use_openrouter:
            print("✅ Travel system initialized with OpenRouter API + OpenStreetMap (free)")
            print(f"   Using model: google/gemini-2.0-flash or gemini-pro via OpenRouter")
        else:
            # Fallback to direct Gemini API
            genai.configure(api_key=self.gemini_api_key)
            try:
                self.model = genai.GenerativeModel("gemini-2.0-flash")
                print("✅ Travel system initialized with Gemini 2.0 Flash + OpenStreetMap (free)")
            except Exception:
                # Fallback to gemini-pro if 2.0 is not available
                self.model = genai.GenerativeModel("gemini-pro")
                print("✅ Travel system initialized with Gemini Pro + OpenStreetMap (free)")

    
    def _get_tavily_api_key(self) -> str:
        """Retrieve Tavily API key from environment"""
        api_key = os.environ.get("TAVILY_API_KEY")
        if not api_key:
            print("ERROR: TAVILY_API_KEY is not set.")
            raise ValueError("TAVILY_API_KEY is required")
        return api_key
    
    def _get_gemini_api_key(self) -> str:
        """Retrieve Gemini API key from environment"""
        api_key = os.environ.get("GOOGLE_API_KEY1")
        if not api_key:
            print("ERROR: GOOGLE_API_KEY1 is not set.")
            raise ValueError("GOOGLE_API_KEY1 is required")
        return api_key
    
    def _get_openrouter_api_key(self) -> str:
        """Retrieve OpenRouter API key from environment (optional)"""
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if api_key:
            print(f"✓ OpenRouter API key found")
        else:
            print("ℹ  OpenRouter API key not configured. Will use direct Gemini API.")
        return api_key
    
    def _validate_api_keys(self):
        """Validate that all required API keys are present"""
        # Either OpenRouter or Gemini API key is required
        if not self.openrouter_api_key and not self.gemini_api_key:
            raise ValueError("Either OPENROUTER_API_KEY or GOOGLE_API_KEY1 is required")
        
        if not self.tavily_api_key:
            raise ValueError("TAVILY_API_KEY is required")
        
        print("✓ All required API keys are configured")

    async def search_with_tavily(self, query: str) -> str:
        """Search using Tavily API directly"""
        try:
            import httpx
            
            url = "https://api.tavily.com/search"
            headers = {"content-type": "application/json"}
            payload = {
                "api_key": self.tavily_api_key,
                "query": query,
                "search_depth": "advanced",
                "include_answer": True,
                "max_results": 10
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                # Format results
                answer = data.get("answer", "")
                results = data.get("results", [])
                
                formatted = f"Search Answer: {answer}\n\n"
                formatted += "Top Results:\n"
                for i, result in enumerate(results[:5], 1):
                    formatted += f"\n{i}. {result.get('title', 'N/A')}\n"
                    formatted += f"   {result.get('content', 'N/A')}\n"
                    formatted += f"   Source: {result.get('url', 'N/A')}\n"
                
                return formatted
                
        except Exception as e:
            print(f"Tavily search error: {str(e)}")
            return f"Search error: {str(e)}"
    
    async def search_with_maps(self, query: str) -> str:
        """Search using OpenStreetMap Nominatim API with proximity sorting"""
        try:
            import httpx
            import math
            
            # Nominatim requires a User-Agent header
            headers = {
                "User-Agent": "TravelPlanningAgent/1.0 (travel-planning-app)"
            }
            
            # Extract location from query
            parts = query.split(" in ")
            if len(parts) > 1:
                location = parts[-1]
            else:
                location = query
            
            url = "https://nominatim.openstreetmap.org/search"
            formatted = "🗺️ NEARBY PLACES & INSIGHTS:\n\n"
            destination_lat = None
            destination_lon = None
            
            # Search for location first to get coordinates
            location_params = {
                "q": location,
                "format": "json",
                "limit": 1,
                "addressdetails": 1,
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                try:
                    # Get destination coordinates
                    response = await client.get(url, params=location_params, headers=headers, timeout=10.0)
                    response.raise_for_status()
                    location_results = response.json()
                    
                    if location_results and isinstance(location_results, list) and len(location_results) > 0:
                        location_info = location_results[0]
                        if location_info and isinstance(location_info, dict):
                            display_name = location_info.get('display_name', location)
                            destination_lat = float(location_info.get('lat', 0))
                            destination_lon = float(location_info.get('lon', 0))
                            formatted += f"📍 Main Location: {display_name}\n"
                            formatted += f"   Coordinates: {destination_lat:.4f}, {destination_lon:.4f}\n\n"
                except Exception as loc_error:
                    print(f"Location lookup error: {str(loc_error)}")
                    formatted += f"📍 Location: {location}\n\n"
                
                # Search for specific amenities with more results
                search_queries = [
                    ("🏨 Hotels Near You", f"hotels in {location}"),
                    ("🍽️ Restaurants & Cafes", f"restaurants in {location}"),
                    ("🎭 Top Attractions", f"tourist attractions in {location}"),
                    ("🎪 Things To Do", f"things to do in {location}"),
                    ("🛍️ Shopping Areas", f"shopping malls in {location}"),
                    ("🏥 Healthcare", f"hospitals pharmacies in {location}")
                ]
                
                for category_emoji, search_q in search_queries:
                    try:
                        # Request more results to sort by distance
                        params = {
                            "q": search_q,
                            "format": "json",
                            "limit": 15,  # Get more results to sort by distance
                            "addressdetails": 1,
                            "extratags": 1
                        }
                        
                        response = await client.get(url, params=params, headers=headers, timeout=10.0)
                        response.raise_for_status()
                        results = response.json()
                        
                        if results and isinstance(results, list) and len(results) > 0:
                            # Calculate distance from destination for each place
                            results_with_distance = []
                            for place in results:
                                if place is None or not isinstance(place, dict):
                                    continue
                                
                                try:
                                    place_lat = float(place.get('lat', 0))
                                    place_lon = float(place.get('lon', 0))
                                    
                                    # Calculate distance using Haversine formula (rough approximation)
                                    if destination_lat and destination_lon:
                                        lat_diff = (place_lat - destination_lat) * 111  # 1 degree ≈ 111 km
                                        lon_diff = (place_lon - destination_lon) * 111 * math.cos(math.radians(destination_lat))
                                        distance_km = math.sqrt(lat_diff**2 + lon_diff**2)
                                    else:
                                        distance_km = 0
                                    
                                    results_with_distance.append({
                                        'distance': distance_km,
                                        'place': place
                                    })
                                except (ValueError, TypeError):
                                    continue
                            
                            # Sort by distance
                            results_with_distance.sort(key=lambda x: x['distance'])
                            
                            formatted += f"\n{'='*70}\n{category_emoji}\n{'='*70}\n\n"
                            
                            # Show top 8 nearest places
                            for i, item in enumerate(results_with_distance[:8], 1):
                                place = item['place']
                                distance = item['distance']
                                
                                display_name = place.get('display_name', 'N/A')
                                place_class = place.get('class', 'N/A')
                                extra = place.get('extratags', {}) or {}
                                website = extra.get('website', '')
                                phone = extra.get('phone', '')
                                opening_hours = extra.get('opening_hours', '')
                                rating = extra.get('rating', '')
                                address = place.get('address', {}) if isinstance(place.get('address'), dict) else {}
                                
                                formatted += f"{i}. {display_name}\n"
                                formatted += f"   📏 Distance: {distance:.1f} km\n"
                                formatted += f"   Category: {place_class}\n"
                                
                                # Extract street address if available
                                street = address.get('road', address.get('street', ''))
                                if street:
                                    formatted += f"   📮 {street}\n"
                                
                                if phone:
                                    formatted += f"   ☎️ {phone}\n"
                                if website:
                                    formatted += f"   🌐 {website}\n"
                                if opening_hours:
                                    formatted += f"   ⏰ {opening_hours}\n"
                                if rating:
                                    formatted += f"   ⭐ {rating}/5\n"
                                formatted += "\n"
                    except Exception as search_error:
                        print(f"Error searching for {search_q}: {str(search_error)}")
                        continue
                
                return formatted if formatted.strip() else f"Unable to find detailed location information for: {location}"
                
        except Exception as e:
            print(f"OpenStreetMap search error: {str(e)}")
            return f"Note: Map data temporarily unavailable. Please try again."
    
    async def generate_with_context(self, prompt: str, context: str = "", max_retries: int = 2) -> str:
        """Generate response using either OpenRouter or Gemini API with retry logic"""
        retry_count = 0
        base_wait_time = 2
        
        while retry_count < max_retries:
            try:
                full_prompt = f"{context}\n\n{prompt}" if context else prompt
                
                if self.use_openrouter:
                    # Use OpenRouter API
                    return await self._generate_with_openrouter(full_prompt, retry_count, max_retries)
                else:
                    # Use direct Gemini API
                    response = await asyncio.to_thread(
                        self.model.generate_content,
                        full_prompt
                    )
                    return response.text
                    
            except Exception as e:
                error_str = str(e)
                
                # Check for quota exceeded errors (429)
                if "429" in error_str or "quota" in error_str.lower():
                    retry_count += 1
                    if retry_count < max_retries:
                        wait_time = base_wait_time * (2 ** (retry_count - 1))
                        print(f"⏳ Rate limit hit. Retrying in {wait_time}s (attempt {retry_count}/{max_retries})...")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        print("⚠️  API quota exceeded. Generating simplified plan...")
                        return self._generate_simplified_plan(context=context, prompt=prompt)
                else:
                    print(f"Generation error: {error_str}")
                    return f"⚠️ Generation error: {error_str}"
        
        return "Unable to generate travel plan due to API limitations."
    
    async def _generate_with_openrouter(self, prompt: str, retry_count: int, max_retries: int) -> str:
        """Generate content using OpenRouter API"""
        try:
            import httpx
            
            # OpenRouter endpoint
            url = "https://openrouter.ai/api/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "HTTP-Referer": "travel-planning-app",
                "Content-Type": "application/json"
            }
            
            # Use Gemini Pro via OpenRouter - try different model options
            # Available models: google/gemini-pro, google/gemini-pro-vision, etc.
            payload = {
                "model": "google/gemini-pro",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt[:4000]  # Limit prompt to 4000 chars to avoid token issues
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 1500
            }
            
            print(f"📤 Sending request to OpenRouter with model: {payload['model']}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                
                # Log response details for debugging
                if response.status_code != 200:
                    error_body = response.text
                    print(f"❌ OpenRouter Error {response.status_code}: {error_body}")
                
                response.raise_for_status()
                data = response.json()
                
                if "choices" in data and len(data["choices"]) > 0:
                    result = data["choices"][0]["message"]["content"]
                    print(f"✅ OpenRouter response received ({len(result)} chars)")
                    return result
                else:
                    error_msg = f"Unexpected response format: {data}"
                    print(f"❌ {error_msg}")
                    return error_msg
                    
        except Exception as e:
            error_str = str(e)
            print(f"❌ OpenRouter generation error: {error_str}")
            
            # If it's a 400 error, try fallback
            if "400" in error_str:
                print("⚠️  Trying fallback model...")
                try:
                    return await self._generate_with_openrouter_fallback(prompt)
                except Exception as fallback_error:
                    print(f"Fallback also failed: {str(fallback_error)}")
            
            # Retry logic for rate limits
            if "429" in error_str:
                if retry_count < max_retries - 1:
                    wait_time = 2 * (2 ** retry_count)
                    print(f"⏳ Rate limit hit. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    return await self._generate_with_openrouter(prompt, retry_count + 1, max_retries)
                else:
                    return self._generate_simplified_plan("", prompt)
            
            raise Exception(error_str)
    
    async def _generate_with_openrouter_fallback(self, prompt: str) -> str:
        """Fallback method using different OpenRouter model"""
        try:
            import httpx
            
            url = "https://openrouter.ai/api/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "HTTP-Referer": "travel-planning-app",
                "Content-Type": "application/json"
            }
            
            # Try Claude if Gemini fails
            payload = {
                "model": "anthropic/claude-3-haiku",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt[:4000]
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 1500
            }
            
            print(f"📤 Trying fallback model: {payload['model']}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                if "choices" in data and len(data["choices"]) > 0:
                    result = data["choices"][0]["message"]["content"]
                    print(f"✅ Fallback model response received ({len(result)} chars)")
                    return result
                    
        except Exception as e:
            print(f"Fallback model also failed: {str(e)}")
            raise
    
    def _generate_simplified_plan(self, context: str, prompt: str) -> str:
        """Generate a simplified travel plan when API quota is exceeded"""
        # Extract key information from prompt
        lines = prompt.split('\n')
        destination = next((line.split(': ')[1] for line in lines if 'Destination:' in line), 'Unknown')
        
        # Extract duration as integer
        duration_str = next((line.split(': ')[1] for line in lines if 'Duration:' in line), '3')
        try:
            duration = int(duration_str.split()[0])  # Extract number from "3 days"
        except (ValueError, IndexError):
            duration = 3
            
        budget = next((line.split(': ')[1] for line in lines if 'Budget:' in line), '₹25,000')
        
        plan = f"""📋 SIMPLIFIED TRAVEL PLAN - {destination}
{'='*70}

Note: Full AI generation temporarily unavailable due to API quota limits.

🏨 ESSENTIAL INFORMATION:
- Budget: {budget}
- Duration: {duration} days
- Destination: {destination}

📅 SUGGESTED ITINERARY:
Day 1: Arrival & Exploration
  • Arrive and check-in to hotel
  • Explore nearby area and local market
  • Dinner at local restaurant

Days 2-{duration-1}: Main Activities
  • Visit major attractions and landmarks
  • Try local cuisine at restaurants
  • Experience cultural sites
  • Day trips if recommended

Day {duration}: Departure
  • Last-minute shopping or sightseeing
  • Depart for airport/station

💰 BUDGET BREAKDOWN:
- Accommodation: ~35% of budget
- Food & Dining: ~25% of budget
- Activities/Attractions: ~25% of budget
- Transport & Shopping: ~15% of budget

✅ PRACTICAL RECOMMENDATIONS:
1. Book accommodation in advance
2. Use public transportation (buses, metro)
3. Visit local markets for authentic experience
4. Try both street food and restaurants
5. Check weather forecast before packing
6. Keep copies of important documents

⚠️ API QUOTA INFORMATION:
Your Gemini API free tier has reached its daily limit.

To get full AI-powered detailed itineraries:
• Upgrade to Gemini API paid plan
• Wait for quota reset (24 hours)
• Use a new API key with fresh quota

Learn more: https://ai.google.dev/gemini-api/docs/rate-limits
Monitor usage: https://ai.dev/rate-limit
"""
        return plan
    
    async def process_travel_request(self, travel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a travel request using direct API calls"""
        try:
            print(f"Processing travel request for {travel_data.get('to', 'Unknown')}")
            
            # Extract travel data
            destination = travel_data.get('to', '').replace('(', '').replace(')', '')
            origin = travel_data.get('from', '').replace('(', '').replace(')', '')
            departure_date = travel_data.get('departureDate')
            return_date = travel_data.get('returnDate')
            budget = self._parse_budget(travel_data.get('budget', 'mid'))
            passengers = int(travel_data.get('passengers', 1))
            
            # Calculate duration
            if departure_date and return_date:
                departure = datetime.fromisoformat(departure_date)
                return_dt = datetime.fromisoformat(return_date)
                duration = (return_dt - departure).days
            else:
                duration = 3
            
            print(f"{origin} → {destination}, {duration} days, ₹{budget:,}, {passengers} travelers")

            # Phase 1: Search for destination info
            print("Phase 1: Searching destination information...")
            search_query = f"""Find travel information for {destination} including:
- Top attractions and activities with prices
- Hotel recommendations and costs in Indian Rupees
- Best restaurants and dining costs
- Local transportation options and costs
- Weather and best time to visit
- Safety tips and local customs
- Daily budget estimates for {passengers} travelers"""
            
            search_results = await self.search_with_tavily(search_query)
            print("Search completed")
            
            # Phase 2: Get location info
            print("Phase 2: Getting location information...")
            maps_query = f"hotels restaurants attractions in {destination}"
            maps_results = await self.search_with_maps(maps_query)
            print("Maps search completed")
            
            # Phase 3: Generate comprehensive plan
            print("Phase 3: Creating travel plan...")
            planning_prompt = f"""Create a detailed {duration}-day travel plan for {destination}.

TRIP DETAILS:
- Origin: {origin}
- Destination: {destination}
- Duration: {duration} days
- Budget: ₹{budget:,}
- Travelers: {passengers}
- Dates: {departure_date} to {return_date}

SEARCH RESULTS:
{search_results}

LOCATION DATA:
{maps_results}

Create a comprehensive plan with:
1. Executive Summary
2. Day-by-day detailed itinerary with timings
3. Accommodation recommendations (3-4 options)
4. Transportation guide
5. Food & dining suggestions
6. Complete budget breakdown
7. Practical tips
8. Backup plans

Ensure the plan stays within ₹{budget:,} budget and includes specific costs."""
            
            final_plan = await self.generate_with_context(planning_prompt)
            print("Plan created")
            
            return {
                'success': True,
                'destination': destination,
                'origin': origin,
                'duration': duration,
                'budget': budget,
                'travelers': passengers,
                'search_results': search_results,
                'maps_results': maps_results,
                'comprehensive_plan': final_plan,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'generated_at': datetime.now().isoformat()
            }
    
    def _parse_budget(self, budget_range: str) -> int:
        """Convert budget range to numeric value"""
        budget_mapping = {
            'budget': 10000,
            'mid': 25000,
            'premium': 55000,
            'luxury': 100000
        }
        return budget_mapping.get(budget_range, 25000)

# Sync wrapper for FastAPI
def plan_trip(trip_request: Dict[str, Any]) -> Dict[str, Any]:
    """Synchronous wrapper for FastAPI"""
    try:
        travel_system = TravelPlanningSystem()
        return asyncio.run(travel_system.process_travel_request(trip_request))
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# Test code
if __name__ == "__main__":
    sample_request = {
        "from": "Delhi (DEL)",
        "to": "Mumbai (BOM)",
        "departureDate": "2025-10-15",
        "returnDate": "2025-10-18",
        "passengers": "2",
        "travelClass": "economy",
        "tripType": "roundtrip",
        "budget": "mid"
    }
    
    print("\n Testing travel planning system...")
    result = plan_trip(sample_request)
    
    if result['success']:
        print("\n Success!")
        with open('travel_plan.txt', 'w', encoding='utf-8') as f:
            f.write("COMPREHENSIVE TRAVEL PLAN\n")
            f.write("="*80 + "\n\n")
            f.write(result['comprehensive_plan'])
            f.write("\n\n" + "="*80 + "\n")
            f.write("SEARCH RESULTS\n")
            f.write("="*80 + "\n\n")
            f.write(result['search_results'])
            f.write("\n\n" + "="*80 + "\n")
            f.write("MAPS RESULTS\n")
            f.write("="*80 + "\n\n")
            f.write(result['maps_results'])
        print("Full plan saved to travel_plan.txt")
    else:
        print(f"\n Failed: {result.get('error')}")