# boutique
선택한 세력이 갑자기 영향력이 압도적으로 커진 주식이다.
우선 선택한 일자 범위 동안의 영향력 배열을 받아온다.
이때 영향력은 % 단위여야 한다. 즉 0 이상 100 이하의 유리수여야 한다.
그 다음 그 영향력 배열에서
2보다 작은 모든 원소를 0으로 치환한다.
그리고 첫 번째로 큰 원소 A와 두 번째로 큰 원소 B를 얻는다.
A == B일 수도 있다.

점수: A / B (B가 0일시 점수는 0)

점수가 2보다 커야 검색 창에 노출된다.

점수 계산하는 코드는 다음과 같다.
```py
def ignore_too_small_number(x:float) -> float:
    if x < 2:
        return 0
    else:
        return x


def crushing(powers: list[float])->float:
    if len(powers) < 2:
        return 0
    powers2 = list(map(ignore_too_small_number, powers))
    max_power = max(powers2)
    powers2.remove(max_power)
    max_power2 = max(powers2)
    score = max_power / max_power2 if max_power2 > 0 else 0
    return score
```
