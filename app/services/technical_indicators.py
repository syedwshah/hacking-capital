"""
Technical Indicators Module

Comprehensive collection of technical analysis indicators for trading decisions.
All indicators follow standard financial calculations and are optimized for performance.
"""

from __future__ import annotations
import math
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import numpy as np


@dataclass
class IndicatorResult:
    """Standardized result structure for technical indicators."""
    name: str
    value: float
    signal: str  # "BUY", "SELL", "HOLD", "NEUTRAL"
    strength: float  # 0.0 to 1.0
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class TechnicalIndicators:
    """Collection of technical analysis indicators."""

    @staticmethod
    def simple_moving_average(prices: List[float], period: int) -> List[float]:
        """Calculate Simple Moving Average."""
        if len(prices) < period:
            return []
        return [sum(prices[i:i+period]) / period for i in range(len(prices) - period + 1)]

    @staticmethod
    def exponential_moving_average(prices: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average."""
        if len(prices) < period:
            return []

        ema = [sum(prices[:period]) / period]  # First EMA is SMA
        multiplier = 2 / (period + 1)

        for price in prices[period:]:
            ema.append((price * multiplier) + (ema[-1] * (1 - multiplier)))

        return ema

    @staticmethod
    def weighted_moving_average(prices: List[float], period: int) -> List[float]:
        """Calculate Weighted Moving Average."""
        if len(prices) < period:
            return []

        weights = list(range(1, period + 1))
        weight_sum = sum(weights)

        wma = []
        for i in range(len(prices) - period + 1):
            window = prices[i:i+period]
            weighted_sum = sum(w * p for w, p in zip(weights, window))
            wma.append(weighted_sum / weight_sum)

        return wma

    @staticmethod
    def macd(prices: List[float], fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Tuple[List[float], List[float], List[float]]:
        """Calculate MACD (Moving Average Convergence Divergence)."""
        fast_ema = TechnicalIndicators.exponential_moving_average(prices, fast_period)
        slow_ema = TechnicalIndicators.exponential_moving_average(prices, slow_period)

        if len(fast_ema) < len(slow_ema):
            slow_ema = slow_ema[-len(fast_ema):]
        elif len(slow_ema) < len(fast_ema):
            fast_ema = fast_ema[-len(slow_ema):]

        macd_line = [f - s for f, s in zip(fast_ema, slow_ema)]
        signal_line = TechnicalIndicators.exponential_moving_average(macd_line, signal_period)
        histogram = [m - s for m, s in zip(macd_line[-len(signal_line):], signal_line)]

        return macd_line, signal_line, histogram

    @staticmethod
    def rsi(prices: List[float], period: int = 14) -> List[float]:
        """Calculate Relative Strength Index."""
        if len(prices) < period + 1:
            return []

        rsi_values = []
        for i in range(period, len(prices)):
            window = prices[i-period:i+1]
            gains = []
            losses = []

            for j in range(1, len(window)):
                change = window[j] - window[j-1]
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(change))

            avg_gain = sum(gains) / period if gains else 0
            avg_loss = sum(losses) / period if losses else 0

            if avg_loss == 0:
                rsi = 100.0
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))

            rsi_values.append(rsi)

        return rsi_values

    @staticmethod
    def bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2.0) -> Tuple[List[float], List[float], List[float]]:
        """Calculate Bollinger Bands."""
        if len(prices) < period:
            return [], [], []

        sma = TechnicalIndicators.simple_moving_average(prices, period)
        upper_band = []
        lower_band = []

        for i, ma in enumerate(sma):
            window = prices[i:i+period]
            std = np.std(window)
            upper_band.append(ma + (std_dev * std))
            lower_band.append(ma - (std_dev * std))

        return sma, upper_band, lower_band

    @staticmethod
    def stochastic_oscillator(highs: List[float], lows: List[float], closes: List[float], k_period: int = 14, d_period: int = 3) -> Tuple[List[float], List[float]]:
        """Calculate Stochastic Oscillator."""
        if len(closes) < k_period:
            return [], []

        k_values = []
        for i in range(k_period - 1, len(closes)):
            high_window = highs[i-k_period+1:i+1]
            low_window = lows[i-k_period+1:i+1]

            highest_high = max(high_window)
            lowest_low = min(low_window)
            current_close = closes[i]

            if highest_high == lowest_low:
                k = 50.0  # Neutral when no range
            else:
                k = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100

            k_values.append(k)

        # Calculate %D (SMA of %K)
        d_values = TechnicalIndicators.simple_moving_average(k_values, d_period)

        return k_values, d_values

    @staticmethod
    def commodity_channel_index(highs: List[float], lows: List[float], closes: List[float], period: int = 20) -> List[float]:
        """Calculate Commodity Channel Index (CCI)."""
        if len(closes) < period:
            return []

        cci_values = []
        for i in range(period - 1, len(closes)):
            high_window = highs[i-period+1:i+1]
            low_window = lows[i-period+1:i+1]
            close_window = closes[i-period+1:i+1]

            # Calculate Typical Price
            typical_prices = [(h + l + c) / 3 for h, l, c in zip(high_window, low_window, close_window)]
            sma_tp = sum(typical_prices) / period

            # Calculate Mean Deviation
            mean_deviation = sum(abs(tp - sma_tp) for tp in typical_prices) / period

            if mean_deviation == 0:
                cci = 0.0
            else:
                cci = (typical_prices[-1] - sma_tp) / (0.015 * mean_deviation)

            cci_values.append(cci)

        return cci_values

    @staticmethod
    def average_true_range(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> List[float]:
        """Calculate Average True Range (ATR)."""
        if len(closes) < period + 1:
            return []

        true_ranges = []
        for i in range(1, len(closes)):
            tr1 = highs[i] - lows[i]
            tr2 = abs(highs[i] - closes[i-1])
            tr3 = abs(lows[i] - closes[i-1])
            true_range = max(tr1, tr2, tr3)
            true_ranges.append(true_range)

        # First ATR is simple average
        atr = [sum(true_ranges[:period]) / period]

        # Subsequent ATRs use smoothing
        multiplier = 1 / period
        for tr in true_ranges[period:]:
            atr.append((atr[-1] * (period - 1) + tr) * multiplier)

        return atr

    @staticmethod
    def williams_percent_r(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> List[float]:
        """Calculate Williams %R."""
        if len(closes) < period:
            return []

        williams_r = []
        for i in range(period - 1, len(closes)):
            high_window = highs[i-period+1:i+1]
            low_window = lows[i-period+1:i+1]

            highest_high = max(high_window)
            lowest_low = min(low_window)
            current_close = closes[i]

            if highest_high == lowest_low:
                r = -50.0  # Neutral
            else:
                r = ((highest_high - current_close) / (highest_high - lowest_low)) * -100

            williams_r.append(r)

        return williams_r

    @staticmethod
    def on_balance_volume(closes: List[float], volumes: List[float]) -> List[float]:
        """Calculate On Balance Volume (OBV)."""
        if len(closes) != len(volumes) or len(closes) < 2:
            return []

        obv = [volumes[0]]  # Start with first volume

        for i in range(1, len(closes)):
            if closes[i] > closes[i-1]:
                obv.append(obv[-1] + volumes[i])
            elif closes[i] < closes[i-1]:
                obv.append(obv[-1] - volumes[i])
            else:
                obv.append(obv[-1])  # No change

        return obv

    @staticmethod
    def chaikin_money_flow(highs: List[float], lows: List[float], closes: List[float], volumes: List[float], period: int = 21) -> List[float]:
        """Calculate Chaikin Money Flow (CMF)."""
        if len(closes) < period:
            return []

        cmf_values = []
        for i in range(period - 1, len(closes)):
            high_window = highs[i-period+1:i+1]
            low_window = lows[i-period+1:i+1]
            close_window = closes[i-period+1:i+1]
            volume_window = volumes[i-period+1:i+1]

            # Calculate Money Flow Multiplier
            mfm = []
            for h, l, c, v in zip(high_window, low_window, close_window, volume_window):
                if h == l:
                    mfm_val = 0.0
                else:
                    mfm_val = ((c - l) - (h - c)) / (h - l)
                mfm.append(mfm_val)

            # Calculate Money Flow Volume
            mfv = [mfm[j] * volume_window[j] for j in range(len(mfm))]

            # Calculate CMF
            cmf = sum(mfv) / sum(volume_window) if sum(volume_window) != 0 else 0
            cmf_values.append(cmf)

        return cmf_values

    # ===== INDICATOR ANALYSIS METHODS =====

    @classmethod
    def analyze_trend_indicators(cls, prices: List[float], highs: List[float] = None, lows: List[float] = None) -> List[IndicatorResult]:
        """Analyze trend-following indicators."""
        results = []

        # SMA Crossovers
        if len(prices) >= 20:
            sma_10 = cls.simple_moving_average(prices, 10)
            sma_20 = cls.simple_moving_average(prices, 20)

            if sma_10 and sma_20:
                last_10 = sma_10[-1]
                last_20 = sma_20[-1]
                prev_10 = sma_10[-2] if len(sma_10) > 1 else last_10
                prev_20 = sma_20[-2] if len(sma_20) > 1 else last_20

                # Golden Cross / Death Cross detection
                if prev_10 <= prev_20 and last_10 > last_20:
                    signal, strength = "BUY", 0.8
                elif prev_10 >= prev_20 and last_10 < last_20:
                    signal, strength = "SELL", 0.8
                else:
                    signal, strength = "HOLD", 0.5

                results.append(IndicatorResult(
                    name="SMA_Crossover",
                    value=last_10 - last_20,
                    signal=signal,
                    strength=strength,
                    metadata={"sma10": last_10, "sma20": last_20}
                ))

        # MACD Analysis
        if len(prices) >= 35:  # Need enough data for MACD
            macd_line, signal_line, histogram = cls.macd(prices)

            if macd_line and signal_line and histogram:
                last_macd = macd_line[-1]
                last_signal = signal_line[-1]
                last_hist = histogram[-1]

                # MACD Signal
                if last_hist > 0 and len(histogram) > 1 and histogram[-2] <= 0:
                    signal, strength = "BUY", 0.7
                elif last_hist < 0 and len(histogram) > 1 and histogram[-2] >= 0:
                    signal, strength = "SELL", 0.7
                else:
                    signal, strength = "HOLD", 0.6

                results.append(IndicatorResult(
                    name="MACD",
                    value=last_hist,
                    signal=signal,
                    strength=strength,
                    metadata={"macd": last_macd, "signal": last_signal, "histogram": last_hist}
                ))

        return results

    @classmethod
    def analyze_momentum_indicators(cls, prices: List[float], highs: List[float] = None, lows: List[float] = None) -> List[IndicatorResult]:
        """Analyze momentum-based indicators."""
        results = []

        # RSI Analysis
        if len(prices) >= 15:
            rsi_values = cls.rsi(prices, 14)

            if rsi_values:
                last_rsi = rsi_values[-1]

                if last_rsi > 70:
                    signal, strength = "SELL", min(0.8, (last_rsi - 70) / 30)
                elif last_rsi < 30:
                    signal, strength = "BUY", min(0.8, (30 - last_rsi) / 30)
                else:
                    signal, strength = "HOLD", 0.5

                results.append(IndicatorResult(
                    name="RSI",
                    value=last_rsi,
                    signal=signal,
                    strength=strength,
                    metadata={"period": 14}
                ))

        # Stochastic Oscillator (requires OHLC data)
        if highs and lows and len(highs) >= 17 and len(highs) == len(lows) == len(prices):
            k_values, d_values = cls.stochastic_oscillator(highs, lows, prices, 14, 3)

            if k_values and d_values:
                last_k = k_values[-1]
                last_d = d_values[-1]

                # Stochastic signals
                if last_k > 80 and last_d > 80:
                    signal, strength = "SELL", 0.7
                elif last_k < 20 and last_d < 20:
                    signal, strength = "BUY", 0.7
                elif last_k > last_d and len(k_values) > 1 and k_values[-2] <= d_values[-2]:
                    signal, strength = "BUY", 0.6  # %K crosses above %D
                elif last_k < last_d and len(k_values) > 1 and k_values[-2] >= d_values[-2]:
                    signal, strength = "SELL", 0.6  # %K crosses below %D
                else:
                    signal, strength = "HOLD", 0.5

                results.append(IndicatorResult(
                    name="Stochastic",
                    value=last_k,
                    signal=signal,
                    strength=strength,
                    metadata={"k": last_k, "d": last_d, "k_period": 14, "d_period": 3}
                ))

        # Williams %R
        if highs and lows and len(highs) >= 15 and len(highs) == len(lows) == len(prices):
            williams_r = cls.williams_percent_r(highs, lows, prices, 14)

            if williams_r:
                last_r = williams_r[-1]

                if last_r > -20:
                    signal, strength = "SELL", min(0.8, (last_r + 20) / 20)
                elif last_r < -80:
                    signal, strength = "BUY", min(0.8, (-80 - last_r) / 20)
                else:
                    signal, strength = "HOLD", 0.5

                results.append(IndicatorResult(
                    name="Williams_R",
                    value=last_r,
                    signal=signal,
                    strength=strength,
                    metadata={"period": 14}
                ))

        return results

    @classmethod
    def analyze_volatility_indicators(cls, prices: List[float], highs: List[float] = None, lows: List[float] = None) -> List[IndicatorResult]:
        """Analyze volatility-based indicators."""
        results = []

        # Bollinger Bands
        if len(prices) >= 20:
            sma, upper_band, lower_band = cls.bollinger_bands(prices, 20, 2.0)

            if sma and upper_band and lower_band:
                last_price = prices[-1]
                last_sma = sma[-1]
                last_upper = upper_band[-1]
                last_lower = lower_band[-1]

                # Bollinger Band signals
                if last_price <= last_lower:
                    signal, strength = "BUY", min(0.8, (last_lower - last_price) / last_lower)
                elif last_price >= last_upper:
                    signal, strength = "SELL", min(0.8, (last_price - last_upper) / last_upper)
                else:
                    # Mean reversion signals
                    bb_width = (last_upper - last_lower) / last_sma
                    if bb_width > 0.1:  # High volatility
                        signal, strength = "HOLD", 0.6
                    else:
                        signal, strength = "HOLD", 0.4

                results.append(IndicatorResult(
                    name="Bollinger_Bands",
                    value=(last_price - last_sma) / (last_upper - last_lower),
                    signal=signal,
                    strength=strength,
                    metadata={"price": last_price, "sma": last_sma, "upper": last_upper, "lower": last_lower}
                ))

        # Average True Range
        if highs and lows and len(highs) >= 15 and len(highs) == len(lows) == len(prices):
            atr_values = cls.average_true_range(highs, lows, prices, 14)

            if atr_values:
                last_atr = atr_values[-1]
                avg_price = sum(prices[-14:]) / 14
                volatility_ratio = last_atr / avg_price

                # ATR indicates volatility level
                if volatility_ratio > 0.05:  # High volatility
                    signal, strength = "CAUTION", min(0.9, volatility_ratio * 10)
                elif volatility_ratio < 0.01:  # Low volatility
                    signal, strength = "NEUTRAL", 0.3
                else:
                    signal, strength = "NEUTRAL", 0.5

                results.append(IndicatorResult(
                    name="ATR",
                    value=last_atr,
                    signal=signal,
                    strength=strength,
                    metadata={"volatility_ratio": volatility_ratio, "period": 14}
                ))

        return results

    @classmethod
    def analyze_volume_indicators(cls, prices: List[float], volumes: List[float] = None) -> List[IndicatorResult]:
        """Analyze volume-based indicators."""
        results = []

        if volumes and len(volumes) == len(prices):
            # On Balance Volume
            if len(prices) >= 2:
                obv_values = cls.on_balance_volume(prices, volumes)

                if len(obv_values) >= 2:
                    last_obv = obv_values[-1]
                    prev_obv = obv_values[-2]

                    if last_obv > prev_obv:
                        signal, strength = "BUY", 0.6
                    elif last_obv < prev_obv:
                        signal, strength = "SELL", 0.6
                    else:
                        signal, strength = "HOLD", 0.4

                    results.append(IndicatorResult(
                        name="OBV",
                        value=last_obv,
                        signal=signal,
                        strength=strength,
                        metadata={"change": last_obv - prev_obv}
                    ))

            # Chaikin Money Flow
            if len(prices) >= 21:
                cmf_values = cls.chaikin_money_flow([], [], prices, volumes, 21)

                if cmf_values:
                    last_cmf = cmf_values[-1]

                    if last_cmf > 0.25:
                        signal, strength = "BUY", min(0.8, last_cmf)
                    elif last_cmf < -0.25:
                        signal, strength = "SELL", min(0.8, abs(last_cmf))
                    else:
                        signal, strength = "HOLD", 0.5

                    results.append(IndicatorResult(
                        name="CMF",
                        value=last_cmf,
                        signal=signal,
                        strength=strength,
                        metadata={"period": 21}
                    ))

        return results

    @classmethod
    def get_comprehensive_analysis(cls, prices: List[float], highs: List[float] = None,
                                lows: List[float] = None, volumes: List[float] = None) -> Dict[str, List[IndicatorResult]]:
        """Get comprehensive analysis from all available indicators."""
        return {
            "trend": cls.analyze_trend_indicators(prices, highs, lows),
            "momentum": cls.analyze_momentum_indicators(prices, highs, lows),
            "volatility": cls.analyze_volatility_indicators(prices, highs, lows),
            "volume": cls.analyze_volume_indicators(prices, volumes)
        }

    @classmethod
    def get_weighted_signal(cls, analysis_results: Dict[str, List[IndicatorResult]],
                          weights: Dict[str, float] = None) -> IndicatorResult:
        """Combine multiple indicator signals into a weighted overall signal."""
        if weights is None:
            weights = {
                "trend": 0.4,
                "momentum": 0.3,
                "volatility": 0.2,
                "volume": 0.1
            }

        total_score = 0.0
        total_weight = 0.0
        signals = []

        for category, indicators in analysis_results.items():
            weight = weights.get(category, 0.25)

            for indicator in indicators:
                # Convert signal to score
                if indicator.signal == "BUY":
                    score = 1.0
                elif indicator.signal == "SELL":
                    score = -1.0
                elif indicator.signal == "CAUTION":
                    score = 0.0  # Neutral but with caution
                else:
                    score = 0.0

                # Weight by indicator strength
                weighted_score = score * indicator.strength * weight
                total_score += weighted_score
                total_weight += weight
                signals.append(indicator)

        # Normalize score
        if total_weight > 0:
            final_score = total_score / total_weight
        else:
            final_score = 0.0

        # Convert back to signal
        if final_score > 0.3:
            signal = "BUY"
        elif final_score < -0.3:
            signal = "SELL"
        else:
            signal = "HOLD"

        return IndicatorResult(
            name="Composite_Signal",
            value=final_score,
            signal=signal,
            strength=min(1.0, abs(final_score)),
            metadata={"indicators_used": len(signals), "categories": list(analysis_results.keys())}
        )
