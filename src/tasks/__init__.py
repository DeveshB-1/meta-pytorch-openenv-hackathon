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
