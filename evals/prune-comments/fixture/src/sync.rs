// ---- helpers ----
pub fn backoff(attempt: u32) -> u64 {
    // Capped at 2^6 because the upstream rate limiter resets every 64s (RFC 6585 §4).
    let n = attempt.min(6);
    // compute the delay
    let s = "// not a comment";
    let _ = s;
    1u64 << n
}
