# AUTH TABLE QUERIES

CREATE_AUTH_RECORD = """
INSERT INTO auth (user_id, password_hash)
VALUES (%s, %s)
RETURNING id, user_id, password_hash, created_at, updated_at;
"""

GET_AUTH_BY_USER_ID = """
SELECT id, user_id, password_hash, created_at, updated_at
FROM auth
WHERE user_id = %s;
"""

UPDATE_PASSWORD_HASH = """
UPDATE auth
SET password_hash = %s,
    updated_at = NOW()
WHERE user_id = %s
RETURNING id, user_id, password_hash, created_at, updated_at;
"""

DELETE_AUTH_RECORD = """
DELETE FROM auth
WHERE user_id = %s
RETURNING user_id;
"""

# REFRESH TOKEN QUERIES

CREATE_REFRESH_TOKEN = """
INSERT INTO refresh_tokens (user_id, token, user_agent, expires_at)
VALUES (%s, %s, %s, %s)
RETURNING id, user_id, token, user_agent, created_at, expires_at, is_valid;
"""

GET_REFRESH_TOKEN = """
SELECT id, user_id, token, user_agent, created_at, expires_at, is_valid
FROM refresh_tokens
WHERE token = %s;
"""

GET_REFRESH_TOKENS_BY_USER = """
SELECT id, user_id, token, user_agent, created_at, expires_at, is_valid
FROM refresh_tokens
WHERE user_id = %s
ORDER BY created_at DESC;
"""

INVALIDATE_REFRESH_TOKEN = """
UPDATE refresh_tokens
SET is_valid = FALSE
WHERE token = %s
RETURNING id, user_id, token, is_valid;
"""

INVALIDATE_ALL_REFRESH_TOKENS = """
UPDATE refresh_tokens
SET is_valid = FALSE
WHERE user_id = %s
RETURNING id, token, is_valid;
"""

DELETE_EXPIRED_REFRESH_TOKENS = """
DELETE FROM refresh_tokens
WHERE expires_at < NOW()
RETURNING id;
"""

DELETE_REFRESH_TOKEN = """
DELETE FROM refresh_tokens
WHERE token = %s
RETURNING id;
"""

ROTATE_REFRESH_TOKEN = """
UPDATE refresh_tokens
SET is_valid = FALSE
WHERE token = %s
RETURNING id;
"""