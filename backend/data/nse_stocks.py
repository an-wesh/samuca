"""
NSE Stocks Database
Comprehensive list of NSE-listed stocks including NIFTY 50, NIFTY Next 50, sectoral indices
"""

# NIFTY 50 Stocks (Top 50 by market cap)
NIFTY_50 = [
    {"symbol": "RELIANCE.NS", "name": "Reliance Industries", "sector": "Energy"},
    {"symbol": "TCS.NS", "name": "Tata Consultancy Services", "sector": "IT"},
    {"symbol": "HDFCBANK.NS", "name": "HDFC Bank", "sector": "Banking"},
    {"symbol": "INFY.NS", "name": "Infosys", "sector": "IT"},
    {"symbol": "ICICIBANK.NS", "name": "ICICI Bank", "sector": "Banking"},
    {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever", "sector": "FMCG"},
    {"symbol": "SBIN.NS", "name": "State Bank of India", "sector": "Banking"},
    {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel", "sector": "Telecom"},
    {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank", "sector": "Banking"},
    {"symbol": "ITC.NS", "name": "ITC Limited", "sector": "FMCG"},
    {"symbol": "LT.NS", "name": "Larsen & Toubro", "sector": "Infrastructure"},
    {"symbol": "AXISBANK.NS", "name": "Axis Bank", "sector": "Banking"},
    {"symbol": "ASIANPAINT.NS", "name": "Asian Paints", "sector": "Consumer"},
    {"symbol": "MARUTI.NS", "name": "Maruti Suzuki", "sector": "Automobile"},
    {"symbol": "SUNPHARMA.NS", "name": "Sun Pharma", "sector": "Pharma"},
    {"symbol": "TITAN.NS", "name": "Titan Company", "sector": "Consumer"},
    {"symbol": "BAJFINANCE.NS", "name": "Bajaj Finance", "sector": "Finance"},
    {"symbol": "DMART.NS", "name": "Avenue Supermarts", "sector": "Retail"},
    {"symbol": "WIPRO.NS", "name": "Wipro", "sector": "IT"},
    {"symbol": "HCLTECH.NS", "name": "HCL Technologies", "sector": "IT"},
    {"symbol": "ULTRACEMCO.NS", "name": "UltraTech Cement", "sector": "Cement"},
    {"symbol": "NESTLEIND.NS", "name": "Nestle India", "sector": "FMCG"},
    {"symbol": "POWERGRID.NS", "name": "Power Grid Corp", "sector": "Power"},
    {"symbol": "NTPC.NS", "name": "NTPC Limited", "sector": "Power"},
    {"symbol": "TATAMOTORS.NS", "name": "Tata Motors", "sector": "Automobile"},
    {"symbol": "M&M.NS", "name": "Mahindra & Mahindra", "sector": "Automobile"},
    {"symbol": "TATASTEEL.NS", "name": "Tata Steel", "sector": "Metal"},
    {"symbol": "JSWSTEEL.NS", "name": "JSW Steel", "sector": "Metal"},
    {"symbol": "ADANIENT.NS", "name": "Adani Enterprises", "sector": "Diversified"},
    {"symbol": "ADANIPORTS.NS", "name": "Adani Ports", "sector": "Infrastructure"},
    {"symbol": "BAJAJFINSV.NS", "name": "Bajaj Finserv", "sector": "Finance"},
    {"symbol": "COALINDIA.NS", "name": "Coal India", "sector": "Mining"},
    {"symbol": "ONGC.NS", "name": "ONGC", "sector": "Energy"},
    {"symbol": "GRASIM.NS", "name": "Grasim Industries", "sector": "Cement"},
    {"symbol": "TECHM.NS", "name": "Tech Mahindra", "sector": "IT"},
    {"symbol": "INDUSINDBK.NS", "name": "IndusInd Bank", "sector": "Banking"},
    {"symbol": "HINDALCO.NS", "name": "Hindalco", "sector": "Metal"},
    {"symbol": "DRREDDY.NS", "name": "Dr. Reddy's Labs", "sector": "Pharma"},
    {"symbol": "CIPLA.NS", "name": "Cipla", "sector": "Pharma"},
    {"symbol": "APOLLOHOSP.NS", "name": "Apollo Hospitals", "sector": "Healthcare"},
    {"symbol": "EICHERMOT.NS", "name": "Eicher Motors", "sector": "Automobile"},
    {"symbol": "DIVISLAB.NS", "name": "Divi's Laboratories", "sector": "Pharma"},
    {"symbol": "BPCL.NS", "name": "BPCL", "sector": "Energy"},
    {"symbol": "BRITANNIA.NS", "name": "Britannia Industries", "sector": "FMCG"},
    {"symbol": "SBILIFE.NS", "name": "SBI Life Insurance", "sector": "Insurance"},
    {"symbol": "HDFCLIFE.NS", "name": "HDFC Life Insurance", "sector": "Insurance"},
    {"symbol": "HEROMOTOCO.NS", "name": "Hero MotoCorp", "sector": "Automobile"},
    {"symbol": "BAJAJ-AUTO.NS", "name": "Bajaj Auto", "sector": "Automobile"},
    {"symbol": "TATACONSUM.NS", "name": "Tata Consumer", "sector": "FMCG"},
    {"symbol": "LTIM.NS", "name": "LTIMindtree", "sector": "IT"},
]

# NIFTY Next 50 Stocks
NIFTY_NEXT_50 = [
    {"symbol": "ADANIGREEN.NS", "name": "Adani Green Energy", "sector": "Power"},
    {"symbol": "AMBUJACEM.NS", "name": "Ambuja Cements", "sector": "Cement"},
    {"symbol": "AUROPHARMA.NS", "name": "Aurobindo Pharma", "sector": "Pharma"},
    {"symbol": "BANKBARODA.NS", "name": "Bank of Baroda", "sector": "Banking"},
    {"symbol": "BERGEPAINT.NS", "name": "Berger Paints", "sector": "Consumer"},
    {"symbol": "BOSCHLTD.NS", "name": "Bosch", "sector": "Automobile"},
    {"symbol": "CHOLAFIN.NS", "name": "Cholamandalam Finance", "sector": "Finance"},
    {"symbol": "COLPAL.NS", "name": "Colgate-Palmolive", "sector": "FMCG"},
    {"symbol": "DLF.NS", "name": "DLF Limited", "sector": "Real Estate"},
    {"symbol": "GAIL.NS", "name": "GAIL India", "sector": "Energy"},
    {"symbol": "GODREJCP.NS", "name": "Godrej Consumer", "sector": "FMCG"},
    {"symbol": "HAVELLS.NS", "name": "Havells India", "sector": "Consumer"},
    {"symbol": "ICICIPRULI.NS", "name": "ICICI Pru Life", "sector": "Insurance"},
    {"symbol": "ICICIGI.NS", "name": "ICICI Lombard", "sector": "Insurance"},
    {"symbol": "INDIGO.NS", "name": "InterGlobe Aviation", "sector": "Aviation"},
    {"symbol": "IOC.NS", "name": "Indian Oil Corp", "sector": "Energy"},
    {"symbol": "JINDALSTEL.NS", "name": "Jindal Steel", "sector": "Metal"},
    {"symbol": "LUPIN.NS", "name": "Lupin", "sector": "Pharma"},
    {"symbol": "MARICO.NS", "name": "Marico", "sector": "FMCG"},
    {"symbol": "MCDOWELL-N.NS", "name": "United Spirits", "sector": "FMCG"},
    {"symbol": "MOTHERSON.NS", "name": "Motherson Sumi", "sector": "Automobile"},
    {"symbol": "NAUKRI.NS", "name": "Info Edge", "sector": "IT"},
    {"symbol": "PAGEIND.NS", "name": "Page Industries", "sector": "Textile"},
    {"symbol": "PEL.NS", "name": "Piramal Enterprises", "sector": "Diversified"},
    {"symbol": "PETRONET.NS", "name": "Petronet LNG", "sector": "Energy"},
    {"symbol": "PIDILITIND.NS", "name": "Pidilite Industries", "sector": "Chemicals"},
    {"symbol": "PNB.NS", "name": "Punjab National Bank", "sector": "Banking"},
    {"symbol": "SAIL.NS", "name": "SAIL", "sector": "Metal"},
    {"symbol": "SHREECEM.NS", "name": "Shree Cement", "sector": "Cement"},
    {"symbol": "SIEMENS.NS", "name": "Siemens India", "sector": "Engineering"},
    {"symbol": "SRF.NS", "name": "SRF Limited", "sector": "Chemicals"},
    {"symbol": "TATAPOWER.NS", "name": "Tata Power", "sector": "Power"},
    {"symbol": "TORNTPHARM.NS", "name": "Torrent Pharma", "sector": "Pharma"},
    {"symbol": "TRENT.NS", "name": "Trent Limited", "sector": "Retail"},
    {"symbol": "UPL.NS", "name": "UPL Limited", "sector": "Chemicals"},
    {"symbol": "VEDL.NS", "name": "Vedanta", "sector": "Metal"},
    {"symbol": "ZOMATO.NS", "name": "Zomato", "sector": "Internet"},
    {"symbol": "ZYDUSLIFE.NS", "name": "Zydus Lifesciences", "sector": "Pharma"},
    {"symbol": "MUTHOOTFIN.NS", "name": "Muthoot Finance", "sector": "Finance"},
    {"symbol": "NMDC.NS", "name": "NMDC", "sector": "Mining"},
]

# Additional Popular NSE Stocks (Mid-caps & Small-caps)
POPULAR_NSE = [
    {"symbol": "YESBANK.NS", "name": "Yes Bank", "sector": "Banking"},
    {"symbol": "IDEA.NS", "name": "Vodafone Idea", "sector": "Telecom"},
    {"symbol": "PFC.NS", "name": "Power Finance Corp", "sector": "Finance"},
    {"symbol": "RECLTD.NS", "name": "REC Limited", "sector": "Finance"},
    {"symbol": "IRCTC.NS", "name": "IRCTC", "sector": "Travel"},
    {"symbol": "IRFC.NS", "name": "Indian Railway Finance", "sector": "Finance"},
    {"symbol": "HAL.NS", "name": "Hindustan Aeronautics", "sector": "Defence"},
    {"symbol": "BEL.NS", "name": "Bharat Electronics", "sector": "Defence"},
    {"symbol": "BHEL.NS", "name": "BHEL", "sector": "Engineering"},
    {"symbol": "NBCC.NS", "name": "NBCC India", "sector": "Infrastructure"},
    {"symbol": "NHPC.NS", "name": "NHPC", "sector": "Power"},
    {"symbol": "SJVN.NS", "name": "SJVN", "sector": "Power"},
    {"symbol": "SUZLON.NS", "name": "Suzlon Energy", "sector": "Power"},
    {"symbol": "TATAELXSI.NS", "name": "Tata Elxsi", "sector": "IT"},
    {"symbol": "PERSISTENT.NS", "name": "Persistent Systems", "sector": "IT"},
    {"symbol": "COFORGE.NS", "name": "Coforge", "sector": "IT"},
    {"symbol": "MPHASIS.NS", "name": "Mphasis", "sector": "IT"},
    {"symbol": "LAURUSLABS.NS", "name": "Laurus Labs", "sector": "Pharma"},
    {"symbol": "ALKEM.NS", "name": "Alkem Labs", "sector": "Pharma"},
    {"symbol": "BIOCON.NS", "name": "Biocon", "sector": "Pharma"},
    {"symbol": "IPCALAB.NS", "name": "IPCA Laboratories", "sector": "Pharma"},
    {"symbol": "ABBOTINDIA.NS", "name": "Abbott India", "sector": "Pharma"},
    {"symbol": "MAXHEALTH.NS", "name": "Max Healthcare", "sector": "Healthcare"},
    {"symbol": "FORTIS.NS", "name": "Fortis Healthcare", "sector": "Healthcare"},
    {"symbol": "METROPOLIS.NS", "name": "Metropolis Healthcare", "sector": "Healthcare"},
    {"symbol": "LALPATHLAB.NS", "name": "Dr. Lal PathLabs", "sector": "Healthcare"},
    {"symbol": "POLYCAB.NS", "name": "Polycab India", "sector": "Consumer"},
    {"symbol": "VOLTAS.NS", "name": "Voltas", "sector": "Consumer"},
    {"symbol": "WHIRLPOOL.NS", "name": "Whirlpool India", "sector": "Consumer"},
    {"symbol": "CROMPTON.NS", "name": "Crompton Greaves", "sector": "Consumer"},
    {"symbol": "DIXON.NS", "name": "Dixon Technologies", "sector": "Electronics"},
    {"symbol": "KAYNES.NS", "name": "Kaynes Technology", "sector": "Electronics"},
    {"symbol": "ASTRAL.NS", "name": "Astral Limited", "sector": "Building"},
    {"symbol": "SUPREMEIND.NS", "name": "Supreme Industries", "sector": "Building"},
    {"symbol": "APLAPOLLO.NS", "name": "APL Apollo Tubes", "sector": "Metal"},
    {"symbol": "RATNAMANI.NS", "name": "Ratnamani Metals", "sector": "Metal"},
    {"symbol": "DEEPAKFERT.NS", "name": "Deepak Fertilisers", "sector": "Chemicals"},
    {"symbol": "DEEPAKNTR.NS", "name": "Deepak Nitrite", "sector": "Chemicals"},
    {"symbol": "AARTIIND.NS", "name": "Aarti Industries", "sector": "Chemicals"},
    {"symbol": "CLEAN.NS", "name": "Clean Science", "sector": "Chemicals"},
    {"symbol": "NAVINFLUOR.NS", "name": "Navin Fluorine", "sector": "Chemicals"},
    {"symbol": "FLUOROCHEM.NS", "name": "Gujarat Fluorochemicals", "sector": "Chemicals"},
    {"symbol": "JUBLFOOD.NS", "name": "Jubilant FoodWorks", "sector": "Food"},
    {"symbol": "VBL.NS", "name": "Varun Beverages", "sector": "FMCG"},
    {"symbol": "RADICO.NS", "name": "Radico Khaitan", "sector": "FMCG"},
    {"symbol": "DABUR.NS", "name": "Dabur India", "sector": "FMCG"},
    {"symbol": "EMAMILTD.NS", "name": "Emami", "sector": "FMCG"},
    {"symbol": "TATACOMM.NS", "name": "Tata Communications", "sector": "Telecom"},
    {"symbol": "ROUTE.NS", "name": "Route Mobile", "sector": "IT"},
    {"symbol": "HAPPSTMNDS.NS", "name": "Happiest Minds", "sector": "IT"},
    {"symbol": "LTTS.NS", "name": "L&T Technology Services", "sector": "IT"},
    {"symbol": "CYIENT.NS", "name": "Cyient", "sector": "IT"},
    {"symbol": "BIRLASOFT.NS", "name": "Birlasoft", "sector": "IT"},
    {"symbol": "CAMS.NS", "name": "CAMS", "sector": "Finance"},
    {"symbol": "CDSL.NS", "name": "CDSL", "sector": "Finance"},
    {"symbol": "MCX.NS", "name": "MCX", "sector": "Finance"},
    {"symbol": "BSE.NS", "name": "BSE Limited", "sector": "Finance"},
    {"symbol": "ANGELONE.NS", "name": "Angel One", "sector": "Finance"},
    {"symbol": "IIFL.NS", "name": "IIFL Finance", "sector": "Finance"},
    {"symbol": "MANAPPURAM.NS", "name": "Manappuram Finance", "sector": "Finance"},
    {"symbol": "L&TFH.NS", "name": "L&T Finance Holdings", "sector": "Finance"},
    {"symbol": "LICHSGFIN.NS", "name": "LIC Housing Finance", "sector": "Finance"},
    {"symbol": "CANFINHOME.NS", "name": "Can Fin Homes", "sector": "Finance"},
    {"symbol": "AAVAS.NS", "name": "Aavas Financiers", "sector": "Finance"},
    {"symbol": "HOMEFIRST.NS", "name": "Home First Finance", "sector": "Finance"},
    {"symbol": "OBEROIRLTY.NS", "name": "Oberoi Realty", "sector": "Real Estate"},
    {"symbol": "GODREJPROP.NS", "name": "Godrej Properties", "sector": "Real Estate"},
    {"symbol": "PRESTIGE.NS", "name": "Prestige Estates", "sector": "Real Estate"},
    {"symbol": "BRIGADE.NS", "name": "Brigade Enterprises", "sector": "Real Estate"},
    {"symbol": "SOBHA.NS", "name": "Sobha Limited", "sector": "Real Estate"},
    {"symbol": "PHOENIXLTD.NS", "name": "Phoenix Mills", "sector": "Real Estate"},
    {"symbol": "ESCORTS.NS", "name": "Escorts Kubota", "sector": "Automobile"},
    {"symbol": "ASHOKLEY.NS", "name": "Ashok Leyland", "sector": "Automobile"},
    {"symbol": "TVSMOTOR.NS", "name": "TVS Motor", "sector": "Automobile"},
    {"symbol": "BALKRISIND.NS", "name": "Balkrishna Industries", "sector": "Automobile"},
    {"symbol": "MRF.NS", "name": "MRF", "sector": "Automobile"},
    {"symbol": "APOLLOTYRE.NS", "name": "Apollo Tyres", "sector": "Automobile"},
    {"symbol": "CEATLTD.NS", "name": "CEAT", "sector": "Automobile"},
    {"symbol": "EXIDEIND.NS", "name": "Exide Industries", "sector": "Automobile"},
    {"symbol": "AMARAJABAT.NS", "name": "Amara Raja Batteries", "sector": "Automobile"},
    {"symbol": "SCHAEFFLER.NS", "name": "Schaeffler India", "sector": "Automobile"},
    {"symbol": "SKFINDIA.NS", "name": "SKF India", "sector": "Engineering"},
    {"symbol": "TIMKEN.NS", "name": "Timken India", "sector": "Engineering"},
    {"symbol": "CUMMINSIND.NS", "name": "Cummins India", "sector": "Engineering"},
    {"symbol": "GRINDWELL.NS", "name": "Grindwell Norton", "sector": "Engineering"},
    {"symbol": "THERMAX.NS", "name": "Thermax", "sector": "Engineering"},
    {"symbol": "HONAUT.NS", "name": "Honeywell Automation", "sector": "Engineering"},
    {"symbol": "ABB.NS", "name": "ABB India", "sector": "Engineering"},
    {"symbol": "CGPOWER.NS", "name": "CG Power", "sector": "Engineering"},
    {"symbol": "KALYANKJIL.NS", "name": "Kalyan Jewellers", "sector": "Retail"},
    {"symbol": "SHOPERSTOP.NS", "name": "Shoppers Stop", "sector": "Retail"},
    {"symbol": "DEVYANI.NS", "name": "Devyani International", "sector": "Food"},
    {"symbol": "SAPPHIRE.NS", "name": "Sapphire Foods", "sector": "Food"},
    {"symbol": "WESTLIFE.NS", "name": "Westlife Foodworld", "sector": "Food"},
    {"symbol": "DELHIVERY.NS", "name": "Delhivery", "sector": "Logistics"},
    {"symbol": "BLUEDART.NS", "name": "Blue Dart Express", "sector": "Logistics"},
    {"symbol": "CONCOR.NS", "name": "Container Corp", "sector": "Logistics"},
    {"symbol": "GMRAIRPORT.NS", "name": "GMR Airports", "sector": "Infrastructure"},
    {"symbol": "IRB.NS", "name": "IRB Infrastructure", "sector": "Infrastructure"},
    {"symbol": "KEC.NS", "name": "KEC International", "sector": "Infrastructure"},
    {"symbol": "PNCINFRA.NS", "name": "PNC Infratech", "sector": "Infrastructure"},
    {"symbol": "NLCINDIA.NS", "name": "NLC India", "sector": "Power"},
    {"symbol": "TORNTPOWER.NS", "name": "Torrent Power", "sector": "Power"},
    {"symbol": "CESC.NS", "name": "CESC", "sector": "Power"},
    {"symbol": "ADANIPOWER.NS", "name": "Adani Power", "sector": "Power"},
    {"symbol": "JSWENERGY.NS", "name": "JSW Energy", "sector": "Power"},
    {"symbol": "NYKAA.NS", "name": "FSN E-Commerce", "sector": "Internet"},
    {"symbol": "PAYTM.NS", "name": "One 97 Communications", "sector": "Internet"},
    {"symbol": "POLICYBZR.NS", "name": "PB Fintech", "sector": "Internet"},
    {"symbol": "CARTRADE.NS", "name": "CarTrade Tech", "sector": "Internet"},
    {"symbol": "STARHEALTH.NS", "name": "Star Health Insurance", "sector": "Insurance"},
    {"symbol": "NIACL.NS", "name": "New India Assurance", "sector": "Insurance"},
    {"symbol": "GICRE.NS", "name": "General Insurance Corp", "sector": "Insurance"},
]

# Indices (for reference/tracking)
INDICES = [
    {"symbol": "^NSEI", "name": "NIFTY 50", "sector": "Index"},
    {"symbol": "^NSEBANK", "name": "NIFTY Bank", "sector": "Index"},
    {"symbol": "^CNXIT", "name": "NIFTY IT", "sector": "Index"},
    {"symbol": "^CNXPHARMA", "name": "NIFTY Pharma", "sector": "Index"},
    {"symbol": "^CNXAUTO", "name": "NIFTY Auto", "sector": "Index"},
    {"symbol": "^CNXFMCG", "name": "NIFTY FMCG", "sector": "Index"},
    {"symbol": "^CNXMETAL", "name": "NIFTY Metal", "sector": "Index"},
    {"symbol": "^CNXREALTY", "name": "NIFTY Realty", "sector": "Index"},
    {"symbol": "^CNXENERGY", "name": "NIFTY Energy", "sector": "Index"},
    {"symbol": "^CNXINFRA", "name": "NIFTY Infrastructure", "sector": "Index"},
]

# Combine all stocks
ALL_NSE_STOCKS = NIFTY_50 + NIFTY_NEXT_50 + POPULAR_NSE

# Create lookup dictionaries
STOCK_BY_SYMBOL = {s["symbol"]: s for s in ALL_NSE_STOCKS}
STOCK_BY_SECTOR = {}
for stock in ALL_NSE_STOCKS:
    sector = stock["sector"]
    if sector not in STOCK_BY_SECTOR:
        STOCK_BY_SECTOR[sector] = []
    STOCK_BY_SECTOR[sector].append(stock)

# Keep crypto for international markets
CRYPTO_SYMBOLS = [
    {"symbol": "BTCUSD", "name": "Bitcoin USD", "sector": "Crypto"},
    {"symbol": "ETHUSD", "name": "Ethereum USD", "sector": "Crypto"},
]

# US stocks for reference
US_STOCKS = [
    {"symbol": "AAPL", "name": "Apple Inc", "sector": "Technology"},
    {"symbol": "TSLA", "name": "Tesla Inc", "sector": "Automobile"},
    {"symbol": "SPY", "name": "S&P 500 ETF", "sector": "ETF"},
    {"symbol": "GOOGL", "name": "Alphabet Inc", "sector": "Technology"},
    {"symbol": "MSFT", "name": "Microsoft Corp", "sector": "Technology"},
    {"symbol": "AMZN", "name": "Amazon.com Inc", "sector": "Technology"},
    {"symbol": "NVDA", "name": "NVIDIA Corp", "sector": "Technology"},
    {"symbol": "META", "name": "Meta Platforms", "sector": "Technology"},
]

def get_all_symbols():
    """Get all tradeable symbols"""
    symbols = []
    for stock in ALL_NSE_STOCKS:
        symbols.append({
            "symbol": stock["symbol"],
            "display_symbol": stock["symbol"].replace(".NS", ""),
            "name": stock["name"],
            "sector": stock["sector"],
            "exchange": "NSE"
        })
    for stock in US_STOCKS:
        symbols.append({
            "symbol": stock["symbol"],
            "display_symbol": stock["symbol"],
            "name": stock["name"],
            "sector": stock["sector"],
            "exchange": "US"
        })
    for stock in CRYPTO_SYMBOLS:
        symbols.append({
            "symbol": stock["symbol"],
            "display_symbol": stock["symbol"],
            "name": stock["name"],
            "sector": stock["sector"],
            "exchange": "Crypto"
        })
    return symbols

def get_sectors():
    """Get all unique sectors"""
    sectors = set()
    for stock in ALL_NSE_STOCKS:
        sectors.add(stock["sector"])
    return sorted(list(sectors))
