from parser.parse_data import get_holders, get_current_price
import bot
import asyncio



url_ = 'https://etherscan.io/exportData?type=tokenholders&decimal=18'

if __name__ == "__main__":
    asyncio.run(get_holders('sushiswap'))
    asyncio.run(bot)