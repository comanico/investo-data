def get_delta_owc(years, ca, cash, mkt, cl, std) -> int:
    """
    Unknown how many years in 10-k added, therefore we specify the last two
    """
    current_owc = (ca[years[-1]] - cash[years[-1]] - mkt[years[-1]] - (cl[years[-1]] - std[years[-1]]))
    previous_owc = (ca[years[-2]] - cash[years[-2]] - mkt[years[-2]] - (cl[years[-2]] - std[years[-2]]))
    delta_owc = abs(previous_owc - current_owc)

    return delta_owc