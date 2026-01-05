-- Playoff Bracket Label Updates for Fantasy Football Database
-- This script populates bracket_type and round columns for all playoff matchups

BEGIN TRANSACTION;

-- ============================================================================
-- 2019 SEASON PLAYOFFS (Weeks 14-17, two-week rounds)
-- ============================================================================

-- 2019 Round 1 (Weeks 14-15) - Championship Bracket
UPDATE matchups SET bracket_type = 'Championship', round = 'Round 1'
WHERE season_year = 2019 AND week IN (14, 15)
AND ((home_team LIKE '%Atul%' OR away_team LIKE '%Atul%') AND (home_team LIKE '%Pranesh%' OR away_team LIKE '%Pranesh%'))
OR ((home_team LIKE '%Vinay%' OR away_team LIKE '%Vinay%') AND (home_team LIKE '%Varun%' OR away_team LIKE '%Varun%'));

-- 2019 Round 1 (Weeks 14-15) - Consolation
UPDATE matchups SET bracket_type = 'Consolation', round = 'Round 1'
WHERE season_year = 2019 AND week IN (14, 15)
AND ((home_team LIKE '%Aditya%' OR away_team LIKE '%Aditya%') AND (home_team LIKE '%Saket%' OR away_team LIKE '%Saket%'));

-- 2019 Round 2 (Weeks 16-17) - Championship
UPDATE matchups SET bracket_type = 'Championship', round = 'Championship'
WHERE season_year = 2019 AND week IN (16, 17)
AND ((home_team LIKE '%Vinay%' OR away_team LIKE '%Vinay%') AND (home_team LIKE '%Pranesh%' OR away_team LIKE '%Pranesh%'));

-- 2019 Round 2 (Weeks 16-17) - Winner's Consolation (3rd place)
UPDATE matchups SET bracket_type = 'Winner''s Consolation', round = '3rd Place'
WHERE season_year = 2019 AND week IN (16, 17)
AND ((home_team LIKE '%Atul%' OR away_team LIKE '%Atul%') AND (home_team LIKE '%Varun%' OR away_team LIKE '%Varun%'));

-- 2019 Round 2 (Weeks 16-17) - Consolation
UPDATE matchups SET bracket_type = 'Consolation', round = 'Round 2'
WHERE season_year = 2019 AND week IN (16, 17)
AND ((home_team LIKE '%Aditya%' OR away_team LIKE '%Aditya%') AND (home_team LIKE '%Saket%' OR away_team LIKE '%Saket%'));

-- ============================================================================
-- 2020 SEASON PLAYOFFS (Weeks 14-16)
-- ============================================================================

-- 2020 Round 1 (Week 14) - Championship Bracket
UPDATE matchups SET bracket_type = 'Championship', round = 'Round 1'
WHERE season_year = 2020 AND week = 14
AND (
    ((home_team LIKE '%Pranesh%' OR away_team LIKE '%Pranesh%') AND (home_team LIKE '%Atul%' OR away_team LIKE '%Atul%'))
    OR ((home_team LIKE '%Rohit%' OR home_team LIKE '%Ved%' OR home_team LIKE '%Bay Area%' OR home_team LIKE '%Iyerland%'
         OR away_team LIKE '%Rohit%' OR away_team LIKE '%Ved%' OR away_team LIKE '%Bay Area%' OR away_team LIKE '%Iyerland%')
        AND (home_team LIKE '%Saket%' OR away_team LIKE '%Saket%'))
);

-- 2020 Round 1 (Week 14) - Consolation
UPDATE matchups SET bracket_type = 'Consolation', round = 'Round 1'
WHERE season_year = 2020 AND week = 14
AND ((home_team LIKE '%Varun%' OR away_team LIKE '%Varun%') AND (home_team LIKE '%Vinay%' OR away_team LIKE '%Vinay%'));

-- 2020 Round 2 (Week 15) - Championship Bracket
UPDATE matchups SET bracket_type = 'Championship', round = 'Round 2'
WHERE season_year = 2020 AND week = 15
AND (
    ((home_team LIKE '%Atul%' OR away_team LIKE '%Atul%') AND (home_team LIKE '%Kush%' OR away_team LIKE '%Kush%'))
    OR ((home_team LIKE '%Rohit%' OR home_team LIKE '%Ved%' OR home_team LIKE '%Bay Area%' OR home_team LIKE '%Iyerland%'
         OR away_team LIKE '%Rohit%' OR away_team LIKE '%Ved%' OR away_team LIKE '%Bay Area%' OR away_team LIKE '%Iyerland%')
        AND (home_team LIKE '%Aditya%' OR away_team LIKE '%Aditya%'))
);

