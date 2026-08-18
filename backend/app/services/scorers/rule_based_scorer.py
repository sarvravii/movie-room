def score_movie(positive_swipes: int, total_swipes: int, total_participants: int) -> float:
    """Group agreement score for a movie, in [0, 1].

    Caller is expected to only call this for movies with total_swipes >= 1;
    untouched movies are filtered out upstream, not scored as 0 here.

    total_swipes is accepted (not just positive_swipes) so future scorers in
    this same swappable slot can factor in swipe coverage/confidence without
    changing the call site — this rule-based version doesn't use it.
    """
    if total_participants <= 0:
        return 0.0
    return positive_swipes / total_participants
