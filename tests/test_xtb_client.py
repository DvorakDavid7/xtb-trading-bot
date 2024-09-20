import os
import unittest

from dotenv import load_dotenv

from xtb_trading_bot.xtb_client import XtbClient


class XtbClientTest(unittest.TestCase):

    def setUp(self):
        load_dotenv()
        self.client_id = os.getenv("USER_ID")
        self.password = os.getenv("PASSWORD")
        self.url = "wss://ws.xtb.com/demo"
        self.stream_url = "wss://ws.xtb.com/demoStream"

    def test_login(self):
        client = XtbClient(self.client_id, self.password, self.url, self.stream_url)

        client.login()

        self.assertIsNotNone(client.conn)
        self.assertIsNotNone(client.stream_session_id)

    def test_login_invalid_credentials(self):
        client_1 = XtbClient("invalid", self.password, self.url, self.stream_url)
        client_2 = XtbClient(self.client_id, "invalid", self.url, self.stream_url)

        with self.assertRaises(ValueError):
            client_1.login()

        with self.assertRaises(ValueError):
            client_2.login()

    def test_streaming_connect(self):
        client = XtbClient(self.client_id, self.password, self.url, self.stream_url)

        client.login()
        client.streaming_connect()

        self.assertIsNotNone(client.stream_conn)
