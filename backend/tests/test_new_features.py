"""
Backend API Tests for AI Trading Bot Builder Platform
Testing P0-P3 features: Backtest engine, Deployments, News & Sentiment

Test user: backtest@test.com / Test123!
"""
import pytest
import requests
import os
import time

# Use environment variable for BASE_URL
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test user credentials
TEST_EMAIL = "backtest@test.com"
TEST_PASSWORD = "Test123!"


class TestSetup:
    """Setup and authentication tests"""
    
    @pytest.fixture(scope="class")
    def session(self):
        """Create a requests session"""
        s = requests.Session()
        s.headers.update({"Content-Type": "application/json"})
        return s
    
    @pytest.fixture(scope="class")
    def auth_token(self, session):
        """Get authentication token"""
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            token = response.json().get("token")
            return token
        # If login fails, try signup
        response = session.post(f"{BASE_URL}/api/auth/signup", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name": "Backtest User"
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Authentication failed - skipping authenticated tests")
    
    @pytest.fixture(scope="class")
    def auth_session(self, session, auth_token):
        """Create authenticated session"""
        session.headers.update({"Authorization": f"Bearer {auth_token}"})
        return session


class TestAuthentication(TestSetup):
    """Test authentication endpoints"""
    
    def test_login_success(self, session):
        """Test login with valid credentials"""
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        # Accept both 200 (existing user) and possibility of 401 if user doesn't exist
        if response.status_code == 401:
            # User might not exist, try signup
            signup_resp = session.post(f"{BASE_URL}/api/auth/signup", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "name": "Backtest User"
            })
            assert signup_resp.status_code in [200, 400], f"Signup failed: {signup_resp.text}"
            # Retry login
            response = session.post(f"{BASE_URL}/api/auth/login", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        print(f"✓ Login successful for {TEST_EMAIL}")
    
    def test_get_current_user(self, auth_session):
        """Test getting current user info"""
        response = auth_session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == TEST_EMAIL
        print(f"✓ Current user retrieved: {data['email']}")


class TestStrategies(TestSetup):
    """Test strategy CRUD operations"""
    
    def test_list_strategies(self, auth_session):
        """Test listing strategies"""
        response = auth_session.get(f"{BASE_URL}/api/strategies")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Listed {len(data)} strategies")
        return data
    
    def test_create_strategy(self, auth_session):
        """Test creating a new strategy"""
        strategy_data = {
            "name": "TEST_RSI_Strategy",
            "symbol": "BTCUSD",
            "timeframe": "1h",
            "entry": {
                "logic": "AND",
                "conditions": [{"type": "RSI", "condition": "oversold", "value": 30, "period": 14}]
            },
            "exit": {
                "logic": "OR",
                "conditions": [{"type": "RSI", "condition": "overbought", "value": 70, "period": 14}]
            },
            "risk": {
                "stop_loss_pct": 3,
                "take_profit_pct": 6,
                "max_position_size_pct": 20
            }
        }
        response = auth_session.post(f"{BASE_URL}/api/strategies", json=strategy_data)
        assert response.status_code in [200, 201]
        data = response.json()
        assert "id" in data or "strategy_id" in data or data.get("name") == "TEST_RSI_Strategy"
        print(f"✓ Strategy created successfully")
        return data


class TestBacktestEngine(TestSetup):
    """Test backtest functionality with institutional metrics"""
    
    def test_get_available_indicators(self, auth_session):
        """Test getting available indicators"""
        response = auth_session.get(f"{BASE_URL}/api/backtest/indicators")
        assert response.status_code == 200
        data = response.json()
        assert "trend" in data
        assert "momentum" in data
        assert "volatility" in data
        assert "volume" in data
        print(f"✓ Retrieved indicators: {list(data.keys())}")
    
    def test_list_backtests(self, auth_session):
        """Test listing backtest history"""
        response = auth_session.get(f"{BASE_URL}/api/backtests")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Listed {len(data)} backtests")
        return data
    
    def test_run_backtest_with_strategy(self, auth_session):
        """Test running a backtest with existing strategy"""
        # First get a strategy
        strat_resp = auth_session.get(f"{BASE_URL}/api/strategies")
        strategies = strat_resp.json()
        
        if not strategies:
            # Create a simple strategy first
            strategy_data = {
                "name": "TEST_Backtest_Strategy",
                "symbol": "BTCUSD",
                "timeframe": "1h",
                "entry": {
                    "logic": "AND",
                    "conditions": [{"type": "RSI", "condition": "oversold", "value": 30}]
                },
                "exit": {
                    "logic": "OR",
                    "conditions": [{"type": "RSI", "condition": "overbought", "value": 70}]
                },
                "risk": {"stop_loss_pct": 3, "take_profit_pct": 6, "max_position_size_pct": 20}
            }
            create_resp = auth_session.post(f"{BASE_URL}/api/strategies", json=strategy_data)
            assert create_resp.status_code in [200, 201]
            strat_resp = auth_session.get(f"{BASE_URL}/api/strategies")
            strategies = strat_resp.json()
        
        if strategies:
            strategy_id = strategies[0].get("id")
            
            backtest_data = {
                "strategy_id": strategy_id,
                "symbol": "BTCUSD",
                "timeframe": "1h",
                "initial_capital": 100000,
                "commission_pct": 0.1,
                "slippage_pct": 0.05
            }
            
            response = auth_session.post(f"{BASE_URL}/api/backtest/run", json=backtest_data, timeout=60)
            
            # Previous test showed 520 timeout, check current status
            if response.status_code == 200:
                data = response.json()
                assert "metrics" in data
                assert "equity_curve" in data
                assert "trades" in data
                
                # Verify institutional metrics
                metrics = data["metrics"]
                assert "sharpe_ratio" in metrics, "Missing Sharpe Ratio"
                assert "sortino_ratio" in metrics, "Missing Sortino Ratio"
                assert "max_drawdown" in metrics, "Missing Max Drawdown"
                assert "win_rate" in metrics, "Missing Win Rate"
                assert "profit_factor" in metrics, "Missing Profit Factor"
                
                print(f"✓ Backtest completed successfully")
                print(f"  - Total Return: {metrics.get('total_return_pct')}%")
                print(f"  - Sharpe Ratio: {metrics.get('sharpe_ratio')}")
                print(f"  - Sortino Ratio: {metrics.get('sortino_ratio')}")
                print(f"  - Max Drawdown: {metrics.get('max_drawdown')}%")
                print(f"  - Win Rate: {metrics.get('win_rate')}%")
            elif response.status_code in [500, 520]:
                pytest.fail(f"Backtest endpoint returns server error: {response.status_code} - {response.text[:200]}")
            else:
                print(f"Backtest response: {response.status_code} - {response.text[:200]}")
                assert False, f"Unexpected response: {response.status_code}"
        else:
            pytest.skip("No strategies available for backtest")


class TestDeployments(TestSetup):
    """Test deployment management functionality"""
    
    def test_list_deployments(self, auth_session):
        """Test listing all deployments"""
        response = auth_session.get(f"{BASE_URL}/api/deploy/list")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Listed {len(data)} deployments")
        return data
    
    def test_create_deployment(self, auth_session):
        """Test creating a new deployment"""
        # First get a strategy
        strat_resp = auth_session.get(f"{BASE_URL}/api/strategies")
        strategies = strat_resp.json()
        
        if not strategies:
            pytest.skip("No strategies available for deployment")
        
        strategy_id = strategies[0].get("id")
        
        deployment_data = {
            "strategy_id": strategy_id,
            "symbol": "BTCUSD",
            "timeframe": "1h",
            "initial_capital": 10000,
            "max_position_size_pct": 10,
            "mode": "paper",
            "auto_trade": False
        }
        
        response = auth_session.post(f"{BASE_URL}/api/deploy/create", json=deployment_data)
        
        # May fail if strategy already deployed
        if response.status_code == 400 and "already deployed" in response.text.lower():
            print("✓ Strategy already deployed (expected)")
            return None
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert "deployment_id" in data
        print(f"✓ Deployment created: {data.get('deployment_id')}")
        return data
    
    def test_get_deployment_details(self, auth_session):
        """Test getting deployment details"""
        # Get list first
        list_resp = auth_session.get(f"{BASE_URL}/api/deploy/list")
        deployments = list_resp.json()
        
        if not deployments:
            pytest.skip("No deployments available")
        
        deployment_id = deployments[0].get("id")
        response = auth_session.get(f"{BASE_URL}/api/deploy/{deployment_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == deployment_id
        print(f"✓ Retrieved deployment details for {deployment_id}")
        return data
    
    def test_check_signals(self, auth_session):
        """Test checking signals for a deployment"""
        # Get list first
        list_resp = auth_session.get(f"{BASE_URL}/api/deploy/list")
        deployments = list_resp.json()
        
        if not deployments:
            pytest.skip("No deployments available")
        
        # Find an active deployment
        active_deploy = next((d for d in deployments if d.get("status") == "active"), None)
        
        if not active_deploy:
            print("✓ No active deployments to check signals (expected)")
            return None
        
        deployment_id = active_deploy.get("id")
        response = auth_session.get(f"{BASE_URL}/api/deploy/{deployment_id}/signals")
        assert response.status_code == 200
        data = response.json()
        
        # May have signal data or message about insufficient data
        if "entry_signal" in data:
            print(f"✓ Signals checked - Entry: {data.get('entry_signal')}, Exit: {data.get('exit_signal')}")
        else:
            print(f"✓ Signal check returned: {data.get('message', data)}")
        return data
    
    def test_deployment_control(self, auth_session):
        """Test deployment pause/start/stop"""
        list_resp = auth_session.get(f"{BASE_URL}/api/deploy/list")
        deployments = list_resp.json()
        
        if not deployments:
            pytest.skip("No deployments available")
        
        deployment = deployments[0]
        deployment_id = deployment.get("id")
        current_status = deployment.get("status")
        
        if current_status == "active":
            # Test pause
            response = auth_session.post(f"{BASE_URL}/api/deploy/{deployment_id}/pause")
            assert response.status_code == 200
            print(f"✓ Deployment paused")
            
            # Test resume
            response = auth_session.post(f"{BASE_URL}/api/deploy/{deployment_id}/start")
            assert response.status_code == 200
            print(f"✓ Deployment resumed")
        elif current_status == "paused":
            # Test start
            response = auth_session.post(f"{BASE_URL}/api/deploy/{deployment_id}/start")
            assert response.status_code == 200
            print(f"✓ Deployment started from paused")
        else:
            print(f"✓ Deployment status is {current_status} - control test skipped")


class TestNewsSentiment(TestSetup):
    """Test news and sentiment analysis functionality"""
    
    def test_get_news_feed(self, auth_session):
        """Test getting news feed"""
        response = auth_session.get(f"{BASE_URL}/api/news/feed")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Retrieved {len(data)} news items")
        if data:
            print(f"  - Sample headline: {data[0].get('headline')[:50]}...")
        return data
    
    def test_get_symbol_news(self, auth_session):
        """Test getting news for specific symbol"""
        response = auth_session.get(f"{BASE_URL}/api/news/feed/BTCUSD")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for item in data:
            assert item.get("symbol") == "BTCUSD"
        print(f"✓ Retrieved {len(data)} BTCUSD news items")
        return data
    
    def test_analyze_sentiment(self, auth_session):
        """Test AI sentiment analysis"""
        headlines = [
            "Bitcoin surges past $100K on institutional demand",
            "Regulatory concerns grow over crypto exchanges",
            "Market remains stable amid economic uncertainty"
        ]
        
        response = auth_session.post(f"{BASE_URL}/api/news/analyze", json={
            "headlines": headlines,
            "symbols": ["BTCUSD"]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert "aggregate" in data
        
        # Verify results structure
        results = data["results"]
        assert len(results) == len(headlines)
        
        for r in results:
            assert "score" in r
            assert "label" in r
            assert -1 <= r["score"] <= 1
            assert r["label"] in ["Strong Bullish", "Bullish", "Neutral", "Bearish", "Strong Bearish"]
        
        # Verify aggregate
        agg = data["aggregate"]
        assert "avg_score" in agg
        assert "label" in agg
        assert "bullish_count" in agg
        assert "bearish_count" in agg
        
        print(f"✓ Sentiment analysis completed")
        print(f"  - Average Score: {agg.get('avg_score')}")
        print(f"  - Label: {agg.get('label')}")
        print(f"  - Analysis Type: {'AI' if results[0].get('ai_analyzed') else 'Keyword (fallback)'}")
        return data
    
    def test_get_symbol_sentiment_aggregate(self, auth_session):
        """Test getting aggregated sentiment for symbol"""
        response = auth_session.get(f"{BASE_URL}/api/news/sentiment/aggregate/BTCUSD")
        assert response.status_code == 200
        data = response.json()
        
        assert "symbol" in data
        assert "avg_score" in data
        assert "label" in data
        
        print(f"✓ Symbol sentiment retrieved: {data.get('symbol')} - {data.get('label')}")
        return data


class TestMarketData(TestSetup):
    """Test market data endpoints"""
    
    def test_get_latest_prices(self, auth_session):
        """Test getting latest prices"""
        response = auth_session.get(f"{BASE_URL}/api/market/latest_prices")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        print(f"✓ Retrieved prices for {len(data)} symbols")
        return data
    
    def test_get_symbols(self, auth_session):
        """Test getting available symbols"""
        response = auth_session.get(f"{BASE_URL}/api/market/symbols")
        assert response.status_code == 200
        data = response.json()
        # API returns dict with symbols and timeframes
        if isinstance(data, dict):
            symbols = data.get("symbols", [])
            assert len(symbols) > 0
            print(f"✓ Retrieved {len(symbols)} symbols: {symbols}")
        else:
            assert isinstance(data, list)
            print(f"✓ Retrieved {len(data)} symbols")


# Run all tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
