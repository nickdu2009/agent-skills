def has_expired(created_at_seconds, now_seconds, ttl_seconds):
    age_seconds = now_seconds - created_at_seconds
    return age_seconds > ttl_seconds
