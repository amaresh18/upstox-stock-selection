# How Scheduling Works

## Overview

The script **does NOT use an external scheduler** (like cron, Windows Task Scheduler, or Railway's scheduler). Instead, it runs **continuously** and schedules itself internally.

## How It Works

### 1. Railway Keeps the Script Running

Railway runs the script as a **long-running process**:

```bash
python scripts/run_continuous_alerts.py
```

Railway's job is just to:
- ✅ Keep the script running 24/7
- ✅ Restart it if it crashes
- ✅ Provide logs

Railway **does NOT** schedule when the script runs checks.

### 2. The Script Schedules Itself

The script has an **infinite loop** that:

1. **Checks current time**
2. **Calculates next check time** (9:15:30, 10:15:30, etc.)
3. **Waits until that time** using `asyncio.sleep()`
4. **Runs the check** when time arrives
5. **Repeats** forever

## Where Timing is Configured

### Location: `scripts/run_continuous_alerts.py`

#### 1. Check Times Definition (Line 107)

```python
# Check at 9:15:30, 10:15:30, 11:15:30, 12:15:30, 13:15:30, 14:15:30, 15:15:30
# (30 seconds after each hour to ensure hourly candle is complete and catch stocks on time)
```

**To change check times**, modify this logic in the `get_next_check_time()` method.

#### 2. Market Hours (Line 114)

```python
# Market hours: 9:15 AM - 3:30 PM IST
market_hours = [9, 10, 11, 12, 13, 14, 15]
```

**To change market hours**, modify this list.

#### 3. Check Time Calculation (Lines 116-133)

```python
# Find next check time
if current_hour < 9:
    # Before market opens, check at 9:15:30
    next_check = now.replace(hour=9, minute=15, second=30, microsecond=0)
elif current_hour > 15 or (current_hour == 15 and current_minute >= 30):
    # After market closes, check tomorrow at 9:15:30
    next_check = (now + timedelta(days=1)).replace(hour=9, minute=15, second=30, microsecond=0)
elif current_minute < 15 or (current_minute == 15 and current_second < 30):
    # Current hour hasn't completed yet, check at :15:30 of current hour
    next_check = now.replace(minute=15, second=30, microsecond=0)
else:
    # Current hour has completed, check at :15:30 of next hour
    next_hour = current_hour + 1
    if next_hour in market_hours:
        next_check = now.replace(hour=next_hour, minute=15, second=30, microsecond=0)
```

**This logic calculates the next check time** based on current time.

#### 4. Main Loop (Lines 300-350)

```python
while True:  # Infinite loop
    now = datetime.now(self.ist)
    
    if self.is_market_open():
        # Market is open - check for alerts
        await self.check_for_alerts()
        
        # Calculate next check time
        next_check = self.get_next_check_time()
        wait_seconds = (next_check - now).total_seconds()
        
        # Wait until next check time
        await asyncio.sleep(wait_seconds)
    else:
        # Market is closed - wait and check again
        await asyncio.sleep(3600)  # Wait 1 hour
```

**This loop runs forever**, checking and waiting in cycles.

## How to Change Check Times

### Example: Change to Check Every 30 Minutes

1. **Modify `get_next_check_time()` method** in `scripts/run_continuous_alerts.py`:

```python
def get_next_check_time(self) -> datetime:
    now = datetime.now(self.ist)
    
    # Check every 30 minutes: 9:15, 9:45, 10:15, 10:45, etc.
    current_minute = now.minute
    
    if current_minute < 15:
        # Check at :15 of current hour
        next_check = now.replace(minute=15, second=30, microsecond=0)
    elif current_minute < 45:
        # Check at :45 of current hour
        next_check = now.replace(minute=45, second=30, microsecond=0)
    else:
        # Check at :15 of next hour
        next_hour = now.hour + 1
        next_check = now.replace(hour=next_hour, minute=15, second=30, microsecond=0)
    
    return next_check
```

### Example: Change to Check Every 15 Minutes

```python
def get_next_check_time(self) -> datetime:
    now = datetime.now(self.ist)
    
    # Check every 15 minutes: 9:15, 9:30, 9:45, 10:00, 10:15, etc.
    current_minute = now.minute
    
    if current_minute < 15:
        next_check = now.replace(minute=15, second=30, microsecond=0)
    elif current_minute < 30:
        next_check = now.replace(minute=30, second=30, microsecond=0)
    elif current_minute < 45:
        next_check = now.replace(minute=45, second=30, microsecond=0)
    else:
        # Next hour at :15
        next_hour = now.hour + 1
        next_check = now.replace(hour=next_hour, minute=15, second=30, microsecond=0)
    
    return next_check
```

### Example: Change to Check at Specific Times

```python
def get_next_check_time(self) -> datetime:
    now = datetime.now(self.ist)
    
    # Check at specific times: 9:30, 10:00, 11:00, 12:00, 13:00, 14:00, 15:00
    check_times = [
        (9, 30, 0),   # 9:30:00
        (10, 0, 0),   # 10:00:00
        (11, 0, 0),   # 11:00:00
        (12, 0, 0),   # 12:00:00
        (13, 0, 0),   # 13:00:00
        (14, 0, 0),   # 14:00:00
        (15, 0, 0),   # 15:00:00
    ]
    
    # Find next check time
    for hour, minute, second in check_times:
        check_time = now.replace(hour=hour, minute=minute, second=second, microsecond=0)
        if check_time > now:
            return check_time
    
    # If all times passed, check tomorrow at first time
    tomorrow = now + timedelta(days=1)
    return tomorrow.replace(hour=9, minute=30, second=0, microsecond=0)
```

## Current Configuration

### Check Times
- **9:15:30** (30 seconds after 9:15 AM)
- **10:15:30** (30 seconds after 10:15 AM)
- **11:15:30** (30 seconds after 11:15 AM)
- **12:15:30** (30 seconds after 12:15 PM)
- **13:15:30** (30 seconds after 1:15 PM)
- **14:15:30** (30 seconds after 2:15 PM)
- **15:15:30** (30 seconds after 3:15 PM)

### Why 30 Seconds After Each Hour?

- Hourly candles complete at `:15` of each hour (e.g., 9:15, 10:15)
- We wait 30 seconds to ensure the candle is fully formed
- This gives us the fastest possible alerts while ensuring data accuracy

## Flow Diagram

```
Railway Starts Script
        ↓
Script Enters Main Loop
        ↓
Check Current Time
        ↓
Is Market Open?
    ├─ YES → Calculate Next Check Time (9:15:30, 10:15:30, etc.)
    │         ↓
    │    Wait Until Next Check Time
    │         ↓
    │    Run Alert Check
    │         ↓
    │    Loop Back
    │
    └─ NO → Wait 1 Hour
             ↓
        Loop Back
```

## Key Points

1. **No External Scheduler**: The script doesn't use cron, Windows Task Scheduler, or Railway's scheduler
2. **Self-Scheduling**: The script calculates and waits for the next check time internally
3. **Continuous Running**: Railway keeps the script running 24/7, but the script manages its own timing
4. **Flexible**: You can modify `get_next_check_time()` to change check times without changing Railway configuration

## Verification

To verify the script is running at scheduled times:

1. Check Railway logs for `⏰ CHECK TIME:` messages
2. Verify timestamps match scheduled times (9:15:30, 10:15:30, etc.)
3. See [Railway Monitoring Guide](RAILWAY_MONITORING.md) for details

---

**Summary**: Railway keeps the script running, but the script itself schedules when to check for alerts using an internal loop and time calculations.