-- 2020 Round 2 (Week 15) - Winner's Consolation
UPDATE matchups SET bracket_type = 'Winner''s Consolation', round = 'Round 2'
WHERE season_year = 2020 AND week = 15
AND ((home_team LIKE '%Pranesh%' OR away_team LIKE '%Pranesh%') AND (home_team LIKE '%Saket%' OR away_team LIKE '%Saket%'));

-- 2020 Round 2 (Week 15) - Consolation
UPDATE matchups SET bracket_type = 'Consolation', round = 'Round 2'
WHERE season_year = 2020 AND week = 15
AND ((home_team LIKE '%Varun%' OR away_team LIKE '%Varun%') AND (home_team LIKE '%Vinay%' OR away_team LIKE '%Vinay%'));

-- 2020 Round 3 (Week 16) - Championship
UPDATE matchups SET bracket_type = 'Championship', round = 'Championship'
WHERE season_year = 2020 AND week = 16
AND ((home_team LIKE '%Rohit%' OR home_team LIKE '%Ved%' OR home_team LIKE '%Bay Area%' OR home_team LIKE '%Iyerland%'
      OR away_team LIKE '%Rohit%' OR away_team LIKE '%Ved%' OR away_team LIKE '%Bay Area%' OR away_team LIKE '%Iyerland%')
     AND (home_team LIKE '%Atul%' OR away_team LIKE '%Atul%'));

-- 2020 Round 3 (Week 16) - Winner's Consolation
UPDATE matchups SET bracket_type = 'Winner''s Consolation', round = 'Round 3'
WHERE season_year = 2020 AND week = 16
AND (
    ((home_team LIKE '%Pranesh%' OR away_team LIKE '%Pranesh%') AND (home_team LIKE '%Saket%' OR away_team LIKE '%Saket%'))
    OR ((home_team LIKE '%Aditya%' OR away_team LIKE '%Aditya%') AND (home_team LIKE '%Kush%' OR away_team LIKE '%Kush%'))
);

-- 2020 Round 3 (Week 16) - Consolation
UPDATE matchups SET bracket_type = 'Consolation', round = 'Round 3'
WHERE season_year = 2020 AND week = 16
AND ((home_team LIKE '%Varun%' OR away_team LIKE '%Varun%') AND (home_team LIKE '%Vinay%' OR away_team LIKE '%Vinay%'));

-- ============================================================================
-- 2021 SEASON PLAYOFFS (Weeks 15-17)
-- ============================================================================

-- 2021 Round 1 (Week 15) - Championship Bracket
UPDATE matchups SET bracket_type = 'Championship', round = 'Round 1'
WHERE season_year = 2021 AND week = 15
AND (
    ((home_team LIKE '%Mihir%' OR away_team LIKE '%Mihir%') AND (home_team LIKE '%Pranesh%' OR away_team LIKE '%Pranesh%'))
    OR ((home_team LIKE '%Aditya%' OR away_team LIKE '%Aditya%') AND (home_team LIKE '%Varun%' OR away_team LIKE '%Varun%'))
);

-- 2021 Round 1 (Week 15) - Consolation
UPDATE matchups SET bracket_type = 'Consolation', round = 'Round 1'
WHERE season_year = 2021 AND week = 15
AND ((home_team LIKE '%Vinay%' OR away_team LIKE '%Vinay%')
     AND (home_team LIKE '%Rohit%' OR home_team LIKE '%Ved%' OR home_team LIKE '%Bay Area%' OR home_team LIKE '%Iyerland%'
          OR away_team LIKE '%Rohit%' OR away_team LIKE '%Ved%' OR away_team LIKE '%Bay Area%' OR away_team LIKE '%Iyerland%'));

