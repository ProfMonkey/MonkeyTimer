import unittest

from countdown import CountdownTimer


class FakeClock:
    def __init__(self) -> None:
        self.value = 0.0

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


class CountdownTimerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.clock = FakeClock()
        self.timer = CountdownTimer(clock=self.clock)

    def test_counts_down_using_the_injected_monotonic_clock(self) -> None:
        self.timer.start(90)
        self.clock.advance(12.4)
        self.assertAlmostEqual(self.timer.remaining_seconds(), 77.6)

    def test_pause_and_resume_exclude_paused_time(self) -> None:
        self.timer.start(30)
        self.clock.advance(5)
        self.timer.pause()
        self.clock.advance(100)
        self.assertEqual(self.timer.remaining_seconds(), 25)
        self.timer.resume()
        self.clock.advance(4)
        self.assertEqual(self.timer.remaining_seconds(), 21)

    def test_automatically_stops_at_zero(self) -> None:
        self.timer.start(2)
        self.clock.advance(3)
        self.assertEqual(self.timer.remaining_seconds(), 0)
        self.assertFalse(self.timer.is_running)
        self.assertFalse(self.timer.is_paused)

    def test_reset_restores_configured_duration(self) -> None:
        self.timer.start(15)
        self.clock.advance(8)
        self.timer.reset()
        self.assertEqual(self.timer.remaining_seconds(), 15)
        self.assertFalse(self.timer.is_running)

    def test_non_positive_duration_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.timer.start(0)


if __name__ == "__main__":
    unittest.main()
