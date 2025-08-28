import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from nltk.util import ngrams
from plotly import graph_objects as go
from plotly.subplots import make_subplots
from time import time
from datetime import timedelta
class CandlestickSequenceAnalyzer:
    def __init__(self):
        self.pattern_stats = defaultdict(lambda: {"correct": 0, "total": 0})
    
    def calculate_features(self, df):
        """Calculate technical features for pattern identification."""
        df = df.copy()
        
        # Calculate body size and ATR
        df['body_size'] = abs(df['Close'] - df['Open'])
        df['body_size_pct'] = df['body_size'] / df['Close']
        df['ATR'] = df['body_size'].rolling(window=14).mean()
        
        # Categorize candle size relative to ATR
        df['size_category'] = ((df['Close'] - df['Open']) / df['ATR']).fillna(0)
        df['size_category'] = df['size_category'].apply(
            lambda x: 0 if abs(x) < 0.5 else int(np.sign(x) * min(abs(x), 3))
        )
        
        # Volume analysis
        df['Volume_SMA20'] = df['Volume'].rolling(window=20).mean()
        df['Volume_STD'] = df['Volume'].rolling(window=20).std()
        df['volume_category'] = ((df['Volume'] - df['Volume_SMA20']) / df['Volume_STD']).apply(
            lambda x: 1 if x < -1 else (3 if x > 1 else 2)
        ).fillna(2)
        
        # Price action patterns
        df['prev_low'] = df['Low'].shift(1)
        df['prev_high'] = df['High'].shift(1)
        df['equal_lows'] = (abs(df['Low'] - df['prev_low']) < df['ATR'] * 0.1).astype(int)
        df['equal_highs'] = (abs(df['High'] - df['prev_high']) < df['ATR'] * 0.1).astype(int)
        
        # Higher highs and lower lows
        df['higher_high'] = (df['High'] > df['High'].shift(1)).astype(int)
        df['lower_low'] = (df['Low'] < df['Low'].shift(1)).astype(int)
        
        # Consecutive higher highs and lower lows
        df['consec_higher_high'] = ((df['higher_high'] == 1) & (df['higher_high'].shift(1) == 1)).astype(int)
        df['consec_lower_low'] = ((df['lower_low'] == 1) & (df['lower_low'].shift(1) == 1)).astype(int)
        
        # Higher highs and lower lows
        df['higher_high'] = (df['High'] > df['High'].shift(1)).astype(int)
        df['lower_low'] = (df['Low'] < df['Low'].shift(1)).astype(int)
        
        # Consecutive higher highs and lower lows
        df['consec_higher_high'] = ((df['higher_high'] == 1) & (df['higher_high'].shift(1) == 1)).astype(int)
        df['consec_lower_low'] = ((df['lower_low'] == 1) & (df['lower_low'].shift(1) == 1)).astype(int)
        
        # Higher highs and lower lows relative to previous candle
        df['higher_high'] = (df['High'] > df['prev_high']).astype(int)
        df['lower_low'] = (df['Low'] < df['prev_low']).astype(int)
        
        return df
    
    def identify_patterns(self, df, lookback=3):
        """Identify recurring patterns in the data using n-grams."""
        df = self.calculate_features(df)
        
        # Create feature sequences
        feature_sequences = []
        for i in range(len(df)):
            features = (
                df['size_category'].iloc[i],
                df['volume_category'].iloc[i],
                df['equal_lows'].iloc[i],
                df['equal_highs'].iloc[i],
                df['higher_high'].iloc[i],
                df['lower_low'].iloc[i],
                df['consec_higher_high'].iloc[i],
                df['consec_lower_low'].iloc[i]
            )
            feature_sequences.append(features)
        
        # Generate n-grams from sequences
        pattern_sequences = list(ngrams(feature_sequences, lookback))
        
        # Count pattern occurrences using Counter
        pattern_counts = Counter(pattern_sequences)
            
        return pattern_counts
    
    def predict_next_candles(self, df, n_predictions=3):
        """Predict the next n candles based on identified n-gram patterns."""
        df = self.calculate_features(df)
        lookback = 5
        
        # Get current pattern sequence
        current_sequence = []
        for i in range(-lookback, 0):
            features = (
                df['size_category'].iloc[i],
                df['volume_category'].iloc[i],
                df['equal_lows'].iloc[i],
                df['equal_highs'].iloc[i],
                df['higher_high'].iloc[i],
                df['lower_low'].iloc[i],
                df['consec_higher_high'].iloc[i],
                df['consec_lower_low'].iloc[i]
            )
            current_sequence.append(features)
        current_pattern = tuple(current_sequence)
        
        # Get pattern statistics
        pattern_stats = self.identify_patterns(df, lookback)
        
        # Find similar patterns if exact match not found
        if current_pattern not in pattern_stats:
            # Look for patterns with similar characteristics
            similar_patterns = []
            for pattern in pattern_stats:
                similarity_score = 0
                for i in range(lookback):
                    if pattern[i][0] == current_pattern[i][0]:  # Same size category
                        similarity_score += 1
                    if pattern[i][1] == current_pattern[i][1]:  # Same volume category
                        similarity_score += 1
                    if pattern[i][4] == current_pattern[i][4]:  # Same higher high
                        similarity_score += 1
                    if pattern[i][5] == current_pattern[i][5]:  # Same lower low
                        similarity_score += 1
                if similarity_score >= 8:  # At least 8 matching features
                    similar_patterns.append((pattern, similarity_score, pattern_stats[pattern]))
            
            if not similar_patterns:
                return None
            
            # Use the most similar pattern with highest occurrence
            similar_patterns.sort(key=lambda x: (x[1], x[2]), reverse=True)
            current_pattern = similar_patterns[0][0]
        
        # Generate predictions
        next_candles = []
        last_close = df['Close'].iloc[-1]
        last_atr = df['ATR'].iloc[-1]
        last_volume = df['Volume'].iloc[-1]
        
        for i in range(n_predictions):
            if current_pattern not in pattern_stats:
                break
                
            # Get most likely next state
            pattern_count = pattern_stats[current_pattern]
            confidence = pattern_count / sum(pattern_stats.values())
            
            # Generate candle from predicted state
            size_cat = current_pattern[-1][0]
            volume_cat = current_pattern[-1][1]
            is_higher_high = current_pattern[-1][4]
            is_lower_low = current_pattern[-1][5]
            
            # Calculate predicted values based on pattern characteristics
            pred_size = size_cat * last_atr
            pred_open = last_close
            pred_close = pred_open + pred_size
            
            # Adjust high/low based on pattern indicators
            if is_higher_high:
                pred_high = max(pred_open, pred_close) + last_atr * 0.3
            else:
                pred_high = max(pred_open, pred_close) + last_atr * 0.1
                
            if is_lower_low:
                pred_low = min(pred_open, pred_close) - last_atr * 0.3
            else:
                pred_low = min(pred_open, pred_close) - last_atr * 0.1
            
            next_candle = {
                'Open': pred_open,
                'High': pred_high,
                'Low': pred_low,
                'Close': pred_close,
                'Confidence': confidence,
                'Pattern': current_pattern
            }
            next_candles.append(next_candle)
            
            # Update for next prediction
            current_sequence = list(current_pattern[1:]) + [(size_cat, volume_cat, 0, 0, is_higher_high, is_lower_low, 0, 0)]
            current_pattern = tuple(current_sequence)
            last_close = pred_close
            last_atr = pred_size
            last_volume = df['Volume'].iloc[-1]
        
        
        return next_candles

    def evaluate_prediction(self, predicted, actual):
        """Evaluate the accuracy of predictions."""
        correct_direction = (
            np.sign(actual['Close'] - actual['Open']) ==
            np.sign(predicted['Close'] - predicted['Open'])
        )
        return {
            'direction_accuracy': correct_direction,
            'price_error': abs(predicted['Close'] - actual['Close']) / actual['Close']
        }
        
    def plot_patterns_and_predictions(self, df, predictions=None):
        """Plot candlestick patterns and predictions."""
        # Create candlestick chart with subplots
        fig = go.Figure()
        
        # Create subplots for historical and prediction data
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                           vertical_spacing=0.05,
                           subplot_titles=('Historical Data', 'Predictions'),
                           row_heights=[0.7, 0.3])
        
        # Ensure proper date handling for x-axis with intraday time
        if not isinstance(df.index, pd.DatetimeIndex):
            if 'Date' in df.columns and 'time' in df.columns:
                # Combine date and time columns
                df['datetime'] = pd.to_datetime(df['Date'] + ' ' + df['time'])
                df.index = df['datetime']
            elif 'Date' in df.columns:
                if isinstance(df['Date'].iloc[0], str) and len(df['Date'].iloc[0]) > 10:
                    # Handle datetime strings with time component
                    df.index = pd.to_datetime(df['Date'], format='%Y-%m-%d %H:%M:%S')
                else:
                    # Handle date-only strings
                    df.index = pd.to_datetime(df['Date'])
            else:
                # Create intraday timestamps with 5-minute intervals
                df.index = pd.date_range(
                    start='today', 
                    periods=len(df), 
                    freq='5min',
                    tz='Asia/Kolkata'  # Use appropriate timezone
                )
        
        # Add candlestick data with proper intraday spacing
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Historical Data',
            increasing_line_color='#26a69a',
            decreasing_line_color='#ef5350'
        ), row=1, col=1)
        
        # Add all predictions to the plot
        if predictions and len(predictions) > 0:
            last_date = df.index[-1]
            for i, pred in enumerate(predictions):
                pred_date = last_date + timedelta(minutes=5 * (i + 1))  # Increment time for each prediction
                # Plot each predicted candlestick
                fig.add_trace(go.Candlestick(
                    x=[pred_date],
                    open=[pred['Open']],
                    high=[pred['High']],
                    low=[pred['Low']],
                    close=[pred['Close']],
                    name=f'Prediction {i+1}',
                    increasing_line_color='rgba(38, 166, 154, 0.7)',
                    decreasing_line_color='rgba(239, 83, 80, 0.7)'
                ), row=2, col=1)
                # Add confidence annotation for each prediction
                fig.add_annotation(
                    x=pred_date,
                    y=pred['High'],
                    text=f'Conf: {pred["Confidence"]:.1%}',
                    showarrow=True,
                    arrowhead=1,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor='#888',
                    bgcolor='rgba(255, 255, 255, 0.8)',
                    bordercolor='#888',
                    borderwidth=1,
                    borderpad=4,
                    font=dict(size=10)
                )
        
        # Update layout with improved styling and x-axis configuration
        fig.update_layout(
            title=dict(
                text='Candlestick Patterns and Predictions',
                y=0.95,
                x=0.5,
                xanchor='center',
                yanchor='top',
                font=dict(size=20)
            ),
            height=900,  # Increase total height for better subplot visibility
            yaxis=dict(
                title='Price',
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.2)',
                zeroline=False,
                showspikes=True,
                spikemode='across',
                spikesnap='cursor',
                showline=True,
                linewidth=1,
                linecolor='rgba(128,128,128,0.2)'
            ),
            yaxis2=dict(
                title='Price',
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.2)',
                zeroline=False,
                showspikes=True,
                spikemode='across',
                spikesnap='cursor',
                showline=True,
                linewidth=1,
                linecolor='rgba(128,128,128,0.2)'
            ),
            xaxis=dict(
                title='Date',
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.2)',
                rangeslider=dict(visible=False),
                type='date',
                tickformat='%H:%M:%S',
                tickmode='auto',
                nticks=20,
                showspikes=True,
                spikemode='across',
                spikesnap='cursor',
                showline=True,
                linewidth=1,
                linecolor='rgba(128,128,128,0.2)',
                hoverformat='%Y-%m-%d %H:%M:%S',
                dtick='M5'
            ),
            xaxis2=dict(
                title='Date',
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.2)',
                rangeslider=dict(visible=False),
                type='date',
                tickformat='%H:%M:%S',
                tickmode='auto',
                nticks=20,
                showspikes=True,
                spikemode='across',
                spikesnap='cursor',
                showline=True,
                linewidth=1,
                linecolor='rgba(128,128,128,0.2)',
                hoverformat='%Y-%m-%d %H:%M:%S',
                dtick='M5'
            ),
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=True,
            legend=dict(
                yanchor='top',
                y=0.99,
                xanchor='left',
                x=0.01,
                bgcolor='rgba(255,255,255,0.1)'
            ),
            margin=dict(l=50, r=50, t=80, b=50)  # Increased top margin for subplot titles
            ,
            yaxis_title='Price',
            xaxis_title='Date',
        )
        
        return fig