-- 2021 Round 2 (Week 16) - Championship Bracket
UPDATE matchups SET bracket_type = 'Championship', round = 'Round 2'
WHERE season_year = 2021 AND week = 16
AND (
    ((home_team LIKE '%Aditya%' OR away_team LIKE '%Aditya%') AND (home_team LIKE '%Kush%' OR away_team LIKE '%Kush%'))
    OR ((home_team LIKE '%Mihir%' OR away_team LIKE '%Mihir%') AND (home_team LIKE '%Atul%' OR away_team LIKE '%Atul%'))
);

-- 2021 Round 2 (Week 16) - Winner's Consolation
UPDATE matchups SET bracket_type = 'Winner''s Consolation', round = 'Round 2'
WHERE season_year = 2021 AND week = 16
AND ((home_team LIKE '%Varun%' OR away_team LIKE '%Varun%') AND (home_team LIKE '%Pranesh%' OR away_team LIKE '%Pranesh%'));

-- 2021 Round 2 (Week 16) - Consolation
UPDATE matchups SET bracket_type = 'Consolation', round = 'Round 2'
WHERE season_year = 2021 AND week = 16
AND ((home_team LIKE '%Vinay%' OR away_team LIKE '%Vinay%')
     AND (home_team LIKE '%Rohit%' OR home_team LIKE '%Ved%' OR home_team LIKE '%Bay Area%' OR home_team LIKE '%Iyerland%'
          OR away_team LIKE '%Rohit%' OR away_team LIKE '%Ved%' OR away_team LIKE '%Bay Area%' OR away_team LIKE '%Iyerland%'));

-- 2021 Round 3 (Week 17) - Championship
UPDATE matchups SET bracket_type = 'Championship', round = 'Championship'
WHERE season_year = 2021 AND week = 17
AND ((home_team LIKE '%Aditya%' OR away_team LIKE '%Aditya%') AND (home_team LIKE '%Atul%' OR away_team LIKE '%Atul%'));

-- 2021 Round 3 (Week 17) - Winner's Consolation
UPDATE matchups SET bracket_type = 'Winner''s Consolation', round = '3rd Place'
WHERE season_year = 2021 AND week = 17
AND ((home_team LIKE '%Varun%' OR away_team LIKE '%Varun%') AND (home_team LIKE '%Pranesh%' OR away_team LIKE '%Pranesh%'));

UPDATE matchups SET bracket_type = 'Winner''s Consolation', round = '5th Place'
WHERE season_year = 2021 AND week = 17
AND ((home_team LIKE '%Mihir%' OR away_team LIKE '%Mihir%') AND (home_team LIKE '%Kush%' OR away_team LIKE '%Kush%'));

-- 2021 Round 3 (Week 17) - Consolation
UPDATE matchups SET bracket_type = 'Consolation', round = 'Round 3'
WHERE season_year = 2021 AND week = 17
AND ((home_team LIKE '%Vinay%' OR away_team LIKE '%Vinay%')
     AND (home_team LIKE '%Rohit%' OR home_team LIKE '%Ved%' OR home_team LIKE '%Bay Area%' OR home_team LIKE '%Iyerland%'
          OR away_team LIKE '%Rohit%' OR away_team LIKE '%Ved%' OR away_team LIKE '%Bay Area%' OR away_team LIKE '%Iyerland%'));

-- ============================================================================
-- 2022 SEASON PLAYOFFS (Weeks 15-17)
-- ============================================================================

-- 2022 Round 1 (Week 15) - Championship Bracket
UPDATE matchups SET bracket_type = 'Championship', round = 'Round 1'
WHERE season_year = 2022 AND week = 15
AND (
    ((home_team LIKE '%Saket%' OR away_team LIKE '%Saket%') AND (home_team LIKE '%Pranesh%' OR away_team LIKE '%Pranesh%'))
    OR ((home_team LIKE '%Ved%' OR away_team LIKE '%Ved%') AND (home_team LIKE '%Vinay%' OR away_team LIKE '%Vinay%'))
);

-- 2022 Round 1 (Week 15) - Consolation
UPDATE matchups SET bracket_type = 'Consolation', round = 'Round 1'
WHERE season_year = 2022 AND week = 15
AND (
    ((home_team LIKE '%Aditya%' OR away_team LIKE '%Aditya%') AND (home_team LIKE '%Mihir%' OR away_team LIKE '%Mihir%'))
    OR ((home_team LIKE '%Kush%' OR away_team LIKE '%Kush%') AND (home_team LIKE '%Rohit%' OR away_team LIKE '%Rohit%'))
);

