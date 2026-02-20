"""
Backend API Tests for AI Trading Bot Builder - P4 & P5 Features
Testing: ML Bot Builder, Admin Terminal, News & Sentiment APIs
Test user: admin@test.com / admin123
"""
import pytest
import requests
import os
import time

# Use environment variable for BASE_URL
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin test credentials
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "admin123"


class TestSetup:
    """Setup and authentication"""
    
    @pytest.fixture(scope="class")
    def session(self):
        """Create requests session"""
        s = requests.Session()
        s.headers.update({"Content-Type": "application/json"})
        return s
    
    @pytest.fixture(scope="class")
    def auth_token(self, session):
        """Get authentication token"""
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Authentication failed: {response.text}")
    
    @pytest.fixture(scope="class")
    def auth_session(self, session, auth_token):
        """Create authenticated session"""
        session.headers.update({"Authorization": f"Bearer {auth_token}"})
        return session


# ================== ML BOT BUILDER TESTS ==================

class TestMLBotBuilder(TestSetup):
    """Test ML Bot Builder endpoints (P4)"""
    
    def test_get_templates(self, auth_session):
        """Test GET /api/ml/templates - Should return ML model templates"""
        response = auth_session.get(f"{BASE_URL}/api/ml/templates")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "templates" in data, "Response should have 'templates' key"
        assert isinstance(data["templates"], list), "Templates should be a list"
        
        if data["templates"]:
            template = data["templates"][0]
            assert "id" in template, "Template should have 'id'"
            assert "name" in template, "Template should have 'name'"
            assert "model_type" in template, "Template should have 'model_type'"
            assert "features" in template, "Template should have 'features'"
            
        print(f"✓ Retrieved {len(data['templates'])} ML templates")
        for t in data["templates"][:3]:
            print(f"  - {t.get('name')}: {t.get('model_type')}")
        return data
    
    def test_get_features(self, auth_session):
        """Test GET /api/ml/features - Should return available ML features"""
        response = auth_session.get(f"{BASE_URL}/api/ml/features")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "features" in data, "Response should have 'features'"
        assert "targets" in data, "Response should have 'targets'"
        assert "model_types" in data, "Response should have 'model_types'"
        
        assert len(data["features"]) > 0, "Should have at least one feature"
        assert len(data["targets"]) > 0, "Should have at least one target"
        
        # Verify feature structure
        feature = data["features"][0]
        assert "name" in feature, "Feature should have 'name'"
        assert "category" in feature, "Feature should have 'category'"
        assert "description" in feature, "Feature should have 'description'"
        
        print(f"✓ Retrieved {len(data['features'])} features, {len(data['targets'])} targets")
        return data
    
    def test_list_models(self, auth_session):
        """Test GET /api/ml/models - Should list user's trained models"""
        response = auth_session.get(f"{BASE_URL}/api/ml/models")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ Found {len(data)} trained ML models")
        return data


# ================== ADMIN TERMINAL TESTS ==================

