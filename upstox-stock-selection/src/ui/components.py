"""
Premium UI Components for Zerodha Kite-inspired Design System

Reusable components for building a world-class trading platform UI.
"""

import streamlit as st
from typing import Optional, List, Dict, Any
from datetime import datetime


def render_navbar(title: str = "Stock Selection", subtitle: Optional[str] = None):
    """
    Render a premium top navigation bar.
    
    Args:
        title: Main title text
        subtitle: Optional subtitle text
    """
    st.markdown(f"""
    <div class="kite-navbar">
        <div class="kite-navbar-brand">
            <span>📈</span>
            <div>
                <div style="font-size: 1.125rem; font-weight: 600; color: #1E293B;">
                    {title}
                </div>
                {f'<div style="font-size: 0.75rem; color: #64748B; margin-top: 2px;">{subtitle}</div>' if subtitle else ''}
            </div>
        </div>
        <div class="kite-navbar-actions">
            <!-- Add action buttons here if needed -->
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_card(
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    content: Optional[str] = None,
    variant: str = "default",
    class_name: str = ""
):
    """
    Render a premium card component.
    
    Args:
        title: Card title
        subtitle: Card subtitle
        content: HTML content for card body
        variant: Card variant ("default", "floating", "glass")
        class_name: Additional CSS classes
    """
    variant_class = {
        "default": "",
        "floating": "kite-card-floating",
        "glass": "kite-card-glass"
    }.get(variant, "")
    
    # Build header HTML
    header_html = ""
    if title or subtitle:
        title_html = f'<div class="kite-card-title">{title}</div>' if title else ''
        subtitle_html = f'<div class="kite-card-subtitle">{subtitle}</div>' if subtitle else ''
        header_html = f'<div class="kite-card-header"><div>{title_html}{subtitle_html}</div></div>'
    
    # Build body HTML
    body_html = f'<div class="kite-card-body">{content or ""}</div>' if content else ""
    
    # Combine all HTML into a single line to avoid rendering issues
    card_html = f'<div class="kite-card {variant_class} {class_name}">{header_html}{body_html}</div>'
    
    # Render using markdown with unsafe_allow_html
    st.markdown(card_html, unsafe_allow_html=True)


def render_alert_card(
    symbol: str,
    signal_type: str,
    price: Optional[float] = None,
    vol_ratio: Optional[float] = None,
    swing_level: Optional[float] = None,
    timestamp: Optional[str] = None,
    price_momentum: Optional[float] = None,
    additional_info: Optional[Dict[str, Any]] = None
):
    """
    Render a premium alert card for stock signals.
    
    Args:
        symbol: Stock symbol
        signal_type: "BREAKOUT", "BREAKDOWN", or "VOLUME_SPIKE_15M"
        price: Current price
        vol_ratio: Volume ratio
        swing_level: Swing high/low level (not applicable for volume spikes)
        timestamp: Alert timestamp
        additional_info: Additional key-value pairs to display
    """
    signal_type_upper = signal_type.upper()
    
    # Handle different alert types
    if signal_type_upper == "VOLUME_SPIKE_15M":
        is_breakout = True  # Use green for volume spikes
        border_color = "#2196F3"  # Blue for volume spikes
        badge_bg = "rgba(33, 150, 243, 0.1)"
        badge_text = "#2196F3"
        alert_class = "kite-alert-primary"
        signal_badge = "VOLUME SPIKE 15M"
        level_text = "15-minute volume spike detected"
    else:
        is_breakout = signal_type_upper == "BREAKOUT"
        border_color = "#00C853" if is_breakout else "#F44336"
        badge_bg = "rgba(0, 200, 83, 0.1)" if is_breakout else "rgba(244, 67, 54, 0.1)"
        badge_text = "#00C853" if is_breakout else "#F44336"
        alert_class = "kite-alert-success" if is_breakout else "kite-alert-danger"
        signal_badge = "BREAKOUT" if is_breakout else "BREAKDOWN"
        
        level_text = ""
        if swing_level:
            level_text = f"Above ₹{swing_level:.2f}" if is_breakout else f"Below ₹{swing_level:.2f}"
    
    details = []
    if price is not None:
        details.append(f'<span style="color: #64748B; font-size: 0.875rem;">Price:</span> <span style="color: #1E293B; font-weight: 500; font-size: 0.875rem;">₹{price:.2f}</span>')
    if vol_ratio is not None:
        details.append(f'<span style="color: #64748B; font-size: 0.875rem;">Volume:</span> <span style="color: #1E293B; font-weight: 500; font-size: 0.875rem;">{vol_ratio:.2f}×</span>')
    if price_momentum is not None:
        momentum_color = "#00C853" if price_momentum > 0 else "#F44336" if price_momentum < 0 else "#64748B"
        momentum_sign = "+" if price_momentum > 0 else ""
        details.append(f'<span style="color: #64748B; font-size: 0.875rem;">Momentum:</span> <span style="color: {momentum_color}; font-weight: 500; font-size: 0.875rem;">{momentum_sign}{price_momentum:.2f}%</span>')
    
    if timestamp:
        details.append(f'<span style="color: #64748B; font-size: 0.875rem;">Time:</span> <span style="color: #1E293B; font-weight: 500; font-size: 0.875rem;">{timestamp}</span>')
    
    # Add average momentum and momentum ratio if available in additional_info
    if additional_info:
        # Handle momentum comparison fields first (special formatting)
        if 'Avg Momentum (7d)' in additional_info:
            avg_mom = additional_info['Avg Momentum (7d)']
            details.append(f'<span style="color: #64748B; font-size: 0.875rem;">Avg (7d):</span> <span style="color: #1E293B; font-weight: 500; font-size: 0.875rem;">{avg_mom}</span>')
        if 'Momentum Ratio' in additional_info:
            mom_ratio = additional_info['Momentum Ratio']
            try:
                ratio_value = float(mom_ratio.replace('×', ''))
                ratio_color = "#00C853" if ratio_value > 1.0 else "#F44336" if ratio_value < 1.0 else "#64748B"
            except:
                ratio_color = "#64748B"
            details.append(f'<span style="color: #64748B; font-size: 0.875rem;">vs Avg:</span> <span style="color: {ratio_color}; font-weight: 500; font-size: 0.875rem;">{mom_ratio}</span>')
        
        # Add other additional info fields (excluding momentum fields already handled)
        excluded_keys = {'Avg Momentum (7d)', 'Momentum Ratio'}
        for key, value in additional_info.items():
            if key not in excluded_keys:
                details.append(f'<span style="color: #64748B; font-size: 0.875rem;">{key}:</span> <span style="color: #1E293B; font-weight: 500; font-size: 0.875rem;">{value}</span>')
    
    st.markdown(f"""
    <div class="kite-alert {alert_class} kite-fade-in">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
            <div style="font-weight: 600; font-size: 1rem; color: #1E293B; letter-spacing: -0.01em;">
                {symbol}
            </div>
            <span class="kite-badge {'kite-badge-primary' if signal_type_upper == 'VOLUME_SPIKE_15M' else ('kite-badge-success' if is_breakout else 'kite-badge-danger')}" style="background: {badge_bg}; color: {badge_text}; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em;">
                {signal_badge}
            </span>
        </div>
        {f'<div style="color: #64748B; font-size: 0.875rem; margin-bottom: 0.75rem; font-weight: 400;">{level_text}</div>' if level_text else ''}
        <div style="color: #1E293B; font-size: 0.875rem; display: flex; gap: 1.25rem; flex-wrap: wrap; font-weight: 400;">
            {' | '.join(details)}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_section_header(title: str, subtitle: Optional[str] = None, action: Optional[str] = None):
    """
    Render a premium section header.
    
    Args:
        title: Section title
        subtitle: Optional subtitle
        action: Optional action button HTML
    """
    subtitle_html = f'<div class="kite-section-subtitle">{subtitle}</div>' if subtitle else ""
    action_html = f'<div>{action}</div>' if action else ""
    
    st.markdown(f"""
    <div class="kite-section-header">
        <div>
            <div class="kite-section-title">{title}</div>
            {subtitle_html}
        </div>
        {action_html}
    </div>
    """, unsafe_allow_html=True)


def render_badge(text: str, variant: str = "primary"):
    """
    Render a premium badge component.
    
    Args:
        text: Badge text
        variant: Badge variant ("primary", "success", "danger", "warning", "info")
    """
    variant_class = f"kite-badge-{variant}"
    
    return f'<span class="kite-badge {variant_class}">{text}</span>'


def render_metric_card(label: str, value: str, delta: Optional[str] = None, delta_color: Optional[str] = None):
    """
    Render a premium metric card.
    
    Args:
        label: Metric label
        value: Metric value
        delta: Optional delta value
        delta_color: Optional delta color ("success", "danger", etc.)
    """
    delta_html = ""
    if delta:
        color = {
            "success": "#00C853",
            "danger": "#F44336",
            "warning": "#FF9800",
            "info": "#2196F3"
        }.get(delta_color or "info", "#64748B")
        delta_html = f'<div style="color: {color}; font-size: 0.875rem; margin-top: 0.25rem;">{delta}</div>'
    
    st.markdown(f"""
    <div class="kite-card" style="text-align: center;">
        <div style="font-size: 2rem; font-weight: 600; color: #1E293B; line-height: 1.2;">
            {value}
        </div>
        <div style="font-size: 0.75rem; color: #64748B; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.5rem;">
            {label}
        </div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_empty_state(
    icon: str = "📊",
    title: str = "No Data",
    message: str = "There's nothing to display here yet.",
    action_label: Optional[str] = None,
    action_callback: Optional[callable] = None
):
    """
    Render a premium empty state component.
    
    Args:
        icon: Icon emoji or symbol
        title: Empty state title
        message: Empty state message
        action_label: Optional action button label
        action_callback: Optional action callback function
    """
    action_html = ""
    if action_label:
        action_html = f'<button class="kite-btn-primary" style="margin-top: 1rem;">{action_label}</button>'
    
    st.markdown(f"""
    <div class="kite-card" style="text-align: center; padding: 3rem 2rem;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">{icon}</div>
        <div style="font-size: 1.25rem; font-weight: 600; color: #1E293B; margin-bottom: 0.5rem;">
            {title}
        </div>
        <div style="font-size: 0.875rem; color: #64748B; margin-bottom: 1rem;">
            {message}
        </div>
        {action_html}
    </div>
    """, unsafe_allow_html=True)


def render_loading_skeleton(width: str = "100%", height: str = "100px"):
    """
    Render a loading skeleton placeholder.
    
    Args:
        width: Skeleton width
        height: Skeleton height
    """
    st.markdown(f"""
    <div class="kite-skeleton" style="width: {width}; height: {height}; margin-bottom: 1rem;"></div>
    """, unsafe_allow_html=True)


def render_tooltip(text: str, tooltip_text: str):
    """
    Render text with a tooltip.
    
    Args:
        text: Display text
        tooltip_text: Tooltip text
    """
    return f'<span class="kite-tooltip" data-tooltip="{tooltip_text}">{text}</span>'


def render_divider():
    """Render a premium divider."""
    st.markdown('<div class="kite-divider"></div>', unsafe_allow_html=True)


def render_group_label(text: str):
    """
    Render a group label (for form sections).
    
    Args:
        text: Label text
    """
    st.markdown(f"""
    <div style="font-size: 0.75rem; font-weight: 500; color: #64748B; 
                text-transform: uppercase; letter-spacing: 0.05em; 
                margin-top: 1rem; margin-bottom: 0.5rem;">
        {text}
    </div>
    """, unsafe_allow_html=True)


def show_toast(message: str, variant: str = "info", duration: int = 3000):
    """
    Show a premium toast notification.
    
    Args:
        message: Toast message
        variant: Toast variant ("success", "error", "warning", "info")
        duration: Duration in milliseconds (default 3000ms)
    """
    toast_id = f"toast_{datetime.now().timestamp()}"
    
    variant_config = {
        "success": {
            "bg": "rgba(0, 200, 83, 0.95)",
            "border": "#00C853",
            "icon": "✅"
        },
        "error": {
            "bg": "rgba(244, 67, 54, 0.95)",
            "border": "#F44336",
            "icon": "❌"
        },
        "warning": {
            "bg": "rgba(255, 152, 0, 0.95)",
            "border": "#FF9800",
            "icon": "⚠️"
        },
        "info": {
            "bg": "rgba(41, 98, 255, 0.95)",
            "border": "#2962FF",
            "icon": "ℹ️"
        }
    }
    
    config = variant_config.get(variant, variant_config["info"])
    
    st.markdown(f"""
    <div id="{toast_id}" class="kite-toast" style="
        position: fixed;
        top: 20px;
        right: 20px;
        background: {config['bg']};
        color: white;
        padding: 1rem 1.25rem;
        border-radius: 8px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        border-left: 3px solid {config['border']};
        z-index: 10000;
        min-width: 300px;
        max-width: 400px;
        animation: slideInRight 0.3s ease-out;
        font-size: 0.875rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    ">
        <span style="font-size: 1.25rem;">{config['icon']}</span>
        <span style="flex: 1;">{message}</span>
    </div>
    <script>
        setTimeout(function() {{
            var toast = document.getElementById('{toast_id}');
            if (toast) {{
                toast.style.animation = 'fadeOutRight 0.3s ease-out';
                setTimeout(function() {{
                    if (toast) toast.remove();
                }}, 300);
            }}
        }}, {duration});
    </script>
    <style>
        @keyframes slideInRight {{
            from {{
                transform: translateX(100%);
                opacity: 0;
            }}
            to {{
                transform: translateX(0);
                opacity: 1;
            }}
        }}
        @keyframes fadeOutRight {{
            from {{
                transform: translateX(0);
                opacity: 1;
            }}
            to {{
                transform: translateX(100%);
                opacity: 0;
            }}
        }}
    </style>
    """, unsafe_allow_html=True)


def render_tooltip_enhanced(text: str, tooltip_text: str, position: str = "top"):
    """
    Render text with an enhanced tooltip.
    
    Args:
        text: Display text
        tooltip_text: Tooltip text
        position: Tooltip position ("top", "bottom", "left", "right")
    """
    tooltip_id = f"tooltip_{datetime.now().timestamp()}"
    
    position_styles = {
        "top": "bottom: 100%; left: 50%; transform: translateX(-50%); margin-bottom: 8px;",
        "bottom": "top: 100%; left: 50%; transform: translateX(-50%); margin-top: 8px;",
        "left": "right: 100%; top: 50%; transform: translateY(-50%); margin-right: 8px;",
        "right": "left: 100%; top: 50%; transform: translateY(-50%); margin-left: 8px;"
    }
    
    style = position_styles.get(position, position_styles["top"])
    
    return f'''
    <span class="kite-tooltip-wrapper" style="position: relative; display: inline-block; cursor: help;">
        {text}
        <span class="kite-tooltip-content" style="
            visibility: hidden;
            opacity: 0;
            position: absolute;
            {style}
            background: #1E293B;
            color: white;
            padding: 0.5rem 0.75rem;
            border-radius: 6px;
            font-size: 0.75rem;
            white-space: nowrap;
            z-index: 1000;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            transition: opacity 0.2s, visibility 0.2s;
            pointer-events: none;
        ">
            {tooltip_text}
        </span>
    </span>
    <style>
        .kite-tooltip-wrapper:hover .kite-tooltip-content {{
            visibility: visible;
            opacity: 1;
        }}
    </style>
    '''


def render_theme_switcher():
    """
    Render a theme switcher (dark/light mode) button.
    """
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    
    theme_icon = "🌙" if st.session_state.theme == 'light' else "☀️"
    theme_label = "Dark Mode" if st.session_state.theme == 'light' else "Light Mode"
    
    return st.button(
        f"{theme_icon} {theme_label}",
        key="theme_switcher",
        help="Toggle between light and dark theme"
    )


def get_theme_css(theme: str = "light") -> str:
    """
    Get theme-specific CSS.
    
    Args:
        theme: Theme name ("light" or "dark")
    """
    if theme == "dark":
        return """
        :root {
            --kite-bg-primary: #1E293B;
            --kite-bg-secondary: #0F172A;
            --kite-bg-tertiary: #1E293B;
            --kite-bg-hover: #334155;
            --kite-text-primary: #F1F5F9;
            --kite-text-secondary: #CBD5E1;
            --kite-text-tertiary: #94A3B8;
            --kite-border: #334155;
            --kite-border-light: #475569;
            --kite-border-dark: #64748B;
        }
        body {
            background: var(--kite-bg-secondary);
            color: var(--kite-text-primary);
        }
        """
    else:
        return """
        :root {
            --kite-bg-primary: #FFFFFF;
            --kite-bg-secondary: #F5F7FA;
            --kite-bg-tertiary: #FAFBFC;
            --kite-bg-hover: #F8F9FA;
            --kite-text-primary: #1E293B;
            --kite-text-secondary: #64748B;
            --kite-text-tertiary: #94A3B8;
            --kite-border: #E2E8F0;
            --kite-border-light: #F1F5F9;
            --kite-border-dark: #CBD5E1;
        }
        body {
            background: var(--kite-bg-secondary);
            color: var(--kite-text-primary);
        }
        """