-- 2022 Round 2 (Week 16) - Championship Bracket
UPDATE matchups SET bracket_type = 'Championship', round = 'Round 2'
WHERE season_year = 2022 AND week = 16
AND (
    ((home_team LIKE '%Saket%' OR away_team LIKE '%Saket%') AND (home_team LIKE '%Varun%' OR away_team LIKE '%Varun%'))
    OR ((home_team LIKE '%Vinay%' OR away_team LIKE '%Vinay%') AND (home_team LIKE '%Atul%' OR away_team LIKE '%Atul%'))
);

-- 2022 Round 2 (Week 16) - Winner's Consolation
UPDATE matchups SET bracket_type = 'Winner''s Consolation', round = 'Round 2'
WHERE season_year = 2022 AND week = 16
AND ((home_team LIKE '%Ved%' OR away_team LIKE '%Ved%') AND (home_team LIKE '%Pranesh%' OR away_team LIKE '%Pranesh%'));

-- 2022 Round 2 (Week 16) - Consolation
UPDATE matchups SET bracket_type = 'Consolation', round = 'Round 2'
WHERE season_year = 2022 AND week = 16
AND (
    ((home_team LIKE '%Rohit%' OR away_team LIKE '%Rohit%') AND (home_team LIKE '%Mihir%' OR away_team LIKE '%Mihir%'))
    OR ((home_team LIKE '%Kush%' OR away_team LIKE '%Kush%') AND (home_team LIKE '%Aditya%' OR away_team LIKE '%Aditya%'))
);

-- 2022 Round 3 (Week 17) - Championship
UPDATE matchups SET bracket_type = 'Championship', round = 'Championship'
WHERE season_year = 2022 AND week = 17
AND ((home_team LIKE '%Saket%' OR away_team LIKE '%Saket%') AND (home_team LIKE '%Vinay%' OR away_team LIKE '%Vinay%'));

-- 2022 Round 3 (Week 17) - Winner's Consolation
UPDATE matchups SET bracket_type = 'Winner''s Consolation', round = '3rd Place'
WHERE season_year = 2022 AND week = 17
AND ((home_team LIKE '%Ved%' OR away_team LIKE '%Ved%') AND (home_team LIKE '%Pranesh%' OR away_team LIKE '%Pranesh%'));

UPDATE matchups SET bracket_type = 'Winner''s Consolation', round = '5th Place'
WHERE season_year = 2022 AND week = 17
AND ((home_team LIKE '%Atul%' OR away_team LIKE '%Atul%') AND (home_team LIKE '%Varun%' OR away_team LIKE '%Varun%'));

-- 2022 Round 3 (Week 17) - Consolation
UPDATE matchups SET bracket_type = 'Consolation', round = '7th Place'
WHERE season_year = 2022 AND week = 17
AND ((home_team LIKE '%Mihir%' OR away_team LIKE '%Mihir%') AND (home_team LIKE '%Kush%' OR away_team LIKE '%Kush%'));

UPDATE matchups SET bracket_type = 'Consolation', round = '8th Place'
WHERE season_year = 2022 AND week = 17
AND ((home_team LIKE '%Rohit%' OR away_team LIKE '%Rohit%') AND (home_team LIKE '%Aditya%' OR away_team LIKE '%Aditya%'));

-- ============================================================================
-- 2023 SEASON PLAYOFFS (Weeks 15-17)
-- ============================================================================

-- 2023 Round 1 (Week 15) - Championship Bracket
UPDATE matchups SET bracket_type = 'Championship', round = 'Round 1'
WHERE season_year = 2023 AND week = 15
AND (
    ((home_team LIKE '%Pranesh%' OR away_team LIKE '%Pranesh%') AND (home_team LIKE '%Varun%' OR away_team LIKE '%Varun%'))
    OR ((home_team LIKE '%Aditya%' OR away_team LIKE '%Aditya%') AND (home_team LIKE '%Rohit%' OR away_team LIKE '%Rohit%'))
);

