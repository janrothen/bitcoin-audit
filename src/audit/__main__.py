import argparse
from decimal import Decimal

from audit.audit_bot import AuditBot
from audit.clients.bitcoin_client import BitcoinClient
from audit.clients.x_client import XClient


class _MockBitcoinClient:
    def get_block_height(self):
        return 942022

    def get_total_amount(self):
        return Decimal("20006091.78041419")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true", help="Use mock Bitcoin client (no node required)")
    args = parser.parse_args()

    bitcoin_client = _MockBitcoinClient() if args.mock else BitcoinClient()
    bot = AuditBot(bitcoin_client, XClient())
    bot.run()
    print(bot.post)


if __name__ == "__main__":
    main()
