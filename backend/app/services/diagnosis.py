def build_roadmap(answers: list[int]):
    n = max(len(answers), 1)
    score = round(sum(answers) / n, 3)
    if score < 0.4:
        weakness, weeks = "기초 문장 구성", 24
    elif score < 0.7:
        weakness, weeks = "이어 말하기·전치사", 20
    else:
        weakness, weeks = "유창성·표현 다양성", 16
    return {"score": score, "weakness": weakness, "weeks": weeks}