-- 2023 Round 1 (Week 15) - Consolation
UPDATE matchups SET bracket_type = 'Consolation', round = 'Round 1'
WHERE season_year = 2023 AND week = 15
AND (
    ((home_team LIKE '%Vinay%' OR away_team LIKE '%Vinay%') AND (home_team LIKE '%Atul%' OR away_team LIKE '%Atul%'))
    OR ((home_team LIKE '%Mihir%' OR away_team LIKE '%Mihir%') AND (home_team LIKE '%Ved%' OR away_team LIKE '%Ved%'))
);

-- 2023 Round 2 (Week 16) - Championship Bracket
UPDATE matchups SET bracket_type = 'Championship', round = 'Round 2'
WHERE season_year = 2023 AND week = 16
AND (
    ((home_team LIKE '%Pranesh%' OR away_team LIKE '%Pranesh%') AND (home_team LIKE '%Saket%' OR away_team LIKE '%Saket%'))
    OR ((home_team LIKE '%Aditya%' OR away_team LIKE '%Aditya%') AND (home_team LIKE '%Kush%' OR away_team LIKE '%Kush%'))
);

-- 2023 Round 2 (Week 16) - Winner's Consolation
UPDATE matchups SET bracket_type = 'Winner''s Consolation', round = 'Round 2'
WHERE season_year = 2023 AND week = 16
AND ((home_team LIKE '%Rohit%' OR away_team LIKE '%Rohit%') AND (home_team LIKE '%Varun%' OR away_team LIKE '%Varun%'));

-- 2023 Round 2 (Week 16) - Consolation
UPDATE matchups SET bracket_type = 'Consolation', round = 'Round 2'
WHERE season_year = 2023 AND week = 16
AND (
    ((home_team LIKE '%Mihir%' OR away_team LIKE '%Mihir%') AND (home_team LIKE '%Atul%' OR away_team LIKE '%Atul%'))
    OR ((home_team LIKE '%Ved%' OR away_team LIKE '%Ved%') AND (home_team LIKE '%Vinay%' OR away_team LIKE '%Vinay%'))
);

-- 2023 Round 3 (Week 17) - Championship
UPDATE matchups SET bracket_type = 'Championship', round = 'Championship'
WHERE season_year = 2023 AND week = 17
AND ((home_team LIKE '%Pranesh%' OR away_team LIKE '%Pranesh%') AND (home_team LIKE '%Kush%' OR away_team LIKE '%Kush%'));

-- 2023 Round 3 (Week 17) - Winner's Consolation
UPDATE matchups SET bracket_type = 'Winner''s Consolation', round = '3rd Place'
WHERE season_year = 2023 AND week = 17
AND ((home_team LIKE '%Aditya%' OR away_team LIKE '%Aditya%') AND (home_team LIKE '%Saket%' OR away_team LIKE '%Saket%'));

UPDATE matchups SET bracket_type = 'Winner''s Consolation', round = '5th Place'
WHERE season_year = 2023 AND week = 17
AND ((home_team LIKE '%Rohit%' OR away_team LIKE '%Rohit%') AND (home_team LIKE '%Varun%' OR away_team LIKE '%Varun%'));

-- 2023 Round 3 (Week 17) - Consolation
UPDATE matchups SET bracket_type = 'Consolation', round = '7th Place'
WHERE season_year = 2023 AND week = 17
AND ((home_team LIKE '%Vinay%' OR away_team LIKE '%Vinay%') AND (home_team LIKE '%Atul%' OR away_team LIKE '%Atul%'));

UPDATE matchups SET bracket_type = 'Consolation', round = '8th Place'
WHERE season_year = 2023 AND week = 17
AND ((home_team LIKE '%Mihir%' OR away_team LIKE '%Mihir%') AND (home_team LIKE '%Ved%' OR away_team LIKE '%Ved%'));

-- ============================================================================
-- 2024 SEASON PLAYOFFS (Weeks 15-17)
-- ============================================================================

-- 2024 Round 1 (Week 15) - Championship Bracket
UPDATE matchups SET bracket_type = 'Championship', round = 'Round 1'
WHERE season_year = 2024 AND week = 15
AND (
    ((home_team LIKE '%Kush%' OR away_team LIKE '%Kush%') AND (home_team LIKE '%Saket%' OR away_team LIKE '%Saket%'))
    OR ((home_team LIKE '%Mihir%' OR away_team LIKE '%Mihir%') AND (home_team LIKE '%Aditya%' OR away_team LIKE '%Aditya%'))
);

