# PIHS Chart Format Reference

Documentation of PeakedInHighSkool trade value chart layouts and data structures.

## Chart Types

### Redraft Charts
- **Update frequency**: Weekly during NFL season (Weeks 1-17)
- **Release day**: Tuesday evenings
- **URL**: https://peakedinhighskool.com/fantasy-trade-value-chart/

**Scoring Formats**:
- PPR (1.0 point per reception)
- Half-PPR (0.5 points per reception)
- Standard (no reception bonus)

### Dynasty Charts
- **Update frequency**: Monthly
- **URL**: https://peakedinhighskool.com/dynasty-trade-value-charts/

**League Types**:
- Superflex (2 QB/Superflex slot)
- 1 QB (traditional single QB)

## Chart Layout

### Tier Structure
Charts are organized into tiers (typically 1-10):

| Tier | Description | Typical Value Range |
|------|-------------|---------------------|
| 1 | Elite/Untouchable | 90-100 |
| 2 | High-End Starters | 75-89 |
| 3 | Mid-Tier Starters | 60-74 |
| 4 | Low-End Starters | 45-59 |
| 5 | Flex Players | 35-44 |
| 6 | Bench Depth | 25-34 |
| 7 | Streamers/Handcuffs | 15-24 |
| 8 | Deep Bench | 8-14 |
| 9 | Waiver Wire | 3-7 |
| 10 | Rosterable | 1-2 |

### Player Entry Format
Each player entry typically includes:
- **Name**: Full name (e.g., "Ja'Marr Chase")
- **Position**: 2-3 letter code (QB, RB, WR, TE)
- **Team**: NFL team abbreviation
- **Value**: Numeric trade value
- **Trend**: Arrow indicator (↑ up, ↓ down, or none for stable)

### Color Coding
Position colors commonly used:
- **QB**: Often red or orange
- **RB**: Green or teal
- **WR**: Blue or purple
- **TE**: Yellow or gold

Trend colors:
- **Rising**: Green arrow or indicator
- **Falling**: Red arrow or indicator
- **Stable**: No indicator or gray

## Value Scale

The PIHS value scale is typically 0-100:

```
100 ─────────────────── Elite (CMC, Chase at peak)
 90 ─────────────────── Premium
 80 ─────────────────── High-End
 70 ─────────────────── Solid Starter
 60 ─────────────────── Mid-Tier
 50 ─────────────────── Low Starter
 40 ─────────────────── Flex
 30 ─────────────────── Bench
 20 ─────────────────── Deep Bench
 10 ─────────────────── Waiver
  0 ─────────────────── Not Rosterable
```

## Dynasty vs Redraft Differences

### Dynasty Charts
- Include rookies and devy players
- Age significantly impacts value
- Future picks may be included
- Higher QB values in Superflex

### Redraft Charts
- Current season only
- Injury impact is more immediate
- No age consideration
- Schedule/matchups more important

## Data Quality Notes

### Common Extraction Challenges
1. **Name variations**: "D.J. Moore" vs "DJ Moore"
2. **Suffixes**: "Kenneth Walker III" vs "Kenneth Walker"
3. **Nicknames**: "Hollywood Brown" vs "Marquise Brown"
4. **Team changes**: Mid-season trades

### Validation Rules
- Value range: 0-100 (allow 0-150 for buffer)
- Position: Must be QB, RB, WR, TE (or K, DST for redraft)
- Team: Must be valid NFL abbreviation
- Tier: 1-20 (typically 1-10)

## Example Extracted Data

```json
{
  "player_name": "Ja'Marr Chase",
  "position": "WR",
  "team": "CIN",
  "value": 95,
  "tier": 1,
  "trend": "stable"
}
```

## Sources

- Official website: https://peakedinhighskool.com/
- Twitter: [@PeakedInHS_FF](https://twitter.com/PeakedInHS_FF)
- Methodology: Combines expert rankings, user trade data, and expected points models