class TestAdminTerminal(TestSetup):
    """Test Admin Terminal endpoints (P5) - Requires admin role"""
    
    def test_admin_dashboard(self, auth_session):
        """Test GET /api/admin/dashboard - Should return platform stats"""
        response = auth_session.get(f"{BASE_URL}/api/admin/dashboard")
        
        if response.status_code == 403:
            pytest.skip("Admin access required - user may not have admin role")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify dashboard structure
        assert "users" in data, "Dashboard should have 'users' section"
        assert "trading" in data, "Dashboard should have 'trading' section"
        assert "capital" in data, "Dashboard should have 'capital' section"
        
        # Verify users section
        users = data["users"]
        assert "total" in users, "Users should have 'total'"
        assert "active" in users, "Users should have 'active'"
        assert "new_this_week" in users, "Users should have 'new_this_week'"
        
        # Verify trading section
        trading = data["trading"]
        assert "strategies" in trading, "Trading should have 'strategies'"
        assert "backtests" in trading, "Trading should have 'backtests'"
        assert "active_deployments" in trading, "Trading should have 'active_deployments'"
        
        print(f"✓ Admin dashboard retrieved")
        print(f"  - Total users: {users.get('total')}")
        print(f"  - Active users: {users.get('active')}")
        print(f"  - Total strategies: {trading.get('strategies')}")
        print(f"  - Active deployments: {trading.get('active_deployments')}")
        return data
    
    def test_list_users(self, auth_session):
        """Test GET /api/admin/users - Should list all platform users"""
        response = auth_session.get(f"{BASE_URL}/api/admin/users")
        
        if response.status_code == 403:
            pytest.skip("Admin access required")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "users" in data, "Response should have 'users'"
        assert "total" in data, "Response should have 'total'"
        
        users = data["users"]
        assert isinstance(users, list), "Users should be a list"
        
        if users:
            user = users[0]
            assert "id" in user, "User should have 'id'"
            assert "email" in user, "User should have 'email'"
            assert "hashed_password" not in user, "Password should be excluded"
        
        print(f"✓ Retrieved {len(users)} users (total: {data.get('total')})")
        return data
    
    def test_monitoring_activity(self, auth_session):
        """Test GET /api/admin/monitoring/activity - Platform activity"""
        response = auth_session.get(f"{BASE_URL}/api/admin/monitoring/activity", params={"hours": 24})
        
        if response.status_code == 403:
            pytest.skip("Admin access required")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "backtests" in data, "Should have 'backtests' section"
        assert "deployments" in data, "Should have 'deployments' section"
        assert "trades" in data, "Should have 'trades' section"
        
        print(f"✓ Activity (24h): {data['backtests'].get('count')} backtests, {data['trades'].get('count')} trades")
        return data
    
    def test_active_deployments(self, auth_session):
        """Test GET /api/admin/monitoring/active-deployments"""
        response = auth_session.get(f"{BASE_URL}/api/admin/monitoring/active-deployments")
        
        if response.status_code == 403:
            pytest.skip("Admin access required")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "total_active" in data, "Should have 'total_active'"
        assert "unique_users" in data, "Should have 'unique_users'"
        assert "deployments" in data, "Should have 'deployments'"
        
        print(f"✓ Active deployments: {data.get('total_active')} across {data.get('unique_users')} users")
        return data


# ================== NEWS & SENTIMENT TESTS ==================

