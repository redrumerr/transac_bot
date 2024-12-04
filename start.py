from parser.parse_data import get_holders, get_current_price
import asyncio


token = '0x6b3595068778dd592e39a122f4f5a5cf09c90fe2'
url_ = 'https://etherscan.io/exportData?type=tokenholders&decimal=18'

if __name__ == "__main__":
    asyncio.run(get_holders('sushiswap'))
