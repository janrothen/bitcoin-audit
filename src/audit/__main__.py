import logging

from audit.audit_bot import AuditBot
from audit.clients.bitcoin_client import BitcoinClient
from audit.clients.x_client import XClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


def main():
    bot = AuditBot(BitcoinClient(), XClient())
    bot.run()


if __name__ == "__main__":
    main()
