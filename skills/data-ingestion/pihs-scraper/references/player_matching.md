# Player Matching Reference

Strategies for matching PIHS player names to existing Neo4j Player nodes.

## Matching Hierarchy

The loader attempts to match players in this order:

1. **Exact name match** (case-insensitive)
2. **Sleeper ID match** (if available)
3. **GSIS ID match** (if available)
4. **Fuzzy name match** (normalized)

## Name Normalization

### Standard Transformations

```python
def normalize_name(name: str) -> str:
    """Normalize player name for matching."""
    # Convert to lowercase
    name = name.lower()

    # Remove punctuation
    name = name.replace("'", "")  # Ja'Marr -> JaMarr
    name = name.replace(".", "")  # D.J. -> DJ

    # Remove suffixes
    suffixes = ['jr', 'sr', 'ii', 'iii', 'iv', 'v']
    parts = name.split()
    parts = [p for p in parts if p not in suffixes]

    return ' '.join(parts)
```

### Common Variations

| PIHS Name | Database Name | Solution |
|-----------|---------------|----------|
| D.J. Moore | DJ Moore | Remove periods |
| Ja'Marr Chase | JaMarr Chase | Remove apostrophe |
| Kenneth Walker III | Kenneth Walker | Remove suffix |
| Gabriel Davis | Gabe Davis | Nickname mapping |
| Hollywood Brown | Marquise Brown | Nickname mapping |
| AJ Brown | A.J. Brown | Period normalization |
| DK Metcalf | D.K. Metcalf | Period normalization |

## Nickname Mappings

Common nickname to legal name mappings:

```python
NICKNAME_MAP = {
    'hollywood brown': 'marquise brown',
    'gabe davis': 'gabriel davis',
    'mike williams': 'michael williams',
    'mike evans': 'michael evans',
    'rob gronkowski': 'robert gronkowski',
    'pat mahomes': 'patrick mahomes',
    'josh allen': 'joshua allen',
    'dak prescott': 'rayne prescott',
    'tee higgins': 'george higgins',
    'dk metcalf': 'deandre metcalf',
    'aj brown': 'arthur brown',
    'cj stroud': 'christopher stroud',
    'jj mccarthy': 'justin mccarthy',
}
```

## Fuzzy Matching Strategy

When exact match fails, use fuzzy matching:

### Last Name First
Most unique identifier is last name:

```python
def fuzzy_match(player_name: str, position: str = None) -> Optional[str]:
    parts = player_name.lower().split()
    last_name = parts[-1]

    # Query by last name
    matches = query_players_by_name_part(last_name, position)

    # If single match, return it
    if len(matches) == 1:
        return matches[0]['gsis_id']

    # Multiple matches - check first name
    first_name = parts[0]
    for match in matches:
        match_parts = match['name'].lower().split()
        if match_parts[0].startswith(first_name[:3]):
            return match['gsis_id']

    return None
```

### Position Filtering
Always filter by position when available:
- Reduces false matches
- Handles common names better (e.g., "Mike Williams" WR vs TE)

## Database ID Fields

The ktcvaluehog database supports multiple ID types:

| Field | Source | Format | Example |
|-------|--------|--------|---------|
| gsis_id | NFL Official | UUID-like | 00-0033873 |
| sleeper_id | Sleeper | Numeric string | 4046 |
| espn_id | ESPN | Numeric | 3116385 |
| pfr_id | Pro Football Reference | String | ChasJa00 |
| yahoo_id | Yahoo | Numeric | 33389 |

### ID Resolution Query

```cypher
MATCH (p:Player)
WHERE p.gsis_id IS NOT NULL OR p.sleeper_id IS NOT NULL
RETURN p.name, p.gsis_id, p.sleeper_id, p.position, p.team
ORDER BY p.name
```

## Unmatched Player Handling

When a player cannot be matched:

1. **Still create PIHSValue node** - for data completeness
2. **Log unmatched name** - for manual review
3. **Skip relationship creation** - no HAS_PIHS_VALUE link

### Periodic Reconciliation

Run periodically to link unmatched nodes:

```cypher
// Find unlinked PIHSValue nodes
MATCH (pv:PIHSValue)
WHERE NOT exists((pv)<-[:HAS_PIHS_VALUE]-(:Player))
RETURN pv.player_name, pv.position, count(*) as occurrences
ORDER BY occurrences DESC

// Attempt re-linking with fuzzy match
MATCH (pv:PIHSValue)
WHERE NOT exists((pv)<-[:HAS_PIHS_VALUE]-(:Player))
MATCH (p:Player)
WHERE toLower(p.name) CONTAINS toLower(split(pv.player_name, ' ')[-1])
  AND p.position = pv.position
WITH pv, p,
     CASE WHEN toLower(p.name) = toLower(pv.player_name) THEN 1 ELSE 0 END as exact
ORDER BY exact DESC
WITH pv, collect(p)[0] as best_match
WHERE best_match IS NOT NULL
MERGE (best_match)-[:HAS_PIHS_VALUE]->(pv)
RETURN count(*) as newly_linked
```

## Rookie Handling

Rookies may not exist in database until draft:

1. **Pre-draft**: Create PIHSValue without Player link
2. **Post-draft**: Run reconciliation to link
3. **Devy**: May never link if college players only

### Rookie Detection

```python
def is_likely_rookie(player_name: str, chart_date: str) -> bool:
    """Check if player is likely a rookie/devy."""
    # Query database for player
    result = query_player(player_name)

    if not result:
        # Not in database - might be rookie
        month = int(chart_date[5:7])
        # Pre-season (before September) rookies may not be loaded
        return month < 9

    return False
```

## Team Abbreviation Mapping

Normalize team abbreviations:

```python
TEAM_NORMALIZATION = {
    # Common variations
    'LA': 'LAR',      # Los Angeles Rams
    'JAC': 'JAX',     # Jacksonville
    'WSH': 'WAS',     # Washington
    'GBP': 'GB',      # Green Bay
    'SFO': 'SF',      # San Francisco
    'TBB': 'TB',      # Tampa Bay
    'NOR': 'NO',      # New Orleans
    'NEP': 'NE',      # New England
    'LVR': 'LV',      # Las Vegas

    # Historical
    'OAK': 'LV',      # Oakland -> Las Vegas
    'SD': 'LAC',      # San Diego -> LA Chargers
    'STL': 'LAR',     # St. Louis -> LA Rams
}
```

## Validation Checks

After loading, run validation:

```cypher
// Check match rate
MATCH (pv:PIHSValue)
WHERE pv.chart_date = date('2025-12-20')
OPTIONAL MATCH (p:Player)-[:HAS_PIHS_VALUE]->(pv)
RETURN
  count(pv) as total_pihs,
  count(p) as linked,
  toFloat(count(p)) / count(pv) as match_rate

// Find position mismatches
MATCH (p:Player)-[:HAS_PIHS_VALUE]->(pv:PIHSValue)
WHERE p.position <> pv.position
RETURN p.name, p.position as player_pos, pv.position as pihs_pos
```
