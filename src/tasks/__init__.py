"""
Data layer — Tempo Music Streaming Analytics database, schema, seed data, and 15 questions.
Expected answers are pre-computed at module load by running reference SQL.
"""
import sqlite3
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Database Schema
# ---------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE artists (
    id                INTEGER PRIMARY KEY,
    name              TEXT    NOT NULL,
    country           TEXT    NOT NULL,
    debut_year        INTEGER NOT NULL,
    monthly_listeners INTEGER NOT NULL,
    genre             TEXT    NOT NULL
);

CREATE TABLE songs (
    id            INTEGER PRIMARY KEY,
    title         TEXT    NOT NULL,
    artist_id     INTEGER NOT NULL,
    genre         TEXT    NOT NULL,
    bpm           INTEGER NOT NULL,
    mood          TEXT    NOT NULL,
    duration_sec  INTEGER NOT NULL,
    release_year  INTEGER NOT NULL,
    FOREIGN KEY (artist_id) REFERENCES artists(id)
);

CREATE TABLE users (
    id                INTEGER PRIMARY KEY,
    username          TEXT    NOT NULL,
    country           TEXT    NOT NULL,
    subscription_tier TEXT    NOT NULL,
    joined_year       INTEGER NOT NULL,
    age               INTEGER NOT NULL
);

CREATE TABLE streams (
    id             INTEGER PRIMARY KEY,
    user_id        INTEGER NOT NULL,
    song_id        INTEGER NOT NULL,
    played_at      TEXT    NOT NULL,
    completed      INTEGER NOT NULL,
    skipped_at_sec INTEGER,
    source         TEXT    NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (song_id) REFERENCES songs(id)
);

