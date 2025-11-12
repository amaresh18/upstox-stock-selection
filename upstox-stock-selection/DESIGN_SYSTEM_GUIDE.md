# Zerodha Kite Premium Design System Guide

## Overview

This document describes the complete design system implementation for the Stock Selection platform, inspired by Zerodha Kite's world-class UI/UX.

## Design Tokens

### Colors

**Primary Palette:**
- `--kite-primary`: #2962FF (Main brand blue)
- `--kite-primary-dark`: #1E4ED8 (Hover states)
- `--kite-primary-light`: #5C7AFF (Light variants)
- `--kite-primary-lighter`: #E3F2FD (Background tints)

**Semantic Colors:**
- Success: #00C853 (Green)
- Danger: #F44336 (Red)
- Warning: #FF9800 (Orange)
- Info: #2196F3 (Blue)

**Backgrounds:**
- Primary: #FFFFFF (White)
- Secondary: #F5F7FA (Light gray)
- Tertiary: #FAFBFC (Very light gray)
- Hover: #F8F9FA (Hover state)

**Text:**
- Primary: #1E293B (Dark slate)
- Secondary: #64748B (Medium gray)
- Tertiary: #94A3B8 (Light gray)
- Disabled: #CBD5E1 (Very light gray)

### Typography

**Font Family:**
- Primary: `-apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', 'Roboto'`
- Monospace: `'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code'`

**Font Sizes:**
- xs: 0.75rem (12px)
- sm: 0.875rem (14px)
- base: 1rem (16px)
- lg: 1.125rem (18px)
- xl: 1.25rem (20px)
- 2xl: 1.5rem (24px)
- 3xl: 1.875rem (30px)
- 4xl: 2.25rem (36px)

**Font Weights:**
- Normal: 400
- Medium: 500
- Semibold: 600
- Bold: 700

### Spacing

- 0: 0
- 1: 0.25rem (4px)
- 2: 0.5rem (8px)
- 3: 0.75rem (12px)
- 4: 1rem (16px)
- 5: 1.25rem (20px)
- 6: 1.5rem (24px)
- 8: 2rem (32px)
- 10: 2.5rem (40px)
- 12: 3rem (48px)
- 16: 4rem (64px)

### Border Radius

- sm: 4px
- md: 6px
- lg: 8px
- xl: 12px
- 2xl: 16px
- full: 9999px

### Shadows

- xs: Subtle elevation (0 1px 2px)
- sm: Light elevation (0 1px 3px)
- md: Medium elevation (0 4px 6px)
- lg: Large elevation (0 10px 15px)
- xl: Extra large elevation (0 20px 25px)

### Transitions

- fast: 0.1s ease
- base: 0.15s ease
- slow: 0.3s ease
- slower: 0.5s ease

## Components

### Navbar

Sticky top navigation bar with brand and actions.

```python
render_navbar(
    title="Stock Selection",
    subtitle="Professional algorithmic trading platform"
)
```

### Cards

Premium card components with multiple variants.

```python
render_card(
    title="Card Title",
    subtitle="Card subtitle",
    content="<p>Card content</p>",
    variant="floating",  # "default", "floating", "glass"
    class_name="kite-fade-in"
)
```

### Alert Cards

Stock signal alert cards with breakout/breakdown indicators.

```python
render_alert_card(
    symbol="RELIANCE",
    signal_type="BREAKOUT",
    price=2450.50,
    vol_ratio=2.5,
    swing_level=2400.00,
    timestamp="10:15 IST"
)
```

### Section Headers

Premium section headers with optional actions.

```python
render_section_header(
    title="Analysis Results",
    subtitle="Review your comprehensive stock selection analysis"
)
```

### Badges

Status badges with semantic colors.

```python
render_badge("BREAKOUT", variant="success")
render_badge("BREAKDOWN", variant="danger")
```

### Metric Cards

Key metric display cards.

```python
render_metric_card(
    label="Total Alerts",
    value="42",
    delta="+12%",
    delta_color="success"
)
```

### Empty States

Elegant empty state displays.

```python
render_empty_state(
    icon="📊",
    title="No Alerts",
    message="No stocks met the selection criteria.",
    action_label="Run Analysis"
)
```

## Usage Examples

### Complete Dashboard Layout

```python
# Navbar
render_navbar(title="Stock Selection", subtitle="Trading Platform")

# Hero Section
render_card(
    title="Welcome",
    subtitle="Start your analysis",
    variant="floating"
)

# Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    render_metric_card("Total Symbols", "100")
with col2:
    render_metric_card("Alerts", "42", "+12%", "success")
with col3:
    render_metric_card("Win Rate", "68%")
with col4:
    render_metric_card("Avg Return", "12.5%")

# Section Header
render_section_header(
    title="Recent Alerts",
    subtitle="Latest trading opportunities"
)

# Alert Cards
for alert in alerts:
    render_alert_card(
        symbol=alert['symbol'],
        signal_type=alert['type'],
        price=alert['price'],
        vol_ratio=alert['vol_ratio']
    )
```

## Best Practices

1. **Consistency**: Always use design tokens (CSS variables) instead of hardcoded values
2. **Spacing**: Use the spacing scale consistently (--kite-space-*)
3. **Colors**: Use semantic color names (--kite-success, --kite-danger) for clarity
4. **Typography**: Follow the type scale for hierarchy
5. **Shadows**: Use subtle shadows (xs, sm) for depth, avoid heavy shadows
6. **Transitions**: Keep transitions fast (0.15s) for responsiveness
7. **Responsive**: Always test on mobile devices
8. **Accessibility**: Maintain proper contrast ratios and focus states

## Animation Guidelines

- **Fade In**: Use for new content appearing
- **Slide In**: Use for side panels and modals
- **Pulse**: Use sparingly for loading states
- **Hover**: Subtle lift (translateY(-1px)) with shadow increase

## Responsive Breakpoints

- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

## Dark Mode (Future)

The design system is prepared for dark mode with CSS variables. A theme switcher can toggle between light and dark variants.

