class Constants:
    L_AVG_TRADE_PRICE=0
    """
    atad.p의 평균거래단가 key
    """

    L_HAVING_WEIGHT=1
    """
    atad.p의 보유비중 key
    """

    L_INFLUENCE=2
    """
    atad.p의 영향력 key
    """

    L_DIRECTION=3
    """
    atad.p의 방향 정보 key
    """

    K_CHART=4
    """
    data.p의 주식일봉차트 key
    """

    K_BUY=5
    """
    data.p의 매수정보 key
    """

    K_SELL=6
    """
    data.p의 매도정보 key
    """

    K_PUBLIC_STOCK=7
    """
    data.p의 유통주식수 key
    """

    K_NAME=8
    """
    data.p의 종목명 key
    """

    K_KOSPI_OR_KOSDAQ=11
    """
    data.p의 KOSPI/KOSDAQ 구분 key
    """

    M_KOSPI=9
    M_KOSDAQ=10

    PATH_DATAP = 'data.p'

    AUTO_SAVE_INTERVAL = 49
    """data.p를 몇 skip되지 않은 데이터 iteration마다 자동 저장할지 정합니다.

    자동 저장을 비활성화하고 싶을 경우 0을 입력하세요.

    2401 ** 0.5 == 49 가 권장 값입니다. 자동 저장 간격을 N의 제곱근으로 잡을 경우
    자동 저장의 시간 복잡도가 O(N**1.5)가 됩니다.
    """

    PATH_ATADP = 'atad.p'

    WINDOWTITLE = "세력모니터 240922"

    VOLUMETOPN = 3

    IDX_81_CLOSE=0

    class IvstIdx:
        """
        투자자별 index
        """
        PERSON=0
        FORIENGER=1
        ORG=2

    SAVEDIR = 'C:\\KiwoomHero4\\temp'
    """
    영웅문4 관심종목 저장 경로
    """

    MAXSTOCK = 100
    """
    한 번에 저장할 수 있는 관심종목의 최대 개수
    """
