# Fantasy Football Playoff Structure and Labeling

This document details the playoff bracket structure and database labeling scheme for all seasons.

## Database Schema

The `matchups` table contains two key fields for identifying playoff games:

- **`bracket_type`**: Identifies which playoff bracket the game belongs to
- **`round`**: Identifies the specific round or placement game

## Bracket Type Labels

| Label | Description |
|-------|-------------|
| `Championship` | Winner's bracket games (top playoff bracket, competing for 1st-2nd place) |
| `Winner's Consolation` | Winner's consolation bracket games (teams eliminated from championship, typically competing for 3rd-6th place) |
| `Consolation` | Consolation bracket/ladder games (lower bracket, typically 7th-10th or lower placement) |
| `Toilet Bowl` | Last place bracket (used in some seasons, e.g., 2025) |

## Round Labels

| Label | Description | Usage |
|-------|-------------|-------|
| `Round 1` | First week of playoffs | All brackets - initial playoff matchups |
| `Round 2` | Second week of playoffs | All brackets - second round matchups |
| `Round 3` | Third week of playoffs | All brackets - final round matchups |
| `Championship` | Championship game | Final game for 1st place |
| `3rd Place` | 3rd place game | Winner's Consolation final |
| `5th Place` | 5th place game | Winner's Consolation placement |
| `7th Place` | 7th place game | Consolation bracket placement |
| `8th Place` | 8th place game | Consolation bracket placement |
| `10th Place` | 10th place game | Consolation/Toilet Bowl placement |

## Regular Season vs Playoff Weeks by Season

### 2019
- **Regular Season:** Weeks 1-13
- **Playoff Weeks:** 14-17 (two-week playoff rounds)
  - Round 1: Weeks 14-15
  - Round 2 (Finals): Weeks 16-17

### 2020
- **Regular Season:** Weeks 1-13
- **Playoff Weeks:** 14-16
  - Round 1: Week 14
  - Round 2: Week 15
  - Round 3 (Finals): Week 16

### 2021-2025
- **Regular Season:** Weeks 1-14
- **Playoff Weeks:** 15-17
  - Round 1: Week 15
  - Round 2: Week 16
  - Round 3 (Finals): Week 17

## Detailed Playoff Brackets by Season

### 2019 Playoffs

**Round 1 (Weeks 14-15)**
- **Championship Bracket:**
  - Atul vs Pranesh
  - Vinay vs Varun
- **Consolation:**
  - Aditya vs Saket

**Round 2 (Weeks 16-17)**
- **Championship Bracket:**
  - Vinay vs Pranesh (Championship game)
- **Winner's Consolation:**
  - Atul vs Varun (3rd place game)
- **Consolation:**
  - Aditya vs Saket

---

### 2020 Playoffs

**Round 1 (Week 14)**
- **Championship Bracket:**
  - Pranesh vs Atul
  - Rohit, Ved vs Saket
- **Consolation:**
  - Varun vs Vinay

**Round 2 (Week 15)**
- **Championship Bracket:**
  - Atul vs Kushagra
  - Rohit vs Aditya
- **Winner's Consolation:**
  - Pranesh vs Saket
- **Consolation:**
  - Varun vs Vinay

**Round 3 (Week 16)**
- **Championship Bracket:**
  - Rohit, Ved vs Atul (Championship game)
- **Winner's Consolation:**
  - Pranesh vs Saket
  - Aditya vs Kushagra
- **Consolation:**
  - Varun vs Vinay

---

### 2021 Playoffs

**Round 1 (Week 15)**
- **Championship Bracket:**
  - Mihir vs Pranesh
  - Aditya vs Varun
- **Consolation:**
  - Vinay vs Rohit, Ved

**Round 2 (Week 16)**
- **Championship Bracket:**
  - Aditya vs Kushagra
  - Mihir vs Atul
- **Winner's Consolation:**
  - Varun vs Pranesh
- **Consolation:**
  - Vinay vs Rohit, Ved

**Round 3 (Week 17)**
- **Championship Bracket:**
  - Aditya vs Atul (Championship game)
- **Winner's Consolation:**
  - Varun vs Pranesh (3rd place game)
  - Mihir vs Kushagra (5th place game)
- **Consolation:**
  - Vinay vs Rohit, Ved