class TestNewsSentiment(TestSetup):
    """Test News & Sentiment endpoints"""
    
    def test_news_feed(self, auth_session):
        """Test GET /api/news/feed - Should return news items"""
        response = auth_session.get(f"{BASE_URL}/api/news/feed")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert isinstance(data, list), "Response should be a list"
        
        if data:
            news = data[0]
            assert "headline" in news, "News should have 'headline'"
            assert "source" in news, "News should have 'source'"
            assert "timestamp" in news, "News should have 'timestamp'"
            
        print(f"✓ Retrieved {len(data)} news items")
        if data:
            print(f"  - Sample: {data[0].get('headline')[:60]}...")
        return data
    
    def test_symbol_news(self, auth_session):
        """Test GET /api/news/feed/{symbol} - News for specific symbol"""
        symbols_to_test = ["BTCUSD", "RELIANCE.NS"]
        
        for symbol in symbols_to_test:
            response = auth_session.get(f"{BASE_URL}/api/news/feed/{symbol}")
            assert response.status_code == 200, f"Expected 200 for {symbol}, got {response.status_code}"
            data = response.json()
            assert isinstance(data, list), f"Response for {symbol} should be list"
            print(f"✓ Retrieved {len(data)} news items for {symbol}")
        
        return True
    
    def test_market_news(self, auth_session):
        """Test GET /api/news/market - General market news"""
        response = auth_session.get(f"{BASE_URL}/api/news/market")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ Retrieved {len(data)} market news items")
        return data
    
    def test_analyze_sentiment(self, auth_session):
        """Test POST /api/news/analyze - AI sentiment analysis"""
        headlines = [
            "Reliance Industries reports record quarterly profits",
            "Market crash fears grow amid global uncertainty",
            "Tech stocks remain stable despite volatility"
        ]
        
        response = auth_session.post(f"{BASE_URL}/api/news/analyze", json={
            "headlines": headlines,
            "symbols": ["RELIANCE.NS"]
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "results" in data, "Response should have 'results'"
        assert "aggregate" in data, "Response should have 'aggregate'"
        
        # Verify results
        results = data["results"]
        assert len(results) == len(headlines), f"Should have {len(headlines)} results"
        
        for r in results:
            assert "score" in r, "Result should have 'score'"
            assert "label" in r, "Result should have 'label'"
            assert -1 <= r["score"] <= 1, "Score should be between -1 and 1"
            assert r["label"] in ["Strong Bullish", "Bullish", "Neutral", "Bearish", "Strong Bearish"]
        
        # Verify aggregate
        agg = data["aggregate"]
        assert "avg_score" in agg, "Aggregate should have 'avg_score'"
        assert "label" in agg, "Aggregate should have 'label'"
        
        # Check if AI or keyword-based
        analysis_type = "AI" if results[0].get("ai_analyzed") else "Keyword (fallback - DeepSeek insufficient balance)"
        
        print(f"✓ Sentiment analysis completed - {analysis_type}")
        print(f"  - Average score: {agg.get('avg_score'):.3f}")
        print(f"  - Label: {agg.get('label')}")
        print(f"  - Bullish: {agg.get('bullish_count')}, Bearish: {agg.get('bearish_count')}, Neutral: {agg.get('neutral_count')}")
        return data
    
    def test_sentiment_aggregate(self, auth_session):
        """Test GET /api/news/sentiment/aggregate/{symbol}"""
        response = auth_session.get(f"{BASE_URL}/api/news/sentiment/aggregate/BTCUSD")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "symbol" in data, "Should have 'symbol'"
        assert "avg_score" in data, "Should have 'avg_score'"
        assert "label" in data, "Should have 'label'"
        
        print(f"✓ BTCUSD sentiment aggregate: {data.get('label')} (score: {data.get('avg_score'):.3f})")
        return data
    
    def test_trending_topics(self, auth_session):
        """Test GET /api/news/trending"""
        response = auth_session.get(f"{BASE_URL}/api/news/trending")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ Retrieved {len(data)} trending topics")
        return data


# ================== MARKET DATA TESTS ==================

class TestMarketData(TestSetup):
    """Test market data endpoints - yfinance integration"""
    
    def test_latest_prices(self, auth_session):
        """Test GET /api/market/latest_prices - Real prices from yfinance"""
        response = auth_session.get(f"{BASE_URL}/api/market/latest_prices")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert isinstance(data, dict), "Response should be a dict"
        
        # Verify price data structure
        if data:
            for symbol, price_info in list(data.items())[:3]:
                assert "price" in price_info, f"{symbol} should have 'price'"
                assert "change" in price_info, f"{symbol} should have 'change'"
                print(f"  - {symbol}: ₹{price_info.get('price'):.2f} ({price_info.get('change_pct', 0):.2f}%)")
        
        print(f"✓ Retrieved prices for {len(data)} symbols")
        return data
    
    def test_symbol_price(self, auth_session):
        """Test GET /api/market/price/{symbol} - Individual stock price"""
        response = auth_session.get(f"{BASE_URL}/api/market/price/RELIANCE.NS")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "price" in data, "Should have 'price'"
        assert "symbol" in data, "Should have 'symbol'"
        
        print(f"✓ RELIANCE.NS price: ₹{data.get('price'):.2f}")
        return data
    
    def test_nifty50(self, auth_session):
        """Test GET /api/market/nifty50 - NIFTY 50 stocks"""
        response = auth_session.get(f"{BASE_URL}/api/market/nifty50")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "stocks" in data, "Should have 'stocks'"
        assert "count" in data, "Should have 'count'"
        
        stocks = data["stocks"]
        assert len(stocks) > 0, "Should have NIFTY 50 stocks"
        
        # Verify stock structure
        stock = stocks[0]
        assert "symbol" in stock, "Stock should have 'symbol'"
        assert "name" in stock, "Stock should have 'name'"
        assert "price" in stock, "Stock should have 'price'"
        
        print(f"✓ Retrieved {data.get('count')} NIFTY 50 stocks")
        return data
    
    def test_symbols(self, auth_session):
        """Test GET /api/market/symbols - Available trading symbols"""
        response = auth_session.get(f"{BASE_URL}/api/market/symbols")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "symbols" in data, "Should have 'symbols'"
        assert "total" in data, "Should have 'total'"
        
        print(f"✓ Retrieved {data.get('total')} available symbols")
        return data
    
    def test_sectors(self, auth_session):
        """Test GET /api/market/sectors - Available sectors"""
        response = auth_session.get(f"{BASE_URL}/api/market/sectors")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "sectors" in data, "Should have 'sectors'"
        
        print(f"✓ Retrieved sectors: {data.get('sectors')[:5]}...")
        return data


# Run all tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
