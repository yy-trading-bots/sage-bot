from __future__ import annotations

from bot.states.position_state import PositionState
from utils.logger import Logger
from tensorflow_model.tf_model import TFModel


class FlatPositionState(PositionState):
    """
    State representing the absence of any active position.

    This state evaluates entry conditions for LONG or SHORT positions
    using the latest market snapshot and transitions to the
    appropriate active-position state when conditions are satisfied.
    """

    def apply(self) -> None:
        """
        Evaluate entry conditions and transition to a new position state if met.

        When a LONG or SHORT entry condition is satisfied, the method delegates
        to the respective handler to open a position and update the bot state.
        """
        model = TFModel()
        prediction = model.predict(self.parent.data_manager.market_snapshot)
        self._apply_long() if prediction == "LONG" else self._apply_short()

    def _update_position_snapshot(self) -> None:
        """
        Persist the current market snapshot as the position snapshot.

        This is used to record the market context at the moment the position
        is opened (price and technical indicators).
        """
        self.parent.data_manager.position_snapshot = (
            self.parent.data_manager.market_snapshot.clone()
        )

    def _apply_long(self) -> None:
        """
        Enter a LONG position and transition to the LongPositionState.

        Actions performed:
            - Blocks further LONG entries until the position is closed.
            - Saves a position snapshot.
            - Places TP/SL via the exchange adapter (in non-test mode).
            - Logs entry details.
        """
        self._update_position_snapshot()
        price: float = self.parent.data_manager.position_snapshot.price
        tp_price, sl_price = self.parent.binance_adapter.enter_long(price)

        Logger.log_info(
            "Entered LONG Current: "
            + str(round(price, 2))
            + " TP_PRICE: "
            + str(round(tp_price, 2))
            + " SL_PRICE: "
            + str(round(sl_price, 2))
        )
        Logger.log_info(str(self.parent.data_manager.position_snapshot))

        from bot.states.active.long_position_state import LongPositionState

        self.parent.state = LongPositionState(
            parent=self.parent, target_prices=[tp_price, sl_price]
        )

    def _apply_short(self) -> None:
        """
        Enter a SHORT position and transition to the ShortPositionState.

        Actions performed:
            - Blocks further SHORT entries until the position is closed.
            - Saves a position snapshot.
            - Places TP/SL via the exchange adapter (in non-test mode).
            - Logs entry details.
        """
        self._update_position_snapshot()

        price: float = self.parent.data_manager.position_snapshot.price
        tp_price, sl_price = self.parent.binance_adapter.enter_short(price)

        Logger.log_info(
            "Entered SHORT Current: "
            + str(round(price, 2))
            + " TP_PRICE: "
            + str(round(tp_price, 2))
            + " SL_PRICE: "
            + str(round(sl_price, 2))
        )
        Logger.log_info(str(self.parent.data_manager.position_snapshot))

        from bot.states.active.short_position_state import ShortPositionState

        self.parent.state = ShortPositionState(
            parent=self.parent, target_prices=[tp_price, sl_price]
        )
