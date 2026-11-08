"""Test that all 8 Streamlit pages render cleanly without exceptions."""

import unittest
from streamlit.testing.v1 import AppTest


class TestStreamlitPages(unittest.TestCase):
    """Test all 8 navigation views in FINORA AI."""

    def test_pages_render(self):
        pages = [
            "Business Overview",
            "Transaction Management",
            "Historical Financial Analysis",
            "Cash Flow Forecast",
            "Cash Flow Risk Analysis",
            "Strategy Advisor",
            "Financial Reports",
            "AI Agent Centre"
        ]

        for p in pages:
            with self.subTest(page=p):
                at = AppTest.from_file("app.py", default_timeout=30)
                at.run()
                # Select page
                at.sidebar.radio[0].set_value(p)
                at.run()
                self.assertEqual(
                    len(at.exception),
                    0,
                    f"Page '{p}' raised exceptions: {[e.value for e in at.exception]}"
                )
                print(f"PASS: Page '{p}' rendered with 0 exceptions.")


if __name__ == "__main__":
    unittest.main()

