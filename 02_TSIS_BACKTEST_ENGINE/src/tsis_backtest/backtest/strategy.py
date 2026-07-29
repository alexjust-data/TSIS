"""Fixed strategy used by BT-GATE-011.

The strategy is deliberately simple. It is a validation harness for the engine,
not an attempt to discover or evaluate edge.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from tsis_backtest.replay.contracts import ReplayBarEvent

from .contracts import (
    BUY_TO_COVER,
    ENGINE_VALIDATION_RUN,
    ENTRY_OPEN_LABEL,
    EXIT_CLOSE_LABEL,
    MARKET_PROXY,
    NOT_EDGE_EVIDENCE,
    OPEN_SHORT_CLOSE_COVER_V0_1,
    SELL_SHORT,
    BacktestOrderIntent,
    BacktestRunError,
    StrategyDecision,
    StrategySpec,
)


def default_open_short_close_strategy(symbols: tuple[str, ...], quantity_per_symbol: int = 100) -> StrategySpec:
    return StrategySpec(
        strategy_id=OPEN_SHORT_CLOSE_COVER_V0_1,
        strategy_spec_version="0.1",
        strategy_name="Preprogrammed short at first regular bar and cover using last regular bar proxy",
        universe_id="lt1b_universe_v0_1",
        symbols=tuple(symbols),
        quantity_per_symbol=quantity_per_symbol,
        run_purpose=ENGINE_VALIDATION_RUN,
        edge_evidence="NOT_AUTHORIZED",
        economic_realism="INCOMPLETE",
        strategy_optimization="NOT_AUTHORIZED",
        limitations=(
            "strategy is fixed and non-optimized",
            "open/close are strategy labels, not new MARKET_ON_OPEN or MARKET_ON_CLOSE order types",
            "run validates engine mechanics only",
            "not edge evidence",
            "not economically realistic for small-caps shorts",
        ),
    )


class OpenShortCloseCoverStrategy:
    """Builds deterministic pre-programmed decisions for a single-session run."""

    def __init__(self, spec: StrategySpec) -> None:
        self.spec = spec
        self._validate_spec()

    def decisions_for_symbol(
        self,
        ticker: str,
        entry_event: ReplayBarEvent,
        exit_event: ReplayBarEvent,
    ) -> tuple[StrategyDecision, StrategyDecision]:
        if ticker not in self.spec.symbols:
            raise BacktestRunError("STRATEGY_SYMBOL_NOT_IN_SPEC", ticker)
        if entry_event.ticker != ticker or exit_event.ticker != ticker:
            raise BacktestRunError("STRATEGY_EVENT_TICKER_MISMATCH", ticker)
        if entry_event.bar.ts_start >= exit_event.bar.ts_start:
            raise BacktestRunError("STRATEGY_ENTRY_EXIT_BAR_ORDER_INVALID", ticker)

        entry_decision_timestamp = entry_event.bar.ts_start - timedelta(microseconds=1)
        exit_decision_timestamp = exit_event.bar.ts_start - timedelta(microseconds=1)
        return (
            StrategyDecision(
                decision_id=f"decision-{self.spec.strategy_id}-{ticker}-entry-open",
                strategy_id=self.spec.strategy_id,
                strategy_spec_version=self.spec.strategy_spec_version,
                ticker=ticker,
                side=SELL_SHORT,
                quantity=self.spec.quantity_per_symbol,
                target_label=ENTRY_OPEN_LABEL,
                decision_timestamp=entry_decision_timestamp,
                information_cutoff=entry_decision_timestamp,
                reason="preprogrammed engine-validation entry before first regular bar",
            ),
            StrategyDecision(
                decision_id=f"decision-{self.spec.strategy_id}-{ticker}-exit-close",
                strategy_id=self.spec.strategy_id,
                strategy_spec_version=self.spec.strategy_spec_version,
                ticker=ticker,
                side=BUY_TO_COVER,
                quantity=self.spec.quantity_per_symbol,
                target_label=EXIT_CLOSE_LABEL,
                decision_timestamp=exit_decision_timestamp,
                information_cutoff=exit_decision_timestamp,
                reason="preprogrammed engine-validation exit before last regular bar",
            ),
        )

    def decision_for_target(self, ticker: str, target_label: str, source_bar_ts_start: datetime) -> StrategyDecision:
        if ticker not in self.spec.symbols:
            raise BacktestRunError("STRATEGY_SYMBOL_NOT_IN_SPEC", ticker)
        if target_label == ENTRY_OPEN_LABEL:
            side = SELL_SHORT
            suffix = "entry-open"
            reason = "preprogrammed engine-validation entry before first regular bar"
        elif target_label == EXIT_CLOSE_LABEL:
            side = BUY_TO_COVER
            suffix = "exit-close"
            reason = "preprogrammed engine-validation exit before final regular bar"
        else:
            raise BacktestRunError("STRATEGY_TARGET_LABEL_UNSUPPORTED", target_label)
        decision_timestamp = source_bar_ts_start - timedelta(microseconds=1)
        return StrategyDecision(
            decision_id=f"decision-{self.spec.strategy_id}-{ticker}-{suffix}",
            strategy_id=self.spec.strategy_id,
            strategy_spec_version=self.spec.strategy_spec_version,
            ticker=ticker,
            side=side,
            quantity=self.spec.quantity_per_symbol,
            target_label=target_label,
            decision_timestamp=decision_timestamp,
            information_cutoff=decision_timestamp,
            reason=reason,
        )

    def intent_from_decision(self, decision: StrategyDecision) -> BacktestOrderIntent:
        market_price_field = "open" if decision.target_label == ENTRY_OPEN_LABEL else "close"
        return BacktestOrderIntent(
            intent_id=f"intent-{decision.decision_id}",
            decision_id=decision.decision_id,
            ticker=decision.ticker,
            side=decision.side,
            quantity=decision.quantity,
            order_type=MARKET_PROXY,
            market_price_field=market_price_field,
            target_label=decision.target_label,
            created_at=decision.decision_timestamp,
            reason=decision.reason,
        )

    def _validate_spec(self) -> None:
        if self.spec.strategy_id != OPEN_SHORT_CLOSE_COVER_V0_1:
            raise BacktestRunError("STRATEGY_ID_UNSUPPORTED", self.spec.strategy_id)
        if self.spec.quantity_per_symbol <= 0:
            raise BacktestRunError("STRATEGY_QUANTITY_NOT_POSITIVE", str(self.spec.quantity_per_symbol))
        if not self.spec.symbols:
            raise BacktestRunError("STRATEGY_SYMBOLS_REQUIRED", "strategy requires at least one symbol")
        if len(set(self.spec.symbols)) != len(self.spec.symbols):
            raise BacktestRunError("STRATEGY_SYMBOLS_DUPLICATED", ",".join(self.spec.symbols))
        if self.spec.entry_side != SELL_SHORT or self.spec.exit_side != BUY_TO_COVER:
            raise BacktestRunError("STRATEGY_SIDE_UNSUPPORTED", "BT-GATE-011 supports short then cover only")
        if self.spec.entry_order_type != MARKET_PROXY or self.spec.exit_order_type != MARKET_PROXY:
            raise BacktestRunError("STRATEGY_ORDER_TYPE_UNSUPPORTED", "BT-GATE-011 supports MARKET_PROXY only")
        if self.spec.edge_evidence != NOT_EDGE_EVIDENCE and self.spec.edge_evidence != "NOT_AUTHORIZED":
            raise BacktestRunError("STRATEGY_EDGE_EVIDENCE_UNAUTHORIZED", self.spec.edge_evidence)
