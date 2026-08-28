def get_delta_owc(years, ca, cash, mkt, cl, std) -> int:
    """
    Unknown how many years in 10-k added, therefore we specify the last two
    """
    current_owc = (ca[str(years[-1])] - cash[str(years[-1])] - mkt[str(years[-1])] - (cl[str(years[-1])] - std[str(years[-1])]))
    previous_owc = (ca[str(years[-2])] - cash[str(years[-2])] - mkt[str(years[-2])] - (cl[str(years[-2])] - std[str(years[-2])]))
    delta_owc = abs(previous_owc - current_owc)

    return delta_owc