---

### 2022 Playoffs

**Round 1 (Week 15)**
- **Championship Bracket:**
  - Saket vs Pranesh
  - Ved vs Vinay
- **Consolation:**
  - Aditya vs Mihir
  - Kushagra vs Rohit

**Round 2 (Week 16)**
- **Championship Bracket:**
  - Saket vs Varun
  - Vinay vs Atul
- **Winner's Consolation:**
  - Ved vs Pranesh
- **Consolation:**
  - Rohit vs Mihir
  - Kushagra vs Aditya

**Round 3 (Week 17)**
- **Championship Bracket:**
  - Saket vs Vinay (Championship game)
- **Winner's Consolation:**
  - Ved vs Pranesh (3rd place game)
  - Atul vs Varun (5th place game)
- **Consolation:**
  - Mihir vs Kushagra (7th place game)
  - Rohit vs Aditya (8th place game)

---

### 2023 Playoffs

**Round 1 (Week 15)**
- **Championship Bracket:**
  - Pranesh vs Varun
  - Aditya vs Rohit
- **Consolation:**
  - Vinay vs Atul
  - Mihir vs Ved

**Round 2 (Week 16)**
- **Championship Bracket:**
  - Pranesh vs Saket
  - Aditya vs Kushagra
- **Winner's Consolation:**
  - Rohit vs Varun
- **Consolation:**
  - Mihir vs Atul
  - Ved vs Vinay

**Round 3 (Week 17)**
- **Championship Bracket:**
  - Pranesh vs Kushagra (Championship game)
- **Winner's Consolation:**
  - Aditya vs Saket (3rd place game)
  - Rohit vs Varun (5th place game)
- **Consolation:**
  - Vinay vs Atul (7th place game)
  - Mihir vs Ved (8th place game)

---

### 2024 Playoffs

**Round 1 (Week 15)**
- **Championship Bracket:**
  - Kushagra vs Saket
  - Mihir vs Aditya
- **Consolation:**
  - Varun vs Pranesh
  - Rohit vs Ved

**Round 2 (Week 16)**
- **Championship Bracket:**
  - Saket vs Atul
  - Mihir vs Vinay
- **Winner's Consolation:**
  - Kushagra vs Aditya
- **Consolation:**
  - Pranesh vs Ved
  - Varun vs Rohit

**Round 3 (Week 17)**
- **Championship Bracket:**
  - Vinay vs Atul (Championship game)
- **Winner's Consolation:**
  - Mihir vs Saket (3rd place game)
  - Kushagra vs Aditya (5th place game)
- **Consolation:**
  - Varun vs Pranesh (7th place game)
  - Rohit vs Ved (8th place game)

---

### 2025 Playoffs

**Round 1 (Week 15)**
- **Championship Bracket:**
  - Pranesh vs Vinay
  - Varun vs Atul
- **Toilet Bowl:**
  - Jacob vs Aditya
  - Rohit vs Mihir

**Round 2 (Week 16)**
- **Championship Bracket:**
  - George vs Pranesh
  - Kushagra vs Atul
- **Winner's Consolation:**
  - Vinay vs Varun (5th place game)
- **Consolation:**
  - Ved vs Jacob
  - Sohan vs Mihir
  - Aditya vs Rohit (8th place game)

**Round 3 (Week 17)**
- **Championship Bracket:**
  - Kushagra vs Pranesh (Championship game)
- **Winner's Consolation:**
  - Atul vs George (3rd place game)
- **Consolation:**
  - Ved vs Mihir (7th place game)
  - Jacob vs Sohan (10th place game)

---

## Notes

- **Co-owned teams:** "Rohit, Ved" refers to co-owned teams by Rohit Iyer and VED ANUMALA
  - 2020: "The Bay Area Gods"
  - 2021: "Iyerland And a Ved"
- **Two-week playoff rounds:** The 2019 season used two-week cumulative scoring for playoff rounds
- **Bracket evolution:** The league standardized on a 14-week regular season with 3-week playoffs starting in 2021
- **Toilet Bowl:** First introduced in 2025 for last-place teams

## Database Update Status

- ✅ Regular season vs playoff weeks identified
- ⏳ bracket_type and round labels pending population
- ⏳ Historical playoff data (2019-2024) needs backfill
