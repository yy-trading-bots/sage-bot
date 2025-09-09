import pytest
from bot.sage_bot import SageBot
import bot.sage_bot as sage_bot_module


class Snapshot:
    def __init__(self, price: float, ema_100: float) -> None:
        self.price = price
        self.ema_100 = ema_100


class FakeIndicatorManager:
    def __init__(self, snapshot: Snapshot) -> None:
        self._snapshot = snapshot

    def fetch_indicators(self) -> Snapshot:
        return self._snapshot


class FakeBinanceAdapter:
    def __init__(self, snapshot: Snapshot) -> None:
        self.indicator_manager = FakeIndicatorManager(snapshot)


class FakeState(sage_bot_module.PositionState):
    def __init__(self, parent: SageBot) -> None:
        super().__init__(parent=parent)

    # PositionState.step is final; implement only apply()
    def apply(self) -> None:
        # No-op here; we don't rely on this to break the loop anymore.
        return None


def test_run_exits_when_sleep_raises_and_sleep_called_once(monkeypatch):
    # Force the loop to exit deterministically by raising from sleep.
    calls = []

    class StopLoop(Exception):
        pass

    def fake_sleep(seconds: float) -> None:
        calls.append(seconds)
        raise StopLoop

    monkeypatch.setattr(sage_bot_module, "sleep", fake_sleep)
    monkeypatch.setattr(sage_bot_module, "FlatPositionState", FakeState)

    snapshot = Snapshot(price=100.0, ema_100=50.0)

    def adapter_factory(*_args, **_kwargs):
        return FakeBinanceAdapter(snapshot)

    monkeypatch.setattr(sage_bot_module, "BinanceAdapter", adapter_factory)

    bot = SageBot()

    with pytest.raises(StopLoop):
        bot.run()

    assert len(calls) == 1
    assert isinstance(calls[0], (int, float))
