import requests
import sys
import json
import time
from datetime import datetime

class TradingBotAPITester:
    def __init__(self, base_url="https://tradeforge-16.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.test_user = {"email": "test@demo.com", "password": "Test1234!"}
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.created_resources = {"bot_id": None, "strategy_id": None}

    def log_result(self, test_name, success, response_data=None, error=None):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name} - PASSED")
        else:
            self.failed_tests.append({"test": test_name, "error": error})
            print(f"❌ {test_name} - FAILED: {error}")
            if response_data:
                print(f"   Response: {response_data}")

    def make_request(self, method, endpoint, data=None, expect_status=200):
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}/api{endpoint}" if not endpoint.startswith('/api') else f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

            success = response.status_code == expect_status
            response_data = response.json() if response.content else {}
            
            return success, response_data, response.status_code, None
        except Exception as e:
            return False, {}, 0, str(e)

    def test_auth_login(self):
        """Test user login"""
        success, data, status, error = self.make_request(
            'POST', '/auth/login', self.test_user, 200
        )
        
        if success and 'token' in data:
            self.token = data['token']
            self.log_result("Auth Login", True)
            return True
        else:
            self.log_result("Auth Login", False, data, error or f"Status: {status}")
            return False

    def test_auth_signup(self):
        """Test user signup with random email"""
        signup_data = {
            "email": f"test_{int(time.time())}@demo.com",
            "password": "Test1234!",
            "name": "Test User"
        }
        
        success, data, status, error = self.make_request(
            'POST', '/auth/signup', signup_data, 200
        )
        
        self.log_result("Auth Signup", success, data, error or f"Status: {status}")
        return success

    def test_auth_me(self):
        """Test get current user"""
        success, data, status, error = self.make_request('GET', '/auth/me', expect_status=200)
        
        if success and 'email' in data:
            self.log_result("Auth Me", True)
            return True
        else:
            self.log_result("Auth Me", False, data, error or f"Status: {status}")
            return False

    def test_market_symbols(self):
        """Test get market symbols"""
        success, data, status, error = self.make_request('GET', '/market/symbols', expect_status=200)
        
        if success and 'symbols' in data and isinstance(data['symbols'], list):
            self.log_result("Market Symbols", True)
            return True
        else:
            self.log_result("Market Symbols", False, data, error or f"Status: {status}")
            return False

    def test_market_ohlcv(self):
        """Test get OHLCV data"""
        success, data, status, error = self.make_request(
            'GET', '/market/ohlcv?symbol=BTCUSD&timeframe=1h&limit=10', expect_status=200
        )
        
        if success and isinstance(data, list) and len(data) > 0:
            # Check if first item has required OHLCV fields
            first_candle = data[0]
            required_fields = ['open', 'high', 'low', 'close', 'volume', 'timestamp']
            has_all_fields = all(field in first_candle for field in required_fields)
            
            if has_all_fields:
                self.log_result("Market OHLCV", True)
                return True
            else:
                self.log_result("Market OHLCV", False, first_candle, "Missing OHLCV fields")
                return False
        else:
            self.log_result("Market OHLCV", False, data, error or f"Status: {status}")
            return False

    def test_market_latest_prices(self):
        """Test get latest prices"""
        success, data, status, error = self.make_request('GET', '/market/latest_prices', expect_status=200)
        
        if success and isinstance(data, dict) and len(data) > 0:
            # Check if prices have expected structure
            first_symbol = list(data.keys())[0]
            price_data = data[first_symbol]
            required_fields = ['price', 'change', 'change_pct']
            has_required = all(field in price_data for field in required_fields)
            
            if has_required:
                self.log_result("Market Latest Prices", True)
                return True
            else:
                self.log_result("Market Latest Prices", False, price_data, "Missing price fields")
                return False
        else:
            self.log_result("Market Latest Prices", False, data, error or f"Status: {status}")
            return False

    def test_create_strategy(self):
        """Test create strategy"""
        strategy_data = {
            "name": f"Test Strategy {int(time.time())}",
            "symbol": "BTCUSD",
            "timeframe": "1h",
            "entry": {
                "logic": "AND",
                "conditions": [
                    {"type": "RSI", "operator": "<", "value": 30}
                ]
            },
            "exit": {
                "logic": "OR", 
                "conditions": [
                    {"type": "RSI", "operator": ">", "value": 70}
                ]
            },
            "risk": {
                "stop_loss_pct": 2.0,
                "take_profit_pct": 5.0,
                "max_position_size_pct": 10.0
            }
        }
        
        success, data, status, error = self.make_request(
            'POST', '/strategies', strategy_data, 200
        )
        
        if success and 'id' in data:
            self.created_resources['strategy_id'] = data['id']
            self.log_result("Create Strategy", True)
            return True
        else:
            self.log_result("Create Strategy", False, data, error or f"Status: {status}")
            return False

    def test_list_strategies(self):
        """Test list strategies"""
        success, data, status, error = self.make_request('GET', '/strategies', expect_status=200)
        
        if success and isinstance(data, list):
            self.log_result("List Strategies", True)
            return True
        else:
            self.log_result("List Strategies", False, data, error or f"Status: {status}")
            return False

    def test_create_bot(self):
        """Test create bot"""
        bot_data = {
            "name": f"Test Bot {int(time.time())}",
            "symbol": "BTCUSD",
            "timeframe": "1h",
            "strategy_id": self.created_resources.get('strategy_id'),
            "risk_settings": {
                "stop_loss_pct": 2.0,
                "take_profit_pct": 5.0,
                "max_position_size_pct": 10.0
            }
        }
        
        success, data, status, error = self.make_request(
            'POST', '/bots', bot_data, 200
        )
        
        if success and 'id' in data:
            self.created_resources['bot_id'] = data['id']
            self.log_result("Create Bot", True)
            return True
        else:
            self.log_result("Create Bot", False, data, error or f"Status: {status}")
            return False

    def test_list_bots(self):
        """Test list bots"""
        success, data, status, error = self.make_request('GET', '/bots', expect_status=200)
        
        if success and isinstance(data, list):
            self.log_result("List Bots", True)
            return True
        else:
            self.log_result("List Bots", False, data, error or f"Status: {status}")
            return False

    def test_bot_operations(self):
        """Test bot start/stop/clone"""
        bot_id = self.created_resources.get('bot_id')
        if not bot_id:
            self.log_result("Bot Operations", False, None, "No bot ID available")
            return False

        # Test start bot
        success, data, status, error = self.make_request(
            'POST', f'/bots/{bot_id}/start', expect_status=200
        )
        
        if not success:
            self.log_result("Bot Start", False, data, error or f"Status: {status}")
            return False
        else:
            self.log_result("Bot Start", True)

        # Test stop bot
        success, data, status, error = self.make_request(
            'POST', f'/bots/{bot_id}/stop', expect_status=200
        )
        
        if not success:
            self.log_result("Bot Stop", False, data, error or f"Status: {status}")
            return False
        else:
            self.log_result("Bot Stop", True)

        # Test clone bot
        success, data, status, error = self.make_request(
            'POST', f'/bots/{bot_id}/clone', expect_status=200
        )
        
        if success and 'id' in data:
            self.log_result("Bot Clone", True)
            return True
        else:
            self.log_result("Bot Clone", False, data, error or f"Status: {status}")
            return False

    def test_backtest_run(self):
        """Test run backtest"""
        strategy_id = self.created_resources.get('strategy_id')
        backtest_data = {
            "strategy_id": strategy_id,
            "symbol": "BTCUSD",
            "timeframe": "1h",
            "initial_capital": 100000,
            "commission_pct": 0.1
        }
        
        success, data, status, error = self.make_request(
            'POST', '/backtest/run', backtest_data, 200
        )
        
        if success and 'metrics' in data and 'trades' in data and 'equity_curve' in data:
            self.log_result("Backtest Run", True)
            return True
        else:
            self.log_result("Backtest Run", False, data, error or f"Status: {status}")
            return False

    def test_paper_portfolio(self):
        """Test get paper trading portfolio"""
        success, data, status, error = self.make_request('GET', '/paper/portfolio', expect_status=200)
        
        if success and 'cash' in data and 'total_value' in data:
            self.log_result("Paper Portfolio", True)
            return True
        else:
            self.log_result("Paper Portfolio", False, data, error or f"Status: {status}")
            return False

    def test_paper_order(self):
        """Test place paper trading order"""
        order_data = {
            "symbol": "BTCUSD",
            "side": "buy",
            "quantity": 0.001,
            "order_type": "market"
        }
        
        success, data, status, error = self.make_request(
            'POST', '/paper/order', order_data, 200
        )
        
        if success and 'id' in data and data.get('status') == 'filled':
            self.log_result("Paper Order", True)
            return True
        else:
            self.log_result("Paper Order", False, data, error or f"Status: {status}")
            return False

    def test_paper_orders(self):
        """Test get paper trading orders"""
        success, data, status, error = self.make_request('GET', '/paper/orders', expect_status=200)
        
        if success and isinstance(data, list):
            self.log_result("Paper Orders", True)
            return True
        else:
            self.log_result("Paper Orders", False, data, error or f"Status: {status}")
            return False

    def test_paper_positions(self):
        """Test get paper trading positions"""
        success, data, status, error = self.make_request('GET', '/paper/positions', expect_status=200)
        
        if success and isinstance(data, list):
            self.log_result("Paper Positions", True)
            return True
        else:
            self.log_result("Paper Positions", False, data, error or f"Status: {status}")
            return False

    def test_sentiment_analyze(self):
        """Test sentiment analysis"""
        sentiment_data = {
            "headlines": [
                "Bitcoin surges to new all-time high as institutional adoption grows",
                "Market crash fears grow as inflation data disappoints",
                "Tech stocks rally on positive earnings reports"
            ]
        }
        
        success, data, status, error = self.make_request(
            'POST', '/sentiment/analyze', sentiment_data, 200
        )
        
        if success and 'results' in data and 'aggregate' in data:
            self.log_result("Sentiment Analysis", True)
            return True
        else:
            self.log_result("Sentiment Analysis", False, data, error or f"Status: {status}")
            return False

    def test_fundamentals(self):
        """Test get fundamentals"""
        for symbol in ['BTCUSD', 'AAPL']:
            success, data, status, error = self.make_request(
                'GET', f'/fundamentals/{symbol}', expect_status=200
            )
            
            if success and 'symbol' in data and 'fundamental_score' in data:
                self.log_result(f"Fundamentals {symbol}", True)
            else:
                self.log_result(f"Fundamentals {symbol}", False, data, error or f"Status: {status}")
                return False
        
        return True

    def test_indicators(self):
        """Test get indicators"""
        success, data, status, error = self.make_request(
            'GET', '/indicators/BTCUSD?timeframe=1h', expect_status=200
        )
        
        if success and 'indicators' in data and 'symbol' in data:
            indicators = data['indicators']
            required_indicators = ['sma_20', 'ema_50', 'rsi_14', 'macd_line', 'bb_upper']
            has_indicators = any(ind in indicators for ind in required_indicators)
            
            if has_indicators:
                self.log_result("Indicators", True)
                return True
            else:
                self.log_result("Indicators", False, indicators, "Missing expected indicators")
                return False
        else:
            self.log_result("Indicators", False, data, error or f"Status: {status}")
            return False

    def cleanup_resources(self):
        """Clean up created test resources"""
        print(f"\n🧹 Cleaning up test resources...")
        
        # Delete created bot
        if self.created_resources['bot_id']:
            success, _, _, _ = self.make_request(
                'DELETE', f"/bots/{self.created_resources['bot_id']}", expect_status=200
            )
            if success:
                print(f"✅ Deleted test bot")
            else:
                print(f"❌ Failed to delete test bot")

        # Delete created strategy  
        if self.created_resources['strategy_id']:
            success, _, _, _ = self.make_request(
                'DELETE', f"/strategies/{self.created_resources['strategy_id']}", expect_status=200
            )
            if success:
                print(f"✅ Deleted test strategy")
            else:
                print(f"❌ Failed to delete test strategy")

    def run_all_tests(self):
        """Run all API tests"""
        print(f"🚀 Starting AI Trading Bot API Tests")
        print(f"📡 Testing endpoint: {self.base_url}")
        print("=" * 50)

        # Authentication Tests
        if not self.test_auth_login():
            print("❌ Authentication failed - cannot proceed with other tests")
            return self.get_summary()

        self.test_auth_signup()
        self.test_auth_me()

        # Market Data Tests  
        self.test_market_symbols()
        self.test_market_ohlcv()
        self.test_market_latest_prices()

        # Strategy Tests
        self.test_create_strategy() 
        self.test_list_strategies()

        # Bot Tests
        self.test_create_bot()
        self.test_list_bots()
        self.test_bot_operations()

        # Backtesting Tests
        self.test_backtest_run()

        # Paper Trading Tests
        self.test_paper_portfolio()
        self.test_paper_order()
        self.test_paper_orders()
        self.test_paper_positions()

        # AI Services Tests
        self.test_sentiment_analyze()
        self.test_fundamentals()
        self.test_indicators()

        # Cleanup
        self.cleanup_resources()

        return self.get_summary()

    def get_summary(self):
        """Get test summary"""
        print("\n" + "=" * 50)
        print(f"📊 Test Results Summary")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {len(self.failed_tests)}")
        print(f"📈 Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ Failed Tests:")
            for failed in self.failed_tests:
                print(f"  • {failed['test']}: {failed['error']}")

        return {
            "passed": self.tests_passed,
            "failed": len(self.failed_tests),
            "total": self.tests_run,
            "success_rate": round(self.tests_passed/self.tests_run*100, 1) if self.tests_run > 0 else 0,
            "failed_tests": self.failed_tests
        }

def main():
    tester = TradingBotAPITester()
    summary = tester.run_all_tests()
    
    # Return appropriate exit code
    return 0 if summary["success_rate"] >= 90 else 1

if __name__ == "__main__":
    sys.exit(main())