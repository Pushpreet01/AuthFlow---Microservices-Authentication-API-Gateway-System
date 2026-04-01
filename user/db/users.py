CREATE_USER = """
INSERT INTO users (name, email, skill_level)
VALUES (%s, LOWER(%s), %s)
RETURNING id, name, email, skill_level, video_verified, profile_photo, reputation_score, created_at;
"""

GET_USERS = """
SELECT id, name, email, skill_level, video_verified, profile_photo, reputation_score, created_at
FROM users;
"""

GET_USER_BY_EMAIL = """
SELECT id, name, email, skill_level, video_verified, profile_photo, reputation_score, created_at
FROM users
WHERE email = LOWER(%s);
"""


GET_USER_BY_ID = """
SELECT id, name, email, skill_level, video_verified, profile_photo, reputation_score, created_at
FROM users
WHERE id = %s;
"""


UPDATE_USER_PROFILE = """
UPDATE users
SET
    name = COALESCE(%s, name),
    skill_level = COALESCE(%s, skill_level),
    profile_photo = COALESCE(%s, profile_photo),
    video_verified = COALESCE(%s, video_verified)
WHERE id = %s
RETURNING id, name, email, skill_level, video_verified, profile_photo, reputation_score, created_at;
"""

INCREASE_REPUTATION = """
UPDATE users
SET reputation_score = reputation_score + %s
WHERE id = %s
RETURNING id, name, email, profile_photo, reputation_score;
"""


DECREASE_REPUTATION = """
UPDATE users
SET reputation_score = reputation_score - %s
WHERE id = %s
RETURNING id, name, email, profile_photo, reputation_score;
"""


DELETE_USER = """
DELETE FROM users
WHERE id = %s;
"""
