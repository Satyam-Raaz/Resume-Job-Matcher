from app.matching.scorer import hybrid_score


def test_full_overlap_scores_higher():
    a = hybrid_score("a", 0.8, ["python", "sql"], ["python", "sql"], 5, 3)
    b = hybrid_score("b", 0.8, ["java"], ["python", "sql"], 5, 3)
    assert a.score > b.score
    assert b.missing_skills == ["python", "sql"]