-- 2024 Round 1 (Week 15) - Consolation
UPDATE matchups SET bracket_type = 'Consolation', round = 'Round 1'
WHERE season_year = 2024 AND week = 15
AND (
    ((home_team LIKE '%Varun%' OR away_team LIKE '%Varun%') AND (home_team LIKE '%Pranesh%' OR away_team LIKE '%Pranesh%'))
    OR ((home_team LIKE '%Rohit%' OR away_team LIKE '%Rohit%') AND (home_team LIKE '%Ved%' OR away_team LIKE '%Ved%'))
);

-- 2024 Round 2 (Week 16) - Championship Bracket
UPDATE matchups SET bracket_type = 'Championship', round = 'Round 2'
WHERE season_year = 2024 AND week = 16
AND (
    ((home_team LIKE '%Saket%' OR away_team LIKE '%Saket%') AND (home_team LIKE '%Atul%' OR away_team LIKE '%Atul%'))
    OR ((home_team LIKE '%Mihir%' OR away_team LIKE '%Mihir%') AND (home_team LIKE '%Vinay%' OR away_team LIKE '%Vinay%'))
);

-- 2024 Round 2 (Week 16) - Winner's Consolation
UPDATE matchups SET bracket_type = 'Winner''s Consolation', round = 'Round 2'
WHERE season_year = 2024 AND week = 16
AND ((home_team LIKE '%Kush%' OR away_team LIKE '%Kush%') AND (home_team LIKE '%Aditya%' OR away_team LIKE '%Aditya%'));

-- 2024 Round 2 (Week 16) - Consolation
UPDATE matchups SET bracket_type = 'Consolation', round = 'Round 2'
WHERE season_year = 2024 AND week = 16
AND (
    ((home_team LIKE '%Pranesh%' OR away_team LIKE '%Pranesh%') AND (home_team LIKE '%Ved%' OR away_team LIKE '%Ved%'))
    OR ((home_team LIKE '%Varun%' OR away_team LIKE '%Varun%') AND (home_team LIKE '%Rohit%' OR away_team LIKE '%Rohit%'))
);

-- 2024 Round 3 (Week 17) - Championship
UPDATE matchups SET bracket_type = 'Championship', round = 'Championship'
WHERE season_year = 2024 AND week = 17
AND ((home_team LIKE '%Vinay%' OR away_team LIKE '%Vinay%') AND (home_team LIKE '%Atul%' OR away_team LIKE '%Atul%'));

-- 2024 Round 3 (Week 17) - Winner's Consolation
UPDATE matchups SET bracket_type = 'Winner''s Consolation', round = '3rd Place'
WHERE season_year = 2024 AND week = 17
AND ((home_team LIKE '%Mihir%' OR away_team LIKE '%Mihir%') AND (home_team LIKE '%Saket%' OR away_team LIKE '%Saket%'));

UPDATE matchups SET bracket_type = 'Winner''s Consolation', round = '5th Place'
WHERE season_year = 2024 AND week = 17
AND ((home_team LIKE '%Kush%' OR away_team LIKE '%Kush%') AND (home_team LIKE '%Aditya%' OR away_team LIKE '%Aditya%'));

-- 2024 Round 3 (Week 17) - Consolation
UPDATE matchups SET bracket_type = 'Consolation', round = '7th Place'
WHERE season_year = 2024 AND week = 17
AND ((home_team LIKE '%Varun%' OR away_team LIKE '%Varun%') AND (home_team LIKE '%Pranesh%' OR away_team LIKE '%Pranesh%'));

UPDATE matchups SET bracket_type = 'Consolation', round = '8th Place'
WHERE season_year = 2024 AND week = 17
AND ((home_team LIKE '%Rohit%' OR away_team LIKE '%Rohit%') AND (home_team LIKE '%Ved%' OR away_team LIKE '%Ved%'));

-- ============================================================================
-- 2025 SEASON PLAYOFFS (Weeks 15-17)
-- ============================================================================

-- 2025 Round 1 (Week 15) - Championship Bracket
UPDATE matchups SET bracket_type = 'Championship', round = 'Round 1'
WHERE season_year = 2025 AND week = 15
AND (
    ((home_team LIKE '%Pranesh%' OR away_team LIKE '%Pranesh%') AND (home_team LIKE '%Vinay%' OR away_team LIKE '%Vinay%'))
    OR ((home_team LIKE '%Varun%' OR away_team LIKE '%Varun%') AND (home_team LIKE '%Atul%' OR away_team LIKE '%Atul%'))
);