CREATE TABLE playlists (
    id         INTEGER PRIMARY KEY,
    name       TEXT    NOT NULL,
    user_id    INTEGER NOT NULL,
    is_public  INTEGER NOT NULL,
    created_at TEXT    NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE playlist_songs (
    playlist_id INTEGER NOT NULL,
    song_id     INTEGER NOT NULL,
    position    INTEGER NOT NULL,
    added_at    TEXT    NOT NULL,
    PRIMARY KEY (playlist_id, song_id),
    FOREIGN KEY (playlist_id) REFERENCES playlists(id),
    FOREIGN KEY (song_id)     REFERENCES songs(id)
);
"""

# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

SEED_ARTISTS = [
    (1,  "Nova Pulse",        "USA",     2015, 18200000, "Electronic"),
    (2,  "The Drift Kings",   "UK",      2011, 9500000,  "Indie Rock"),
    (3,  "Yuki Tanaka",       "Japan",   2018, 4300000,  "J-Pop"),
    (4,  "Cobre Vivo",        "Brazil",  2013, 7800000,  "Latin"),
    (5,  "Elara Moon",        "Canada",  2020, 11600000, "Pop"),
    (6,  "Static Wolves",     "Germany", 2009, 6200000,  "Metal"),
    (7,  "Priya Rajan",       "India",   2017, 5100000,  "Bollywood Fusion"),
    (8,  "Lost Meridian",     "USA",     2016, 3400000,  "Lo-fi Hip-hop"),
    (9,  "Zanele Dube",       "South Africa", 2019, 2900000, "Afrobeats"),
    (10, "Cosmo & The Void",  "Australia", 2014, 8700000, "Synth-pop"),
    (11, "Red Margin",        "France",  2012, 4600000,  "Jazz Fusion"),
    (12, "Hyperion",          "South Korea", 2021, 14500000, "K-Pop"),
    (13, "Dust Carnival",     "Mexico",  2010, 3200000,  "Alternative"),
    (14, "Sienna Blake",      "UK",      2022, 9100000,  "R&B"),
    (15, "The Neon Foxes",    "USA",     2018, 6800000,  "Indie Pop"),
    (16, "Vivienne Echo",    "UK",      2020, 7200000,  "Electropop"),
    (17, "Kartik Flow",      "India",   2018, 3800000,  "Hip-hop Fusion"),
    (18, "Boreal Sound",     "Norway",  2016, 5400000,  "Nordic Folk Electronic"),
    (19, "Cipher Collective","USA",     2019, 4100000,  "Experimental"),
    (20, "Mariana Voss",     "Brazil",  2021, 6600000,  "Pop"),
    (21, "Fractal Garden",   "Japan",   2017, 2800000,  "Ambient"),
    (22, "The Rust Belt",    "USA",     2013, 3500000,  "Indie Folk"),
    (23, "Lagos Phonk",      "Nigeria", 2022, 8900000,  "Afrobeats"),
    (24, "Aether Circuit",   "Germany", 2020, 5200000,  "Techno"),
    (25, "Chloe Winters",    "Canada",  2021, 10400000, "R&B Pop"),
]

SEED_SONGS = [
    # Nova Pulse (1) - Electronic
    (1,  "Pulse Override",       1, "Electronic",      128, "Energetic",  214, 2020),
    (2,  "Drift Vector",         1, "Electronic",      140, "Dark",       198, 2021),
    (3,  "Solaris Bloom",        1, "Electronic",      122, "Euphoric",   241, 2022),
    (4,  "Ghost Protocol",       1, "Electronic",      135, "Tense",      187, 2023),
    # The Drift Kings (2) - Indie Rock
    (5,  "Cardboard Cities",     2, "Indie Rock",       96, "Melancholy", 253, 2019),
    (6,  "Neon Bruise",          2, "Indie Rock",      104, "Angry",      228, 2021),
    (7,  "Atlas Shrug",          2, "Indie Rock",       88, "Wistful",    312, 2022),
    # Yuki Tanaka (3) - J-Pop
    (8,  "Sakura Glitch",        3, "J-Pop",           118, "Playful",    195, 2021),
    (9,  "Digital Ohanami",      3, "J-Pop",           126, "Cheerful",   208, 2022),
    # Cobre Vivo (4) - Latin
    (10, "Madrugada Neon",       4, "Latin",           102, "Romantic",   247, 2020),
    (11, "Ritmo Profundo",       4, "Latin",            98, "Sensual",    231, 2021),
    (12, "Fuego Lento",          4, "Latin",           110, "Energetic",  219, 2022),
    # Elara Moon (5) - Pop
    (13, "Gravity Shift",        5, "Pop",             118, "Uplifting",  203, 2021),
    (14, "Silver Static",        5, "Pop",             112, "Dreamy",     226, 2022),
    (15, "Neon Rainfall",        5, "Pop",             124, "Nostalgic",  198, 2023),
    (16, "Zero Gravity Kiss",    5, "Pop",             116, "Romantic",   215, 2023),
    # Static Wolves (6) - Metal
    (17, "Iron Requiem",         6, "Metal",           180, "Aggressive", 287, 2020),
    (18, "Fracture Point",       6, "Metal",           195, "Dark",       261, 2022),
    # Lost Meridian (8) - Lo-fi Hip-hop
    (19, "2am Study Session",    8, "Lo-fi Hip-hop",    75, "Calm",       182, 2021),
    (20, "Rain on Vinyl",        8, "Lo-fi Hip-hop",    72, "Melancholy", 197, 2022),
    (21, "Coffee & Algorithms",  8, "Lo-fi Hip-hop",    78, "Focused",    211, 2022),
    # Zanele Dube (9) - Afrobeats
    (22, "Sunset Lagos",         9, "Afrobeats",       110, "Joyful",     224, 2022),
    (23, "Oya Dance",            9, "Afrobeats",       118, "Energetic",  198, 2023),
    # Cosmo & The Void (10) - Synth-pop
    (24, "Neon Archaeology",    10, "Synth-pop",       126, "Nostalgic",  232, 2019),
    (25, "Starfield Protocol",  10, "Synth-pop",       132, "Euphoric",   219, 2021),
    (26, "Lost Signal 84",      10, "Synth-pop",       120, "Dreamy",     248, 2022),
    # Red Margin (11) - Jazz Fusion
    (27, "Blue Circuit",        11, "Jazz Fusion",      98, "Cool",       341, 2020),
    (28, "Montmartre 3AM",      11, "Jazz Fusion",      88, "Melancholy", 318, 2022),
    # Hyperion (12) - K-Pop
    (29, "CTRL+ALT+LOVE",       12, "K-Pop",           132, "Playful",    201, 2022),
    (30, "Eclipse Protocol",    12, "K-Pop",           138, "Confident",  213, 2022),
    (31, "Mirror Mirror",       12, "K-Pop",           126, "Dreamy",     222, 2023),
    # Sienna Blake (14) - R&B
    (32, "Velvet Static",       14, "R&B",             92, "Sensual",    247, 2022),
    (33, "Glass Feelings",      14, "R&B",             84, "Sad",        263, 2023),
    # The Neon Foxes (15) - Indie Pop
    (34, "Ultraviolet Crush",   15, "Indie Pop",       108, "Uplifting",  221, 2021),
    (35, "Hologram Summer",     15, "Indie Pop",       102, "Nostalgic",  238, 2022),
    (36, "Pastel Vertigo",      15, "Indie Pop",        96, "Dreamy",     254, 2023),
    # Priya Rajan (7) - Bollywood Fusion
    (37, "Raat Aur Neon",        7, "Bollywood Fusion",106, "Romantic",   228, 2021),
    (38, "Dhuan Dhuan",          7, "Bollywood Fusion", 98, "Melancholy", 244, 2022),
    # Dust Carnival (13)
    (39, "Polvo y Cemento",     13, "Alternative",      91, "Melancholy", 271, 2020),
    (40, "Cactus Radio",        13, "Alternative",      99, "Quirky",     233, 2022),
    # Vivienne Echo (16) - Electropop
    (41, "Signal Bloom",        16, "Electropop",      118, "Uplifting",  209, 2021),
    (42, "Chrome Feelings",     16, "Electropop",      124, "Dreamy",     218, 2022),
    (43, "Ultrascript",         16, "Electropop",      130, "Confident",  201, 2023),
    (44, "Mirror Protocol",     16, "Electropop",      126, "Dark",       215, 2024),
    # Kartik Flow (17) - Hip-hop Fusion
    (45, "Delhi Frequency",     17, "Hip-hop Fusion",   92, "Confident",  228, 2021),
    (46, "Monsoon Bars",        17, "Hip-hop Fusion",   86, "Melancholy", 244, 2022),
    # Boreal Sound (18) - Nordic Folk Electronic
    (47, "Fjord Signal",        18, "Nordic Folk Electronic", 108, "Wistful", 267, 2020),
    (48, "Aurora Dispatch",     18, "Nordic Folk Electronic", 114, "Calm",   291, 2022),
    # Cipher Collective (19) - Experimental
    (49, "Null Island",         19, "Experimental",    142, "Tense",      198, 2021),
    (50, "Entropy Suite",       19, "Experimental",     76, "Dark",       354, 2022),
    # Mariana Voss (20) - Pop
    (51, "Sol Nascente",        20, "Pop",             116, "Uplifting",  214, 2021),
    (52, "Onda Nova",           20, "Pop",             122, "Cheerful",   202, 2022),
    (53, "Chuva de Estrelas",   20, "Pop",             112, "Romantic",   231, 2023),
    (54, "Janeiro Heat",        20, "Pop",             118, "Uplifting",  198, 2024),
    # Fractal Garden (21) - Ambient
    (55, "Moss Protocol",       21, "Ambient",          60, "Calm",       384, 2020),
    (56, "Slow Light",          21, "Ambient",          55, "Melancholy", 427, 2022),
    # The Rust Belt (22) - Indie Folk
    (57, "Ohio Elegy",          22, "Indie Folk",       84, "Wistful",    298, 2019),
    (58, "Rust & Morning",      22, "Indie Folk",       78, "Sad",        321, 2021),
    # Lagos Phonk (23) - Afrobeats
    (59, "Agege Highway",       23, "Afrobeats",       112, "Energetic",  201, 2022),
    (60, "Phonk Naija",         23, "Afrobeats",       118, "Aggressive", 189, 2023),
    # Aether Circuit (24) - Techno
    (61, "Warehouse 404",       24, "Techno",          145, "Dark",       366, 2021),
    (62, "Klang System",        24, "Techno",          152, "Tense",      311, 2022),
    # Chloe Winters (25) - R&B Pop
    (63, "Silk & Static",       25, "R&B Pop",          96, "Sensual",   239, 2022),
    (64, "Midnight Garden",     25, "R&B Pop",          88, "Romantic",  253, 2023),
    (65, "Velvet Horizon",      25, "R&B Pop",          94, "Dreamy",    244, 2024),
    # New releases from existing artists
    (66, "Infrared Signal",      1, "Electronic",      132, "Dark",       193, 2024),
    (67, "Stellar Collision",   12, "K-Pop",           140, "Energetic",  207, 2024),
    (68, "Glass Cities",         5, "Pop",             120, "Nostalgic",  224, 2024),
    (69, "Cape Town Drift",      9, "Afrobeats",       108, "Joyful",     218, 2024),
    (70, "4pm Playlist",         8, "Lo-fi Hip-hop",    70, "Calm",       188, 2024),
    (71, "Neon Bruise (Reprise)",14, "R&B",             88, "Sad",        271, 2024),
    (72, "Resonance Grid",      10, "Synth-pop",       128, "Euphoric",   226, 2024),
    (73, "Bombay Haze",          7, "Bollywood Fusion",104, "Nostalgic",  252, 2024),
    (74, "Pigalle Sessions",    11, "Jazz Fusion",      92, "Cool",       328, 2024),
    (75, "Prism Weather",       15, "Indie Pop",       104, "Uplifting",  215, 2024),
]

SEED_USERS = [
    (1,  "beatjunkie_alex",  "USA",          "premium", 2019, 24),
    (2,  "lo_fi_lena",       "Germany",      "free",    2020, 19),
    (3,  "samba_soul",       "Brazil",       "premium", 2018, 31),
    (4,  "tokyodrift_99",    "Japan",        "premium", 2021, 22),
    (5,  "neon_nova",        "USA",          "free",    2022, 17),
    (6,  "vinyljunkie",      "UK",           "premium", 2017, 38),
    (7,  "chill_architect",  "Canada",       "premium", 2020, 27),
    (8,  "afro_rythm",       "South Africa", "free",    2022, 21),
    (9,  "koreawave_fan",    "South Korea",  "premium", 2021, 20),
    (10, "jazzcat_pierre",   "France",       "premium", 2019, 45),
    (11, "rave_goddess",     "Netherlands",  "premium", 2020, 29),
    (12, "midnight_coder",   "India",        "free",    2021, 23),
    (13, "desert_listener",  "Mexico",       "free",    2022, 26),
    (14, "pop_princess",     "Australia",    "premium", 2018, 33),
    (15, "metalhead_kai",    "USA",          "premium", 2016, 35),
    (16, "study_groove",     "UK",           "free",    2023, 18),
    (17, "cumbia_queen",     "Argentina",    "premium", 2019, 28),
    (18, "synth_dreamer",    "USA",          "premium", 2020, 24),
    (19, "indie_orbit",      "Canada",       "free",    2022, 22),
    (20, "bass_prophet",     "Nigeria",      "premium", 2021, 30),
    (21, "cherry_blossom",   "Japan",        "free",    2022, 16),
    (22, "electrowave_jo",   "USA",          "premium", 2018, 26),
    (23, "raga_fusion",      "India",        "premium", 2019, 34),
    (24, "vinyl_cartridge",  "UK",           "free",    2021, 42),
    (25, "cloudhopper",      "Germany",      "premium", 2020, 31),
    (26, "techno_berlin",    "Germany",      "premium", 2020, 28),
    (27, "nordic_wanderer",  "Norway",       "free",    2021, 25),
    (28, "mumbai_nights",    "India",        "premium", 2019, 29),
    (29, "phonk_lagos",      "Nigeria",      "free",    2022, 20),
    (30, "electropop_uk",    "UK",           "premium", 2021, 23),
    (31, "ambient_traveler", "Japan",        "free",    2022, 32),
    (32, "folk_ohio",        "USA",          "free",    2020, 40),
    (33, "voss_stan",        "Brazil",       "premium", 2021, 19),
    (34, "kpop_forever",     "South Korea",  "premium", 2022, 18),
    (35, "rave_berlin",      "Germany",      "premium", 2019, 31),
    (36, "flamenco_heat",    "Spain",        "free",    2022, 27),
    (37, "jazz_tokyo",       "Japan",        "premium", 2020, 36),
    (38, "hip_hop_delhi",    "India",        "free",    2022, 22),
    (39, "pop_mexico",       "Mexico",       "premium", 2021, 24),
    (40, "indie_toronto",    "Canada",       "free",    2022, 21),
    (41, "lo_fi_seoul",      "South Korea",  "premium", 2020, 27),
    (42, "afrobeats_accra",  "Ghana",        "free",    2022, 23),
    (43, "synth_amsterdam",  "Netherlands",  "premium", 2021, 30),
    (44, "rnb_atlanta",      "USA",          "premium", 2020, 26),
    (45, "metal_oslo",       "Norway",       "free",    2021, 33),
    (46, "latin_buenos",     "Argentina",    "premium", 2020, 28),
    (47, "chill_capetown",   "South Africa", "free",    2022, 24),
    (48, "wave_osaka",       "Japan",        "premium", 2021, 22),
    (49, "bass_accra",       "Ghana",        "premium", 2023, 19),
    (50, "dreams_perth",     "Australia",    "free",    2022, 29),
]

# streams: id, user_id, song_id, played_at, completed, skipped_at_sec, source
# source: search / radio / playlist / recommendation / artist_page
SEED_STREAMS = [
    # --- User 1 (beatjunkie_alex, premium) —— heavy electronic listener
    (1,   1,  1, "2024-01-03 10:14:00", 1, None, "search"),
    (2,   1,  2, "2024-01-03 10:18:00", 1, None, "recommendation"),
    (3,   1,  3, "2024-01-05 21:30:00", 1, None, "playlist"),
    (4,   1, 25, "2024-01-07 22:00:00", 1, None, "radio"),
    (5,   1, 29, "2024-01-10 09:00:00", 0, 45,   "recommendation"),
    (6,   1,  4, "2024-01-12 20:00:00", 1, None, "search"),
    (7,   1, 24, "2024-01-15 19:30:00", 1, None, "playlist"),
    (8,   1,  2, "2024-01-20 23:00:00", 1, None, "playlist"),
    (9,   1, 26, "2024-02-01 21:00:00", 1, None, "recommendation"),
    (10,  1,  1, "2024-02-05 20:00:00", 1, None, "search"),
    # --- User 2 (lo_fi_lena, free) —— lo-fi + indie
    (11,  2, 19, "2024-01-04 23:00:00", 1, None, "playlist"),
    (12,  2, 20, "2024-01-04 23:04:00", 1, None, "playlist"),
    (13,  2, 21, "2024-01-04 23:08:00", 1, None, "playlist"),
    (14,  2,  5, "2024-01-06 22:00:00", 1, None, "search"),
    (15,  2, 34, "2024-01-08 20:30:00", 0, 30,   "radio"),
    (16,  2,  7, "2024-01-10 21:00:00", 1, None, "search"),
    (17,  2, 19, "2024-02-02 00:10:00", 1, None, "playlist"),
    (18,  2, 20, "2024-02-02 00:15:00", 1, None, "playlist"),
    (19,  2, 35, "2024-02-10 21:00:00", 0, 55,   "recommendation"),
    (20,  2, 27, "2024-02-15 22:30:00", 1, None, "search"),
    # --- User 3 (samba_soul, premium) —— latin + afrobeats
    (21,  3, 10, "2024-01-02 17:00:00", 1, None, "search"),
    (22,  3, 11, "2024-01-02 17:04:00", 1, None, "artist_page"),
    (23,  3, 12, "2024-01-02 17:08:00", 1, None, "artist_page"),
    (24,  3, 22, "2024-01-05 18:00:00", 1, None, "recommendation"),
    (25,  3, 23, "2024-01-05 18:04:00", 1, None, "artist_page"),
    (26,  3, 10, "2024-01-15 20:00:00", 1, None, "playlist"),
    (27,  3, 37, "2024-01-20 19:00:00", 0, 40,   "radio"),
    (28,  3, 11, "2024-02-01 18:00:00", 1, None, "playlist"),
    (29,  3, 22, "2024-02-08 17:30:00", 1, None, "search"),
    (30,  3, 12, "2024-02-12 19:00:00", 1, None, "recommendation"),
    # --- User 4 (tokyodrift_99, premium) —— J-Pop + K-Pop
    (31,  4,  8, "2024-01-01 15:00:00", 1, None, "search"),
    (32,  4,  9, "2024-01-01 15:03:00", 1, None, "artist_page"),
    (33,  4, 29, "2024-01-03 16:00:00", 1, None, "recommendation"),
    (34,  4, 30, "2024-01-03 16:04:00", 1, None, "artist_page"),
    (35,  4, 31, "2024-01-05 14:00:00", 1, None, "playlist"),
    (36,  4,  8, "2024-01-10 15:00:00", 1, None, "playlist"),
    (37,  4,  9, "2024-01-20 16:00:00", 0, 25,   "radio"),
    (38,  4, 13, "2024-02-01 17:00:00", 0, 38,   "recommendation"),
    (39,  4, 29, "2024-02-05 15:00:00", 1, None, "search"),
    (40,  4, 31, "2024-02-10 14:30:00", 1, None, "playlist"),
    # --- User 5 (neon_nova, free) —— pop fan
    (41,  5, 13, "2024-01-03 12:00:00", 1, None, "search"),
    (42,  5, 14, "2024-01-03 12:04:00", 1, None, "artist_page"),
    (43,  5, 15, "2024-01-05 13:00:00", 0, 60,   "radio"),
    (44,  5, 16, "2024-01-08 11:00:00", 1, None, "search"),
    (45,  5, 32, "2024-01-12 20:00:00", 0, 45,   "recommendation"),
    (46,  5, 13, "2024-01-18 12:00:00", 1, None, "playlist"),
    (47,  5, 14, "2024-02-02 13:00:00", 1, None, "playlist"),
    (48,  5, 15, "2024-02-08 14:00:00", 0, 30,   "radio"),
    # --- User 6 (vinyljunkie, premium) —— indie rock + jazz
    (49,  6,  5, "2024-01-04 19:00:00", 1, None, "search"),
    (50,  6,  6, "2024-01-04 19:04:00", 1, None, "artist_page"),
    (51,  6,  7, "2024-01-04 19:08:00", 1, None, "artist_page"),
    (52,  6, 27, "2024-01-08 20:00:00", 1, None, "search"),
    (53,  6, 28, "2024-01-08 20:05:00", 1, None, "artist_page"),
    (54,  6,  5, "2024-01-20 18:00:00", 1, None, "playlist"),
    (55,  6, 27, "2024-02-03 21:00:00", 1, None, "playlist"),
    (56,  6,  7, "2024-02-10 19:00:00", 1, None, "search"),
    (57,  6, 39, "2024-02-15 20:00:00", 0, 70,   "recommendation"),
    (58,  6, 28, "2024-02-18 21:00:00", 1, None, "playlist"),
    # --- User 7 (chill_architect, premium) —— synth-pop + lo-fi
    (59,  7, 24, "2024-01-02 22:00:00", 1, None, "playlist"),
    (60,  7, 25, "2024-01-02 22:04:00", 1, None, "playlist"),
    (61,  7, 26, "2024-01-02 22:08:00", 1, None, "playlist"),
    (62,  7, 19, "2024-01-05 23:00:00", 1, None, "recommendation"),
    (63,  7, 20, "2024-01-05 23:04:00", 1, None, "playlist"),
    (64,  7, 21, "2024-01-10 22:00:00", 1, None, "playlist"),
    (65,  7, 24, "2024-01-22 21:30:00", 1, None, "search"),
    (66,  7, 26, "2024-02-05 22:00:00", 1, None, "playlist"),
    (67,  7, 36, "2024-02-12 23:00:00", 0, 42,   "recommendation"),
    (68,  7, 25, "2024-02-18 21:00:00", 1, None, "radio"),
    # --- User 8 (afro_rythm, free) —— afrobeats
    (69,  8, 22, "2024-01-04 16:00:00", 1, None, "search"),
    (70,  8, 23, "2024-01-04 16:04:00", 1, None, "artist_page"),
    (71,  8, 10, "2024-01-10 17:00:00", 0, 50,   "recommendation"),
    (72,  8, 22, "2024-01-20 15:30:00", 1, None, "playlist"),
    (73,  8, 23, "2024-02-05 16:00:00", 1, None, "search"),
    (74,  8, 37, "2024-02-10 17:00:00", 1, None, "recommendation"),
    # --- User 9 (koreawave_fan, premium) —— K-Pop heavy
    (75,  9, 29, "2024-01-01 14:00:00", 1, None, "search"),
    (76,  9, 30, "2024-01-01 14:04:00", 1, None, "artist_page"),
    (77,  9, 31, "2024-01-01 14:08:00", 1, None, "artist_page"),
    (78,  9, 29, "2024-01-05 13:00:00", 1, None, "playlist"),
    (79,  9, 13, "2024-01-10 15:00:00", 1, None, "recommendation"),
    (80,  9, 14, "2024-01-10 15:04:00", 0, 35,   "radio"),
    (81,  9, 30, "2024-01-18 14:00:00", 1, None, "playlist"),
    (82,  9, 31, "2024-02-01 13:30:00", 1, None, "search"),
    (83,  9, 29, "2024-02-08 14:00:00", 1, None, "playlist"),
    (84,  9, 30, "2024-02-15 13:00:00", 1, None, "artist_page"),
    # --- User 10 (jazzcat_pierre, premium) —— jazz + indie
    (85, 10, 27, "2024-01-03 21:00:00", 1, None, "search"),
    (86, 10, 28, "2024-01-03 21:05:00", 1, None, "artist_page"),
    (87, 10,  5, "2024-01-08 20:00:00", 1, None, "recommendation"),
    (88, 10,  6, "2024-01-08 20:04:00", 0, 90,   "radio"),
    (89, 10, 27, "2024-01-15 22:00:00", 1, None, "playlist"),
    (90, 10, 28, "2024-02-01 21:00:00", 1, None, "playlist"),
    (91, 10, 40, "2024-02-10 22:00:00", 0, 55,   "recommendation"),
    (92, 10, 27, "2024-02-20 21:00:00", 1, None, "search"),
    # --- User 11 (rave_goddess, premium) —— electronic + synth
    (93, 11,  1, "2024-01-02 23:00:00", 1, None, "playlist"),
    (94, 11,  2, "2024-01-02 23:04:00", 1, None, "playlist"),
    (95, 11,  3, "2024-01-02 23:08:00", 1, None, "playlist"),
    (96, 11,  4, "2024-01-05 22:00:00", 1, None, "artist_page"),
    (97, 11, 25, "2024-01-10 23:00:00", 1, None, "recommendation"),
    (98, 11, 24, "2024-01-15 22:00:00", 1, None, "radio"),
    (99, 11,  1, "2024-02-01 23:00:00", 1, None, "search"),
    (100,11,  3, "2024-02-08 22:00:00", 1, None, "playlist"),
    (101,11,  2, "2024-02-15 23:30:00", 0, 40,   "recommendation"),
    # --- User 12 (midnight_coder, free) —— lo-fi + bollywood fusion
    (102,12, 19, "2024-01-03 01:00:00", 1, None, "playlist"),
    (103,12, 20, "2024-01-03 01:04:00", 1, None, "playlist"),
    (104,12, 21, "2024-01-03 01:08:00", 1, None, "playlist"),
    (105,12, 37, "2024-01-08 00:30:00", 1, None, "search"),
    (106,12, 38, "2024-01-08 00:34:00", 1, None, "artist_page"),
    (107,12, 19, "2024-01-18 02:00:00", 1, None, "playlist"),
    (108,12, 37, "2024-02-03 01:00:00", 1, None, "playlist"),
    (109,12, 21, "2024-02-10 00:30:00", 1, None, "recommendation"),
    # --- User 13 (desert_listener, free) —— alt + metal
    (110,13, 39, "2024-01-05 20:00:00", 1, None, "search"),
    (111,13, 40, "2024-01-05 20:04:00", 1, None, "artist_page"),
    (112,13, 17, "2024-01-10 21:00:00", 0, 50,   "recommendation"),
    (113,13, 39, "2024-01-20 19:30:00", 1, None, "playlist"),
    (114,13, 18, "2024-02-05 20:00:00", 0, 65,   "radio"),
    (115,13, 40, "2024-02-15 21:00:00", 1, None, "search"),
    # --- User 14 (pop_princess, premium) —— pop + R&B
    (116,14, 13, "2024-01-02 18:00:00", 1, None, "search"),
    (117,14, 14, "2024-01-02 18:04:00", 1, None, "artist_page"),
    (118,14, 15, "2024-01-02 18:08:00", 1, None, "artist_page"),
    (119,14, 16, "2024-01-04 19:00:00", 1, None, "playlist"),
    (120,14, 32, "2024-01-10 18:30:00", 1, None, "recommendation"),
    (121,14, 33, "2024-01-10 18:35:00", 1, None, "artist_page"),
    (122,14, 13, "2024-01-20 17:00:00", 1, None, "playlist"),
    (123,14, 15, "2024-02-02 18:00:00", 1, None, "search"),
    (124,14, 32, "2024-02-08 19:00:00", 1, None, "playlist"),
    (125,14, 33, "2024-02-15 18:30:00", 0, 48,   "recommendation"),
    # --- User 15 (metalhead_kai, premium) —— metal + rock
    (126,15, 17, "2024-01-03 22:00:00", 1, None, "search"),
    (127,15, 18, "2024-01-03 22:05:00", 1, None, "artist_page"),
    (128,15,  6, "2024-01-08 21:00:00", 1, None, "recommendation"),
    (129,15, 17, "2024-01-15 23:00:00", 1, None, "playlist"),
    (130,15, 18, "2024-02-01 22:00:00", 1, None, "playlist"),
    (131,15,  6, "2024-02-10 21:00:00", 1, None, "search"),
    # --- User 16 (study_groove, free) —— lo-fi study listener
    (132,16, 19, "2024-01-04 20:00:00", 1, None, "playlist"),
    (133,16, 20, "2024-01-04 20:04:00", 1, None, "playlist"),
    (134,16, 21, "2024-01-04 20:08:00", 1, None, "playlist"),
    (135,16, 21, "2024-01-10 21:00:00", 1, None, "recommendation"),
    (136,16, 19, "2024-02-05 22:00:00", 1, None, "search"),
    (137,16, 27, "2024-02-15 23:00:00", 0, 80,   "recommendation"),
    # --- User 17 (cumbia_queen, premium) —— latin + afrobeats
    (138,17, 10, "2024-01-05 19:00:00", 1, None, "search"),
    (139,17, 11, "2024-01-05 19:04:00", 1, None, "playlist"),
    (140,17, 22, "2024-01-10 18:00:00", 1, None, "recommendation"),
    (141,17, 23, "2024-01-10 18:04:00", 1, None, "artist_page"),
    (142,17, 12, "2024-01-18 19:00:00", 1, None, "playlist"),
    (143,17, 10, "2024-02-03 18:30:00", 1, None, "search"),
    # --- User 18 (synth_dreamer, premium) —— synth-pop + electronic
    (144,18, 24, "2024-01-03 20:00:00", 1, None, "playlist"),
    (145,18, 25, "2024-01-03 20:04:00", 1, None, "playlist"),
    (146,18, 26, "2024-01-03 20:08:00", 1, None, "playlist"),
    (147,18,  1, "2024-01-08 21:00:00", 1, None, "recommendation"),
    (148,18,  2, "2024-01-08 21:04:00", 1, None, "recommendation"),
    (149,18, 24, "2024-01-20 20:00:00", 1, None, "search"),
    (150,18, 26, "2024-02-01 21:00:00", 1, None, "playlist"),
    (151,18, 25, "2024-02-10 20:30:00", 1, None, "radio"),
    # --- User 19 (indie_orbit, free) —— indie pop + rock
    (152,19, 34, "2024-01-05 18:00:00", 1, None, "search"),
    (153,19, 35, "2024-01-05 18:04:00", 1, None, "artist_page"),
    (154,19,  5, "2024-01-10 19:00:00", 0, 35,   "recommendation"),
    (155,19,  7, "2024-01-15 18:30:00", 1, None, "search"),
    (156,19, 36, "2024-01-22 17:00:00", 1, None, "playlist"),
    (157,19, 34, "2024-02-05 18:00:00", 1, None, "playlist"),
    # --- User 20 (bass_prophet, premium) —— electronic + afrobeats
    (158,20,  1, "2024-01-04 21:00:00", 1, None, "search"),
    (159,20, 22, "2024-01-08 20:00:00", 1, None, "recommendation"),
    (160,20, 23, "2024-01-08 20:04:00", 1, None, "artist_page"),
    (161,20,  3, "2024-01-15 21:00:00", 1, None, "playlist"),
    (162,20, 22, "2024-02-01 20:00:00", 1, None, "search"),
    (163,20,  1, "2024-02-10 21:00:00", 1, None, "playlist"),
    # --- User 21 (cherry_blossom, free) —— J-Pop + K-Pop
    (164,21,  8, "2024-01-06 16:00:00", 1, None, "search"),
    (165,21,  9, "2024-01-06 16:04:00", 1, None, "artist_page"),
    (166,21, 29, "2024-01-10 15:00:00", 1, None, "recommendation"),
    (167,21, 30, "2024-01-10 15:04:00", 0, 28,   "radio"),
    (168,21, 31, "2024-01-18 16:00:00", 1, None, "playlist"),
    (169,21,  8, "2024-02-05 15:30:00", 1, None, "search"),
    # --- User 22 (electrowave_jo, premium) —— electronic
    (170,22,  1, "2024-01-02 22:00:00", 1, None, "search"),
    (171,22,  2, "2024-01-02 22:04:00", 1, None, "artist_page"),
    (172,22,  3, "2024-01-02 22:08:00", 1, None, "artist_page"),
    (173,22,  4, "2024-01-05 23:00:00", 1, None, "playlist"),
    (174,22, 25, "2024-01-10 21:00:00", 1, None, "recommendation"),
    (175,22,  1, "2024-01-20 22:00:00", 1, None, "search"),
    (176,22,  3, "2024-02-01 23:00:00", 1, None, "playlist"),
    # --- User 23 (raga_fusion, premium) —— bollywood fusion + jazz
    (177,23, 37, "2024-01-04 19:00:00", 1, None, "search"),
    (178,23, 38, "2024-01-04 19:04:00", 1, None, "artist_page"),
    (179,23, 27, "2024-01-10 20:00:00", 1, None, "recommendation"),
    (180,23, 28, "2024-01-10 20:05:00", 1, None, "artist_page"),
    (181,23, 37, "2024-01-20 19:00:00", 1, None, "playlist"),
    (182,23, 38, "2024-02-05 18:30:00", 1, None, "playlist"),
    # --- User 24 (vinyl_cartridge, free) —— indie rock + jazz
    (183,24,  5, "2024-01-05 20:00:00", 1, None, "search"),
    (184,24,  6, "2024-01-05 20:04:00", 0, 55,   "radio"),
    (185,24, 27, "2024-01-12 21:00:00", 1, None, "recommendation"),
    (186,24,  7, "2024-01-18 20:30:00", 1, None, "search"),
    (187,24, 28, "2024-02-01 21:00:00", 1, None, "playlist"),
    # --- User 25 (cloudhopper, premium) —— synth-pop + pop
    (188,25, 24, "2024-01-03 19:00:00", 1, None, "playlist"),
    (189,25, 13, "2024-01-08 18:00:00", 1, None, "recommendation"),
    (190,25, 14, "2024-01-08 18:04:00", 1, None, "radio"),
    (191,25, 26, "2024-01-15 19:00:00", 1, None, "playlist"),
    (192,25, 15, "2024-01-22 18:00:00", 0, 62,   "recommendation"),
    (193,25, 24, "2024-02-05 19:00:00", 1, None, "search"),
    (194,25, 13, "2024-02-15 18:30:00", 1, None, "playlist"),
    # --- User 26 (techno_berlin) — techno + electronic
    (195,26, 61, "2024-01-05 23:00:00", 1, None, "search"),
    (196,26, 62, "2024-01-05 23:10:00", 1, None, "artist_page"),
    (197,26,  1, "2024-01-10 22:00:00", 0, 35,   "recommendation"),
    (198,26, 24, "2024-01-15 23:30:00", 1, None, "playlist"),
    (199,26, 25, "2024-01-15 23:35:00", 1, None, "playlist"),
    (200,26, 61, "2024-02-01 22:00:00", 1, None, "search"),
    (201,26,  2, "2024-02-10 23:00:00", 1, None, "radio"),
    (202,26, 62, "2024-02-15 22:30:00", 1, None, "artist_page"),
    (203,26, 66, "2024-03-01 22:00:00", 1, None, "recommendation"),
    # --- User 27 (nordic_wanderer) — nordic folk + ambient
    (204,27, 47, "2024-01-06 20:00:00", 1, None, "search"),
    (205,27, 48, "2024-01-06 20:05:00", 1, None, "artist_page"),
    (206,27, 55, "2024-01-12 21:00:00", 1, None, "recommendation"),
    (207,27, 56, "2024-01-12 21:07:00", 1, None, "artist_page"),
    (208,27, 47, "2024-02-01 19:00:00", 1, None, "playlist"),
    (209,27, 19, "2024-02-08 22:00:00", 0, 45,   "recommendation"),
    # --- User 28 (mumbai_nights) — hip-hop fusion + bollywood
    (210,28, 45, "2024-01-04 20:00:00", 1, None, "search"),
    (211,28, 46, "2024-01-04 20:04:00", 1, None, "artist_page"),
    (212,28, 37, "2024-01-10 19:00:00", 1, None, "recommendation"),
    (213,28, 38, "2024-01-10 19:04:00", 1, None, "artist_page"),
    (214,28, 73, "2024-01-18 20:00:00", 1, None, "search"),
    (215,28, 45, "2024-02-02 20:00:00", 1, None, "playlist"),
    (216,28, 73, "2024-02-10 21:00:00", 1, None, "recommendation"),
    (217,28, 37, "2024-02-15 19:00:00", 1, None, "search"),
    (218,28, 73, "2024-03-01 20:00:00", 1, None, "playlist"),
    # --- User 29 (phonk_lagos) — afrobeats
    (219,29, 59, "2024-01-05 18:00:00", 1, None, "search"),
    (220,29, 60, "2024-01-05 18:04:00", 1, None, "artist_page"),
    (221,29, 22, "2024-01-10 17:00:00", 1, None, "recommendation"),
    (222,29, 69, "2024-01-18 18:00:00", 0, 30,   "radio"),
    (223,29, 59, "2024-02-01 19:00:00", 1, None, "search"),
    (224,29, 60, "2024-02-08 18:00:00", 1, None, "playlist"),
    (225,29, 69, "2024-03-02 18:00:00", 1, None, "recommendation"),
    # --- User 30 (electropop_uk) — electropop
    (226,30, 41, "2024-01-04 19:00:00", 1, None, "search"),
    (227,30, 42, "2024-01-04 19:04:00", 1, None, "artist_page"),
    (228,30, 43, "2024-01-04 19:08:00", 1, None, "artist_page"),
    (229,30, 44, "2024-01-10 20:00:00", 1, None, "recommendation"),
    (230,30, 13, "2024-01-15 19:00:00", 0, 55,   "radio"),
    (231,30, 41, "2024-02-01 20:00:00", 1, None, "playlist"),
    (232,30, 43, "2024-02-08 19:00:00", 1, None, "search"),
    (233,30, 42, "2024-02-15 20:00:00", 1, None, "recommendation"),
    (234,30, 44, "2024-03-01 20:00:00", 1, None, "search"),
    # --- User 31 (ambient_traveler) — ambient + lo-fi
    (235,31, 55, "2024-01-06 23:00:00", 1, None, "search"),
    (236,31, 56, "2024-01-06 23:07:00", 1, None, "artist_page"),
    (237,31, 19, "2024-01-12 22:00:00", 1, None, "recommendation"),
    (238,31, 20, "2024-01-12 22:03:00", 1, None, "playlist"),
    (239,31, 21, "2024-01-12 22:07:00", 1, None, "playlist"),
    (240,31, 55, "2024-02-01 23:00:00", 1, None, "search"),
    (241,31, 56, "2024-03-02 22:00:00", 1, None, "recommendation"),
    # --- User 32 (folk_ohio) — indie folk + rock
    (242,32, 57, "2024-01-07 19:00:00", 1, None, "search"),
    (243,32, 58, "2024-01-07 19:05:00", 1, None, "artist_page"),
    (244,32,  7, "2024-01-14 20:00:00", 1, None, "recommendation"),
    (245,32,  5, "2024-01-14 20:05:00", 0, 65,   "radio"),
    (246,32, 57, "2024-02-01 18:00:00", 1, None, "playlist"),
    (247,32, 58, "2024-02-12 19:00:00", 1, None, "search"),
    # --- User 33 (voss_stan) — pop + latin
    (248,33, 51, "2024-01-03 17:00:00", 1, None, "search"),
    (249,33, 52, "2024-01-03 17:04:00", 1, None, "artist_page"),
    (250,33, 53, "2024-01-03 17:08:00", 1, None, "artist_page"),
    (251,33, 54, "2024-01-10 18:00:00", 1, None, "recommendation"),
    (252,33, 10, "2024-01-18 17:00:00", 0, 40,   "radio"),
    (253,33, 51, "2024-02-01 18:00:00", 1, None, "playlist"),
    (254,33, 52, "2024-02-08 17:30:00", 1, None, "playlist"),
    (255,33, 54, "2024-03-01 18:00:00", 1, None, "search"),
    # --- User 34 (kpop_forever) — K-Pop
    (256,34, 29, "2024-01-02 15:00:00", 1, None, "search"),
    (257,34, 30, "2024-01-02 15:04:00", 1, None, "artist_page"),
    (258,34, 31, "2024-01-02 15:08:00", 1, None, "artist_page"),
    (259,34, 67, "2024-01-08 16:00:00", 1, None, "recommendation"),
    (260,34, 29, "2024-01-15 14:00:00", 1, None, "playlist"),
    (261,34, 67, "2024-02-01 15:00:00", 1, None, "search"),
    (262,34, 30, "2024-02-10 16:00:00", 1, None, "playlist"),
    (263,34, 31, "2024-02-18 15:00:00", 0, 22,   "radio"),
    (264,34, 67, "2024-03-01 15:30:00", 1, None, "playlist"),
    # --- User 35 (rave_berlin) — techno + electronic
    (265,35, 61, "2024-01-03 23:00:00", 1, None, "search"),
    (266,35, 62, "2024-01-03 23:10:00", 1, None, "artist_page"),
    (267,35,  1, "2024-01-08 22:00:00", 1, None, "recommendation"),
    (268,35,  2, "2024-01-08 22:04:00", 1, None, "recommendation"),
    (269,35,  3, "2024-01-08 22:08:00", 1, None, "playlist"),
    (270,35, 61, "2024-01-20 23:30:00", 1, None, "search"),
    (271,35,  4, "2024-02-01 22:00:00", 0, 38,   "radio"),
    (272,35, 62, "2024-02-10 23:00:00", 1, None, "playlist"),
    (273,35, 62, "2024-03-02 23:00:00", 1, None, "search"),
    # --- User 36 (flamenco_heat) — latin + afrobeats
    (274,36, 10, "2024-01-05 20:00:00", 1, None, "search"),
    (275,36, 11, "2024-01-05 20:04:00", 1, None, "artist_page"),
    (276,36, 12, "2024-01-05 20:08:00", 1, None, "artist_page"),
    (277,36, 22, "2024-01-12 19:00:00", 1, None, "recommendation"),
    (278,36, 23, "2024-01-12 19:04:00", 0, 45,   "radio"),
    (279,36, 10, "2024-02-01 20:00:00", 1, None, "playlist"),
    (280,36, 22, "2024-02-10 19:30:00", 1, None, "search"),
    (281,36, 12, "2024-03-02 20:00:00", 0, 55,   "radio"),
    # --- User 37 (jazz_tokyo) — jazz fusion + j-pop
    (282,37, 27, "2024-01-04 21:00:00", 1, None, "search"),
    (283,37, 28, "2024-01-04 21:05:00", 1, None, "artist_page"),
    (284,37, 74, "2024-01-10 20:00:00", 1, None, "recommendation"),
    (285,37,  8, "2024-01-15 22:00:00", 0, 50,   "radio"),
    (286,37, 27, "2024-02-01 21:00:00", 1, None, "playlist"),
    (287,37, 28, "2024-02-10 21:30:00", 1, None, "search"),
    (288,37, 74, "2024-02-18 22:00:00", 1, None, "recommendation"),
    (289,37, 74, "2024-03-02 21:00:00", 1, None, "search"),
    # --- User 38 (hip_hop_delhi) — hip-hop fusion + bollywood
    (290,38, 45, "2024-01-06 19:00:00", 1, None, "search"),
    (291,38, 46, "2024-01-06 19:04:00", 0, 55,   "artist_page"),
    (292,38, 73, "2024-01-14 20:00:00", 1, None, "recommendation"),
    (293,38, 37, "2024-01-20 19:00:00", 1, None, "radio"),
    (294,38, 45, "2024-02-05 19:00:00", 1, None, "playlist"),
    (295,38, 73, "2024-03-01 19:00:00", 1, None, "search"),
    # --- User 39 (pop_mexico) — pop
    (296,39, 13, "2024-01-05 17:00:00", 1, None, "search"),
    (297,39, 14, "2024-01-05 17:04:00", 1, None, "artist_page"),
    (298,39, 51, "2024-01-12 18:00:00", 1, None, "recommendation"),
    (299,39, 52, "2024-01-12 18:04:00", 1, None, "artist_page"),
    (300,39, 68, "2024-01-20 17:00:00", 1, None, "search"),
    (301,39, 13, "2024-02-01 18:00:00", 1, None, "playlist"),
    (302,39, 54, "2024-03-01 17:00:00", 1, None, "recommendation"),
    # --- User 40 (indie_toronto) — indie pop + folk
    (303,40, 34, "2024-01-06 19:00:00", 1, None, "search"),
    (304,40, 35, "2024-01-06 19:04:00", 1, None, "artist_page"),
    (305,40, 36, "2024-01-06 19:08:00", 1, None, "artist_page"),
    (306,40, 57, "2024-01-15 20:00:00", 0, 70,   "recommendation"),
    (307,40, 75, "2024-01-22 19:00:00", 1, None, "search"),
    (308,40, 34, "2024-02-05 18:00:00", 1, None, "playlist"),
    (309,40, 36, "2024-02-15 19:00:00", 1, None, "playlist"),
    (310,40, 75, "2024-03-02 19:00:00", 1, None, "search"),
    # --- User 41 (lo_fi_seoul) — lo-fi + k-pop
    (311,41, 19, "2024-01-04 23:00:00", 1, None, "playlist"),
    (312,41, 20, "2024-01-04 23:04:00", 1, None, "playlist"),
    (313,41, 21, "2024-01-04 23:08:00", 1, None, "playlist"),
    (314,41, 70, "2024-01-10 22:00:00", 1, None, "recommendation"),
    (315,41, 29, "2024-01-18 00:00:00", 0, 30,   "radio"),
    (316,41, 19, "2024-02-05 23:00:00", 1, None, "search"),
    (317,41, 70, "2024-02-12 22:30:00", 1, None, "playlist"),
    (318,41, 70, "2024-03-01 23:00:00", 1, None, "playlist"),
    # --- User 42 (afrobeats_accra) — afrobeats
    (319,42, 59, "2024-01-05 16:00:00", 1, None, "search"),
    (320,42, 60, "2024-01-05 16:04:00", 1, None, "artist_page"),
    (321,42, 22, "2024-01-12 17:00:00", 1, None, "recommendation"),
    (322,42, 69, "2024-01-18 16:00:00", 1, None, "search"),
    (323,42, 59, "2024-02-01 16:00:00", 1, None, "playlist"),
    (324,42, 60, "2024-02-10 17:00:00", 0, 40,   "radio"),
    (325,42, 69, "2024-03-02 17:00:00", 1, None, "search"),
    # --- User 43 (synth_amsterdam) — synth-pop + electropop
    (326,43, 24, "2024-01-03 21:00:00", 1, None, "playlist"),
    (327,43, 25, "2024-01-03 21:04:00", 1, None, "playlist"),
    (328,43, 26, "2024-01-03 21:08:00", 1, None, "playlist"),
    (329,43, 41, "2024-01-10 22:00:00", 1, None, "recommendation"),
    (330,43, 42, "2024-01-10 22:04:00", 1, None, "artist_page"),
    (331,43, 24, "2024-02-01 21:00:00", 1, None, "search"),
    (332,43, 41, "2024-02-10 22:00:00", 1, None, "playlist"),
    (333,43, 41, "2024-03-01 22:00:00", 0, 35,   "radio"),
    # --- User 44 (rnb_atlanta) — R&B
    (334,44, 32, "2024-01-04 20:00:00", 1, None, "search"),
    (335,44, 33, "2024-01-04 20:04:00", 1, None, "artist_page"),
    (336,44, 63, "2024-01-10 19:00:00", 1, None, "recommendation"),
    (337,44, 64, "2024-01-10 19:04:00", 1, None, "artist_page"),
    (338,44, 71, "2024-01-18 20:00:00", 1, None, "search"),
    (339,44, 65, "2024-01-22 19:00:00", 1, None, "recommendation"),
    (340,44, 32, "2024-02-01 20:00:00", 1, None, "playlist"),
    (341,44, 63, "2024-02-10 19:30:00", 1, None, "search"),
    (342,44, 64, "2024-02-15 20:00:00", 0, 44,   "recommendation"),
    (343,44, 65, "2024-03-02 19:00:00", 1, None, "playlist"),
    # --- User 45 (metal_oslo) — metal
    (344,45, 17, "2024-01-05 22:00:00", 1, None, "search"),
    (345,45, 18, "2024-01-05 22:05:00", 1, None, "artist_page"),
    (346,45,  6, "2024-01-12 21:00:00", 1, None, "recommendation"),
    (347,45, 17, "2024-02-01 23:00:00", 1, None, "playlist"),
    (348,45, 18, "2024-02-10 22:00:00", 0, 60,   "radio"),
    # --- User 46 (latin_buenos) — latin + afrobeats
    (349,46, 10, "2024-01-05 19:00:00", 1, None, "search"),
    (350,46, 11, "2024-01-05 19:04:00", 1, None, "artist_page"),
    (351,46, 12, "2024-01-05 19:08:00", 1, None, "artist_page"),
    (352,46, 22, "2024-01-12 18:00:00", 1, None, "recommendation"),
    (353,46, 59, "2024-01-18 19:00:00", 0, 55,   "radio"),
    (354,46, 10, "2024-02-01 19:00:00", 1, None, "playlist"),
    (355,46, 11, "2024-02-10 18:30:00", 1, None, "search"),
    (356,46, 12, "2024-03-02 19:00:00", 1, None, "search"),
    # --- User 47 (chill_capetown) — ambient + lo-fi
    (357,47, 19, "2024-01-06 22:00:00", 1, None, "playlist"),
    (358,47, 20, "2024-01-06 22:04:00", 1, None, "playlist"),
    (359,47, 55, "2024-01-12 23:00:00", 1, None, "recommendation"),
    (360,47, 56, "2024-01-12 23:07:00", 1, None, "artist_page"),
    (361,47, 21, "2024-01-20 22:00:00", 1, None, "search"),
    (362,47, 19, "2024-02-05 22:30:00", 1, None, "playlist"),
    (363,47, 56, "2024-03-01 23:00:00", 1, None, "search"),
    # --- User 48 (wave_osaka) — j-pop + k-pop
    (364,48,  8, "2024-01-04 15:00:00", 1, None, "search"),
    (365,48,  9, "2024-01-04 15:03:00", 1, None, "artist_page"),
    (366,48, 29, "2024-01-10 16:00:00", 1, None, "recommendation"),
    (367,48, 30, "2024-01-10 16:04:00", 1, None, "artist_page"),
    (368,48, 31, "2024-01-18 15:00:00", 1, None, "playlist"),
    (369,48,  8, "2024-02-01 16:00:00", 1, None, "search"),
    (370,48, 29, "2024-02-10 15:30:00", 0, 28,   "radio"),
    # --- User 49 (bass_accra) — afrobeats + electronic
    (371,49, 59, "2024-01-05 17:00:00", 1, None, "search"),
    (372,49, 60, "2024-01-05 17:04:00", 1, None, "artist_page"),
    (373,49, 22, "2024-01-12 16:00:00", 1, None, "recommendation"),
    (374,49, 69, "2024-01-18 17:00:00", 1, None, "search"),
    (375,49,  1, "2024-01-25 18:00:00", 1, None, "radio"),
    (376,49, 59, "2024-02-05 17:00:00", 1, None, "playlist"),
    (377,49, 23, "2024-03-02 17:00:00", 1, None, "artist_page"),
    # --- User 50 (dreams_perth) — synth-pop + pop
    (378,50, 24, "2024-01-06 18:00:00", 1, None, "search"),
    (379,50, 25, "2024-01-06 18:04:00", 1, None, "playlist"),
    (380,50, 13, "2024-01-12 17:00:00", 1, None, "recommendation"),
    (381,50, 14, "2024-01-12 17:04:00", 0, 50,   "radio"),
    (382,50, 72, "2024-01-18 18:00:00", 1, None, "search"),
    (383,50, 24, "2024-02-01 19:00:00", 1, None, "playlist"),
    (384,50, 13, "2024-02-10 17:30:00", 1, None, "recommendation"),
    # --- Existing users with new 2024 songs
    (385,  1, 66, "2024-02-20 20:00:00", 1, None, "search"),
    (386,  4, 67, "2024-02-22 15:00:00", 1, None, "recommendation"),
    (387,  5, 68, "2024-02-20 12:00:00", 1, None, "search"),
    (388,  9, 67, "2024-02-25 14:00:00", 1, None, "search"),
    (389, 11, 66, "2024-02-22 23:00:00", 1, None, "recommendation"),
    (390, 14, 63, "2024-02-20 18:00:00", 1, None, "search"),
    (391, 14, 64, "2024-02-20 18:04:00", 1, None, "artist_page"),
    (392, 14, 65, "2024-03-02 18:00:00", 1, None, "recommendation"),
    (393, 20, 69, "2024-02-22 20:00:00", 1, None, "recommendation"),
    (394, 22, 66, "2024-02-25 22:00:00", 1, None, "playlist"),
    (395, 23, 73, "2024-02-22 19:00:00", 1, None, "search"),
    (396,  6, 74, "2024-02-25 21:00:00", 1, None, "search"),
    (397, 10, 74, "2024-02-20 21:00:00", 1, None, "recommendation"),
    (398,  7, 72, "2024-02-22 22:00:00", 1, None, "search"),
    (399, 18, 72, "2024-02-25 20:00:00", 1, None, "playlist"),
    (400,  9, 67, "2024-03-01 14:00:00", 1, None, "playlist"),
    (401, 34, 67, "2024-03-01 15:30:00", 1, None, "playlist"),
    (402, 28, 73, "2024-03-01 20:00:00", 1, None, "playlist"),
    (403, 38, 73, "2024-03-01 19:00:00", 1, None, "search"),
    (404, 37, 74, "2024-03-02 22:00:00", 1, None, "search"),
    (405, 40, 75, "2024-03-02 19:00:00", 1, None, "search"),
    (406, 19, 75, "2024-03-02 18:00:00", 1, None, "recommendation"),
    (407, 41, 70, "2024-03-01 23:00:00", 1, None, "playlist"),
    (408, 12, 70, "2024-03-01 01:00:00", 1, None, "recommendation"),
    (409, 16, 70, "2024-03-01 22:00:00", 1, None, "search"),
    (410, 47, 56, "2024-03-01 23:00:00", 1, None, "search"),
    (411, 31, 56, "2024-03-02 22:00:00", 1, None, "recommendation"),
    (412, 42, 69, "2024-03-02 17:30:00", 1, None, "artist_page"),
    (413, 29, 69, "2024-03-02 18:30:00", 1, None, "recommendation"),
    (414, 49, 23, "2024-03-02 17:00:00", 1, None, "artist_page"),
    (415, 26, 62, "2024-03-01 23:30:00", 1, None, "playlist"),
    (416, 35, 61, "2024-03-02 23:00:00", 1, None, "search"),
    (417,  1, 66, "2024-03-02 20:00:00", 1, None, "playlist"),
    (418, 11, 66, "2024-03-01 23:00:00", 1, None, "search"),
    (419, 22, 66, "2024-03-02 22:30:00", 1, None, "search"),
]

SEED_PLAYLISTS = [
    (1,  "Late Night Circuits",    1,  1, "2024-01-01"),
    (2,  "Coding in the Rain",     2,  1, "2024-01-02"),
    (3,  "Samba & Beats",          3,  1, "2024-01-01"),
    (4,  "Tokyo Nights",           4,  1, "2024-01-01"),
    (5,  "Pop Bops 2024",          5,  0, "2024-01-03"),
    (6,  "Vinyl & Vibes",          6,  1, "2024-01-03"),
    (7,  "Synthwave Sunday",       7,  1, "2024-01-02"),
    (8,  "Lagos Flow",             8,  1, "2024-01-04"),
    (9,  "Hyperion Obsessed",      9,  1, "2024-01-01"),
    (10, "Jazz After Midnight",   10,  1, "2024-01-03"),
    (11, "Rave Essentials",       11,  1, "2024-01-02"),
    (12, "3AM Focus Mode",        12,  1, "2024-01-03"),
    (13, "Desert Road Trip",      13,  0, "2024-01-05"),
    (14, "R&B & Chill",           14,  1, "2024-01-02"),
    (15, "Heavy Metal Bible",     15,  1, "2024-01-03"),
    (16, "Study Groove Vol.1",    16,  1, "2024-01-04"),
    (17, "Ritmos del Mundo",      17,  1, "2024-01-05"),
    (18, "Neon Dreams",           18,  1, "2024-01-03"),
    (19, "Indie Universe",        19,  0, "2024-01-05"),
    (20, "Bass & Afro Fusion",    20,  1, "2024-01-04"),
    (21, "Techno Underground",    26, 1, "2024-01-05"),
    (22, "Nordic Dreamscape",     27, 0, "2024-01-06"),
    (23, "Mumbai After Dark",     28, 1, "2024-01-04"),
    (24, "Afro Street",           29, 1, "2024-01-05"),
    (25, "Electropop Hits",       30, 1, "2024-01-04"),
    (26, "Ambient Journey",       31, 1, "2024-01-06"),
    (27, "Folk Stories",          32, 0, "2024-01-07"),
    (28, "Rio Sessions",          33, 1, "2024-01-03"),
    (29, "Seoul Sunrise",         34, 1, "2024-01-02"),
    (30, "Global Dance Floor",    35, 1, "2024-01-03"),
    (31, "Latin Fever",           36, 1, "2024-01-05"),
    (32, "Jazz & J-Pop Fusion",   37, 1, "2024-01-04"),
    (33, "R&B After Hours",       44, 1, "2024-01-04"),
    (34, "Indie Canvas",          40, 1, "2024-01-06"),
    (35, "K-Pop Universe",        34, 1, "2024-01-02"),
]

SEED_PLAYLIST_SONGS = [
    # Playlist 1 (Late Night Circuits) - electronic
    (1, 1, 1, "2024-01-01"), (1, 2, 2, "2024-01-01"), (1, 3, 3, "2024-01-01"),
    (1, 4, 4, "2024-01-01"), (1, 24,5, "2024-01-02"), (1, 25,6, "2024-01-02"),
    # Playlist 2 (Coding in the Rain) - lo-fi
    (2, 19,1, "2024-01-02"), (2, 20,2, "2024-01-02"), (2, 21,3, "2024-01-02"),
    (2, 5, 4, "2024-01-02"), (2, 7, 5, "2024-01-03"),
    # Playlist 3 (Samba & Beats) - latin + afro
    (3, 10,1, "2024-01-01"), (3, 11,2, "2024-01-01"), (3, 12,3, "2024-01-01"),
    (3, 22,4, "2024-01-01"), (3, 23,5, "2024-01-02"),
    # Playlist 4 (Tokyo Nights) - J/K-Pop
    (4, 8, 1, "2024-01-01"), (4, 9, 2, "2024-01-01"), (4, 29,3, "2024-01-01"),
    (4, 30,4, "2024-01-01"), (4, 31,5, "2024-01-02"),
    # Playlist 5 (Pop Bops 2024) - pop
    (5, 13,1, "2024-01-03"), (5, 14,2, "2024-01-03"), (5, 15,3, "2024-01-03"),
    (5, 16,4, "2024-01-03"),
    # Playlist 6 (Vinyl & Vibes) - indie rock + jazz
    (6, 5, 1, "2024-01-03"), (6, 6, 2, "2024-01-03"), (6, 7, 3, "2024-01-03"),
    (6, 27,4, "2024-01-04"), (6, 28,5, "2024-01-04"),
    # Playlist 7 (Synthwave Sunday)
    (7, 24,1, "2024-01-02"), (7, 25,2, "2024-01-02"), (7, 26,3, "2024-01-02"),
    (7, 19,4, "2024-01-02"), (7, 20,5, "2024-01-03"),
    # Playlist 9 (Hyperion Obsessed)
    (9, 29,1, "2024-01-01"), (9, 30,2, "2024-01-01"), (9, 31,3, "2024-01-01"),
    # Playlist 10 (Jazz After Midnight)
    (10,27,1, "2024-01-03"), (10,28,2, "2024-01-03"), (10,5, 3, "2024-01-04"),
    # Playlist 11 (Rave Essentials)
    (11,1, 1, "2024-01-02"), (11,2, 2, "2024-01-02"), (11,3, 3, "2024-01-02"),
    (11,4, 4, "2024-01-02"), (11,25,5, "2024-01-02"),
    # Playlist 12 (3AM Focus Mode)
    (12,19,1, "2024-01-03"), (12,20,2, "2024-01-03"), (12,21,3, "2024-01-03"),
    (12,37,4, "2024-01-04"),
    # Playlist 14 (R&B & Chill)
    (14,32,1, "2024-01-02"), (14,33,2, "2024-01-02"), (14,13,3, "2024-01-03"),
    (14,15,4, "2024-01-03"),
    # Playlist 15 (Heavy Metal Bible)
    (15,17,1, "2024-01-03"), (15,18,2, "2024-01-03"), (15,6, 3, "2024-01-04"),
    # Playlist 18 (Neon Dreams)
    (18,24,1, "2024-01-03"), (18,25,2, "2024-01-03"), (18,26,3, "2024-01-03"),
    (18,1, 4, "2024-01-04"), (18,2, 5, "2024-01-04"),
    # Playlist 20 (Bass & Afro Fusion)
    (20,1, 1, "2024-01-04"), (20,22,2, "2024-01-04"), (20,23,3, "2024-01-04"),
    (20,3, 4, "2024-01-05"),
    # Playlist 21 (Techno Underground)
    (21,61,1,"2024-01-05"),(21,62,2,"2024-01-05"),(21,1,3,"2024-01-05"),(21,2,4,"2024-01-06"),
    # Playlist 22 (Nordic Dreamscape)
    (22,47,1,"2024-01-06"),(22,48,2,"2024-01-06"),(22,55,3,"2024-01-07"),(22,56,4,"2024-01-07"),
    # Playlist 23 (Mumbai After Dark)
    (23,45,1,"2024-01-04"),(23,37,2,"2024-01-04"),(23,73,3,"2024-01-05"),(23,46,4,"2024-01-05"),
    # Playlist 24 (Afro Street)
    (24,59,1,"2024-01-05"),(24,60,2,"2024-01-05"),(24,22,3,"2024-01-06"),(24,23,4,"2024-01-06"),
    # Playlist 25 (Electropop Hits)
    (25,41,1,"2024-01-04"),(25,42,2,"2024-01-04"),(25,43,3,"2024-01-04"),(25,44,4,"2024-01-05"),
    # Playlist 26 (Ambient Journey)
    (26,55,1,"2024-01-06"),(26,56,2,"2024-01-06"),(26,19,3,"2024-01-07"),(26,70,4,"2024-01-07"),
    # Playlist 27 (Folk Stories)
    (27,57,1,"2024-01-07"),(27,58,2,"2024-01-07"),(27,7,3,"2024-01-08"),(27,5,4,"2024-01-08"),
    # Playlist 28 (Rio Sessions)
    (28,51,1,"2024-01-03"),(28,52,2,"2024-01-03"),(28,53,3,"2024-01-04"),(28,54,4,"2024-01-04"),
    # Playlist 29 (Seoul Sunrise)
    (29,29,1,"2024-01-02"),(29,30,2,"2024-01-02"),(29,31,3,"2024-01-03"),(29,67,4,"2024-01-03"),
    # Playlist 30 (Global Dance Floor)
    (30,61,1,"2024-01-03"),(30,1,2,"2024-01-03"),(30,2,3,"2024-01-03"),(30,3,4,"2024-01-04"),(30,62,5,"2024-01-04"),
    # Playlist 31 (Latin Fever)
    (31,10,1,"2024-01-05"),(31,11,2,"2024-01-05"),(31,12,3,"2024-01-05"),(31,22,4,"2024-01-06"),(31,23,5,"2024-01-06"),
    # Playlist 32 (Jazz & J-Pop Fusion)
    (32,27,1,"2024-01-04"),(32,28,2,"2024-01-04"),(32,74,3,"2024-01-04"),(32,8,4,"2024-01-05"),(32,9,5,"2024-01-05"),
    # Playlist 33 (R&B After Hours)
    (33,32,1,"2024-01-04"),(33,63,2,"2024-01-04"),(33,64,3,"2024-01-05"),(33,71,4,"2024-01-05"),(33,65,5,"2024-01-05"),
    # Playlist 34 (Indie Canvas)
    (34,34,1,"2024-01-06"),(34,35,2,"2024-01-06"),(34,36,3,"2024-01-06"),(34,57,4,"2024-01-07"),(34,75,5,"2024-01-07"),
    # Playlist 35 (K-Pop Universe)
    (35,29,1,"2024-01-02"),(35,30,2,"2024-01-02"),(35,31,3,"2024-01-02"),(35,67,4,"2024-01-03"),(35,8,5,"2024-01-03"),
]


def create_db() -> sqlite3.Connection:
    """Create a fresh in-memory SQLite DB with Tempo seed data."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    conn.executemany("INSERT INTO artists VALUES (?,?,?,?,?,?)", SEED_ARTISTS)
    conn.executemany("INSERT INTO songs VALUES (?,?,?,?,?,?,?,?)", SEED_SONGS)
    conn.executemany("INSERT INTO users VALUES (?,?,?,?,?,?)", SEED_USERS)
    conn.executemany("INSERT INTO streams VALUES (?,?,?,?,?,?,?)", SEED_STREAMS)
    conn.executemany("INSERT INTO playlists VALUES (?,?,?,?,?)", SEED_PLAYLISTS)
    conn.executemany("INSERT INTO playlist_songs VALUES (?,?,?,?)", SEED_PLAYLIST_SONGS)
    conn.commit()
    return conn


def _rows(conn: sqlite3.Connection, sql: str) -> list[dict]:
    """Run SQL and return results as list of dicts."""
    cur = conn.execute(sql)
    return [dict(row) for row in cur.fetchall()]


# ---------------------------------------------------------------------------
# Question + TaskDef dataclasses
# ---------------------------------------------------------------------------

@dataclass
class Question:
    id: str
    text: str
    expected_rows: list[dict]
    order_sensitive: bool
    columns: list[str]


@dataclass
class TaskDef:
    id: str
    name: str
    difficulty: str
    description: str
    questions: list[Question] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Pre-compute expected answers at module load (reference DB)
# ---------------------------------------------------------------------------

_ref = create_db()

# --- EASY ---

_easy_q1_rows = _rows(_ref, """
    SELECT id, title, genre, bpm, mood, duration_sec, release_year
    FROM songs
    WHERE genre = 'Electronic'
""")

_easy_q2_rows = _rows(_ref, """
    SELECT id, name, country, monthly_listeners
    FROM artists
    ORDER BY monthly_listeners DESC, name ASC
    LIMIT 5
""")

_easy_q3_rows = _rows(_ref, """
    SELECT genre, COUNT(*) AS song_count
    FROM songs
    GROUP BY genre
    ORDER BY song_count DESC, genre ASC
""")

_easy_q4_rows = _rows(_ref, """
    SELECT id, username, country, subscription_tier
    FROM users
    WHERE subscription_tier = 'premium'
""")

_easy_q5_rows = _rows(_ref, """
    SELECT subscription_tier, COUNT(*) AS user_count
    FROM users
    GROUP BY subscription_tier
""")

# --- MEDIUM ---

_medium_q1_rows = _rows(_ref, """
    SELECT s.title, COUNT(st.id) AS stream_count
    FROM songs s
    JOIN streams st ON s.id = st.song_id
    GROUP BY s.id, s.title
    ORDER BY stream_count DESC, s.title ASC
    LIMIT 10
""")

_medium_q2_rows = _rows(_ref, """
    SELECT a.name AS artist_name,
           ROUND(100.0 * SUM(st.completed) / COUNT(st.id), 2) AS completion_rate
    FROM artists a
    JOIN songs s ON a.id = s.artist_id
    JOIN streams st ON s.id = st.song_id
    GROUP BY a.id, a.name
    ORDER BY completion_rate DESC, a.name ASC
""")

_medium_q3_rows = _rows(_ref, """
    SELECT source, COUNT(*) AS stream_count
    FROM streams
    GROUP BY source
    ORDER BY stream_count DESC, source ASC
""")

_medium_q4_rows = _rows(_ref, """
    SELECT u.username, COUNT(DISTINCT st.song_id) AS unique_songs
    FROM users u
    JOIN streams st ON u.id = st.user_id
    GROUP BY u.id, u.username
    ORDER BY unique_songs DESC, u.username ASC
    LIMIT 10
""")

_medium_q5_rows = _rows(_ref, """
    SELECT s.mood, COUNT(st.id) AS stream_count
    FROM songs s
    JOIN streams st ON s.id = st.song_id
    WHERE st.completed = 1
    GROUP BY s.mood
    ORDER BY stream_count DESC, s.mood ASC
""")

# --- HARD ---

_hard_q1_rows = _rows(_ref, """
    SELECT s.title, COUNT(st.id) AS stream_count,
           RANK() OVER (PARTITION BY s.genre ORDER BY COUNT(st.id) DESC) AS genre_rank
    FROM songs s
    JOIN streams st ON s.id = st.song_id
    GROUP BY s.id, s.title, s.genre
    ORDER BY s.genre ASC, genre_rank ASC, s.title ASC
""")

_hard_q2_rows = _rows(_ref, """
    SELECT u.username, u.country,
           COUNT(st.id) AS total_streams,
           ROUND(100.0 * SUM(st.completed) / COUNT(st.id), 2) AS completion_rate
    FROM users u
    JOIN streams st ON u.id = st.user_id
    WHERE u.subscription_tier = 'free'
    GROUP BY u.id, u.username, u.country
    HAVING COUNT(st.id) > 5
""")

_hard_q3_rows = _rows(_ref, """
    WITH song_streams AS (
        SELECT song_id, COUNT(*) AS stream_count
        FROM streams
        GROUP BY song_id
    ),
    avg_streams AS (
        SELECT AVG(stream_count) AS avg_count FROM song_streams
    )
    SELECT s.title, s.genre, ss.stream_count
    FROM songs s
    JOIN song_streams ss ON s.id = ss.song_id
    WHERE ss.stream_count > (SELECT avg_count FROM avg_streams)
    ORDER BY ss.stream_count DESC, s.title ASC
""")

_hard_q4_rows = _rows(_ref, """
    SELECT a.name AS artist_name,
           SUM(CASE WHEN st.skipped_at_sec IS NOT NULL THEN 1 ELSE 0 END) AS skip_count,
           COUNT(st.id) AS total_streams,
           ROUND(100.0 * SUM(CASE WHEN st.skipped_at_sec IS NOT NULL THEN 1 ELSE 0 END) / COUNT(st.id), 2) AS skip_rate
    FROM artists a
    JOIN songs s ON a.id = s.artist_id
    JOIN streams st ON s.id = st.song_id
    GROUP BY a.id, a.name
    ORDER BY skip_rate DESC, a.name ASC
""")

_hard_q5_rows = _rows(_ref, """
    SELECT p.name AS playlist_name, u.username, COUNT(ps.song_id) AS song_count
    FROM playlists p
    JOIN users u ON p.user_id = u.id
    JOIN playlist_songs ps ON p.id = ps.playlist_id
    GROUP BY p.id, p.name, u.username
    ORDER BY song_count DESC, p.name ASC
""")

# ---------------------------------------------------------------------------
# Build Task objects
# ---------------------------------------------------------------------------

TASK_EASY = TaskDef(
    id="task_easy",
    name="Easy — Tempo Single-Table Queries",
    difficulty="easy",
    description="Query songs, artists, and users tables using SELECT, WHERE, GROUP BY, ORDER BY, LIMIT.",
    questions=[
        Question("easy_q1",
                 "List all songs in the 'Electronic' genre. Return id, title, genre, bpm, mood, duration_sec, release_year.",
                 _easy_q1_rows, False, ["id", "title", "genre", "bpm", "mood", "duration_sec", "release_year"]),
        Question("easy_q2",
                 "List the top 5 artists by monthly_listeners. Return id, name, country, monthly_listeners.",
                 _easy_q2_rows, True, ["id", "name", "country", "monthly_listeners"]),
        Question("easy_q3",
                 "How many songs are in each genre? Return genre and song_count, ordered by song_count descending.",
                 _easy_q3_rows, True, ["genre", "song_count"]),
        Question("easy_q4",
                 "List all premium users. Return id, username, country, subscription_tier.",
                 _easy_q4_rows, False, ["id", "username", "country", "subscription_tier"]),
        Question("easy_q5",
                 "How many users are on each subscription tier? Return subscription_tier and user_count.",
                 _easy_q5_rows, False, ["subscription_tier", "user_count"]),
    ],
)

TASK_MEDIUM = TaskDef(
    id="task_medium",
    name="Medium — Tempo JOINs and Aggregations",
    difficulty="medium",
    description="Join streams with songs, artists, and users to compute play counts, completion rates, and discovery patterns.",
    questions=[
        Question("medium_q1",
                 "What are the top 10 most streamed songs? Return title and stream_count, ordered by stream_count descending.",
                 _medium_q1_rows, True, ["title", "stream_count"]),
        Question("medium_q2",
                 "What is the stream completion rate per artist? Return artist_name and completion_rate (0–100, 2 decimal places), ordered by completion_rate descending.",
                 _medium_q2_rows, True, ["artist_name", "completion_rate"]),
        Question("medium_q3",
                 "How many streams came from each source? Return source and stream_count, ordered by stream_count descending.",
                 _medium_q3_rows, True, ["source", "stream_count"]),
        Question("medium_q4",
                 "Which users have listened to the most unique songs? Return username and unique_songs, top 10 ordered by unique_songs descending.",
                 _medium_q4_rows, True, ["username", "unique_songs"]),
        Question("medium_q5",
                 "Which moods have the most completed streams? Return mood and stream_count for completed streams only, ordered by stream_count descending.",
                 _medium_q5_rows, True, ["mood", "stream_count"]),
    ],
)

TASK_HARD = TaskDef(
    id="task_hard",
    name="Hard — Tempo Window Functions and CTEs",
    difficulty="hard",
    description="Use window functions, CTEs, and subqueries to uncover viral hits, skip patterns, and listener behavior.",
    questions=[
        Question("hard_q1",
                 "Rank songs by stream count within their genre using a window function. Return title, stream_count, and genre_rank, ordered by genre then genre_rank.",
                 _hard_q1_rows, True, ["title", "stream_count", "genre_rank"]),
        Question("hard_q2",
                 "For free-tier users with more than 5 streams, show their listening engagement. Return username, country, total_streams, and completion_rate (2 decimal places).",
                 _hard_q2_rows, False, ["username", "country", "total_streams", "completion_rate"]),
        Question("hard_q3",
                 "Find songs with above-average stream counts using a CTE. Return title, genre, and stream_count, ordered by stream_count descending.",
                 _hard_q3_rows, True, ["title", "genre", "stream_count"]),
        Question("hard_q4",
                 "Calculate skip rate per artist. Return artist_name, skip_count, total_streams, and skip_rate (0–100, 2 decimal places), ordered by skip_rate descending.",
                 _hard_q4_rows, True, ["artist_name", "skip_count", "total_streams", "skip_rate"]),
        Question("hard_q5",
                 "Which playlists have the most songs? Return playlist_name, username of the creator, and song_count, ordered by song_count descending.",
                 _hard_q5_rows, True, ["playlist_name", "username", "song_count"]),
    ],
)

ALL_TASKS: dict[str, TaskDef] = {
    "task_easy":   TASK_EASY,
    "task_medium": TASK_MEDIUM,
    "task_hard":   TASK_HARD,
}

SCHEMA_DDL = """
Table: artists
  id                INTEGER  - unique artist ID
  name              TEXT     - artist/band name
  country           TEXT     - country of origin
  debut_year        INTEGER  - year of debut
  monthly_listeners INTEGER  - current monthly listener count
  genre             TEXT     - primary genre

Table: songs
  id            INTEGER  - unique song ID
  title         TEXT     - song title
  artist_id     INTEGER  - FK to artists.id
  genre         TEXT     - genre (Electronic, Indie Rock, J-Pop, Latin, Pop, Metal, Lo-fi Hip-hop, Afrobeats, Synth-pop, Jazz Fusion, K-Pop, Alternative, R&B, Indie Pop, Bollywood Fusion)
  bpm           INTEGER  - beats per minute
  mood          TEXT     - Energetic / Dark / Euphoric / Melancholy / Playful / Calm / Focused / Romantic / Joyful / Wistful / Tense / Aggressive / Nostalgic / Dreamy / Uplifting / Sensual / Sad / Cool / Confident / Angry / Cheerful / Quirky
  duration_sec  INTEGER  - track length in seconds
  release_year  INTEGER  - year released

Table: users
  id                INTEGER  - unique user ID
  username          TEXT     - display name
  country           TEXT     - user's country
  subscription_tier TEXT     - 'free' or 'premium'
  joined_year       INTEGER  - year joined Tempo
  age               INTEGER  - user age

Table: streams
  id             INTEGER  - unique stream event ID
  user_id        INTEGER  - FK to users.id
  song_id        INTEGER  - FK to songs.id
  played_at      TEXT     - ISO datetime YYYY-MM-DD HH:MM:SS
  completed      INTEGER  - 1 if listened to end, 0 if skipped
  skipped_at_sec INTEGER  - seconds into track when skipped (NULL if completed)
  source         TEXT     - 'search' / 'playlist' / 'recommendation' / 'radio' / 'artist_page'

Table: playlists
  id         INTEGER  - unique playlist ID
  name       TEXT     - playlist name
  user_id    INTEGER  - FK to users.id (owner)
  is_public  INTEGER  - 1 if public, 0 if private
  created_at TEXT     - YYYY-MM-DD

Table: playlist_songs
  playlist_id INTEGER  - FK to playlists.id
  song_id     INTEGER  - FK to songs.id
  position    INTEGER  - track position in playlist (1-indexed)
  added_at    TEXT     - YYYY-MM-DD when song was added
""".strip()
