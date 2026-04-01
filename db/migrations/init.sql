-- USERS
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    skill_level VARCHAR(20) NOT NULL DEFAULT 'beginner',
    video_verified BOOLEAN DEFAULT FALSE,
    profile_photo TEXT,
    reputation_score INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- AUTH TABLE
CREATE TABLE IF NOT EXISTS auth (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- REFRESH TOKENS
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    token TEXT NOT NULL,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    is_valid BOOLEAN DEFAULT TRUE
);

-- CLUBS
CREATE TABLE IF NOT EXISTS clubs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    city VARCHAR(100) DEFAULT 'Calgary',
    cost_per_hour NUMERIC(10,2) NOT NULL,     -- base cost per hour
    guest_fee NUMERIC(10,2) DEFAULT 0,        -- extra cost per non-member
    created_at TIMESTAMP DEFAULT NOW()
);

-- ROOMS
CREATE TABLE IF NOT EXISTS rooms (
    id SERIAL PRIMARY KEY,
    host_id INT REFERENCES users(id) ON DELETE CASCADE,
    club_id INT REFERENCES clubs(id),
    date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    room_type VARCHAR(10) NOT NULL DEFAULT 'singles', -- singles/doubles
    required_skill VARCHAR(20) NOT NULL,
    total_cost NUMERIC(10,2) NOT NULL,                -- total cost of booking
    cost_per_person NUMERIC(10,2) NOT NULL,           -- calculated per participant
    max_players INT NOT NULL CHECK (max_players >= 2),
    current_players INT NOT NULL DEFAULT 1,           -- people currently joined (host + others)
    pre_registered_players INT NOT NULL DEFAULT 0,    -- friends host already has joined
    description TEXT,                                 -- host can describe event
    guests_allowed BOOLEAN DEFAULT TRUE,              -- can guests join
    members_only BOOLEAN DEFAULT FALSE,               -- only club members allowed
    verified BOOLEAN DEFAULT FALSE,                   -- host verified room
    cancellation_deadline TIMESTAMP,                  -- last moment a participant can cancel
    status VARCHAR(20) NOT NULL DEFAULT 'open',      -- open/closed/cancelled
    created_at TIMESTAMP DEFAULT NOW()
);

-- ROOM PARTICIPANTS
CREATE TABLE IF NOT EXISTS room_participants (
    id SERIAL PRIMARY KEY,
    room_id INT REFERENCES rooms(id) ON DELETE CASCADE,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    num_guests INT DEFAULT 0,                  -- guests brought by participant
    is_member BOOLEAN DEFAULT TRUE,           -- club member or not
    additional_fee NUMERIC(10,2) DEFAULT 0,   -- extra for non-members or guests
    cost_share NUMERIC(10,2) NOT NULL,        -- final amount participant pays
    joined_at TIMESTAMP DEFAULT NOW(),
    is_host BOOLEAN DEFAULT FALSE,
    UNIQUE(room_id, user_id)
);

-- REPUTATION EVENTS
CREATE TABLE IF NOT EXISTS reputation_events (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    event_type VARCHAR(50),
    points INT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

--users buy points -> 10 points -> $1 our app deals with points transactions for room bookings and refunds. 
--the user can convert points to dollars and withdraw in the wallet, so we dont make any payments for 
--every booking and refund, there is just a single service that deals with real money.

-- USER POINTS WALLET
points_wallet (
    id SERIAL PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    points INT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- POINTS TRANSACTIONS
CREATE TABLE points_ledger (
    id BIGSERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    change_amount BIGINT NOT NULL,               -- + or -
    balance_after BIGINT NOT NULL,               -- snapshot
    type VARCHAR(50) NOT NULL,                   -- booking, refund, bonus, admin_adjustment, convert_to_money
    reference_id VARCHAR(255),                   -- booking_id, refund_id etc
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- MONEY TRANSACTIONS
CREATE TABLE money_ledger (
    id BIGSERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    transaction_type VARCHAR(20) NOT NULL,   -- deposit, withdrawal
    amount_cents BIGINT NOT NULL,           -- real money in cents ($10 = 1000)
    points_amount BIGINT NOT NULL,          -- points associated with this conversion
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending, success, failed
    provider VARCHAR(50),                   -- stripe, manual, test_mode
    provider_txn_id VARCHAR(255),           -- stripe charge id etc
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);