-- 2025 Round 1 (Week 15) - Toilet Bowl
UPDATE matchups SET bracket_type = 'Toilet Bowl', round = 'Round 1'
WHERE season_year = 2025 AND week = 15
AND (
    ((home_team LIKE '%Jacob%' OR away_team LIKE '%Jacob%') AND (home_team LIKE '%Aditya%' OR away_team LIKE '%Aditya%'))
    OR ((home_team LIKE '%Rohit%' OR away_team LIKE '%Rohit%') AND (home_team LIKE '%Mihir%' OR away_team LIKE '%Mihir%'))
);

-- 2025 Round 2 (Week 16) - Championship Bracket
UPDATE matchups SET bracket_type = 'Championship', round = 'Round 2'
WHERE season_year = 2025 AND week = 16
AND (
    ((home_team LIKE '%George%' OR away_team LIKE '%George%') AND (home_team LIKE '%Pranesh%' OR away_team LIKE '%Pranesh%'))
    OR ((home_team LIKE '%Kush%' OR away_team LIKE '%Kush%') AND (home_team LIKE '%Atul%' OR away_team LIKE '%Atul%'))
);

-- 2025 Round 2 (Week 16) - Winner's Consolation (5th place)
UPDATE matchups SET bracket_type = 'Winner''s Consolation', round = '5th Place'
WHERE season_year = 2025 AND week = 16
AND ((home_team LIKE '%Vinay%' OR away_team LIKE '%Vinay%') AND (home_team LIKE '%Varun%' OR away_team LIKE '%Varun%'));

-- 2025 Round 2 (Week 16) - Consolation
UPDATE matchups SET bracket_type = 'Consolation', round = 'Round 2'
WHERE season_year = 2025 AND week = 16
AND (
    ((home_team LIKE '%Ved%' OR away_team LIKE '%Ved%') AND (home_team LIKE '%Jacob%' OR away_team LIKE '%Jacob%'))
    OR ((home_team LIKE '%Sohan%' OR away_team LIKE '%Sohan%') AND (home_team LIKE '%Mihir%' OR away_team LIKE '%Mihir%'))
);

-- 2025 Round 2 (Week 16) - 8th Place
UPDATE matchups SET bracket_type = 'Consolation', round = '8th Place'
WHERE season_year = 2025 AND week = 16
AND ((home_team LIKE '%Aditya%' OR away_team LIKE '%Aditya%') AND (home_team LIKE '%Rohit%' OR away_team LIKE '%Rohit%'));

-- 2025 Round 3 (Week 17) - Championship
UPDATE matchups SET bracket_type = 'Championship', round = 'Championship'
WHERE season_year = 2025 AND week = 17
AND ((home_team LIKE '%Kush%' OR away_team LIKE '%Kush%') AND (home_team LIKE '%Pranesh%' OR away_team LIKE '%Pranesh%'));

-- 2025 Round 3 (Week 17) - Winner's Consolation (3rd place)
UPDATE matchups SET bracket_type = 'Winner''s Consolation', round = '3rd Place'
WHERE season_year = 2025 AND week = 17
AND ((home_team LIKE '%Atul%' OR away_team LIKE '%Atul%') AND (home_team LIKE '%George%' OR away_team LIKE '%George%'));

-- 2025 Round 3 (Week 17) - Consolation (7th place)
UPDATE matchups SET bracket_type = 'Consolation', round = '7th Place'
WHERE season_year = 2025 AND week = 17
AND ((home_team LIKE '%Ved%' OR away_team LIKE '%Ved%') AND (home_team LIKE '%Mihir%' OR away_team LIKE '%Mihir%'));

-- 2025 Round 3 (Week 17) - 10th Place
UPDATE matchups SET bracket_type = 'Consolation', round = '10th Place'
WHERE season_year = 2025 AND week = 17
AND ((home_team LIKE '%Jacob%' OR away_team LIKE '%Jacob%') AND (home_team LIKE '%Sohan%' OR away_team LIKE '%Sohan%'));

COMMIT;
