from partial_trueskill.domain import *


winner = SkillBasedRating(mean=1200, variance=150)
loser = SkillBasedRating(mean=1400, variance=40)
test_parameters = Parameters(200, 0)
test_event = Event(1, 'test event', winner, loser, test_parameters)
test_event_half_weight = Event(.5, 'test event', winner, loser, test_parameters)


def test_delta():
    assert test_event.delta == -200


def test_std_dev_of_performances():
    assert round(test_event.std_dev_of_performances, 7) == 322.6453161


def test_z_factor():
    assert round(test_event.z_factor, 7) == -0.6198757


def test_mean_scale():
    assert round(test_event.mean_scale, 7) == 1.2299083


def test_variance_scale():
    assert round(test_event.variance_scale, 7) == 0.7502842


def test_winner_new_mean():
    assert round(standard_mean_update(winner, test_event), 7) == 1285.7689114


def test_loser_new_mean():
    assert round(standard_mean_update(loser, test_event), 7) == 1393.9008774


def test_winner_new_variance():
    assert round(standard_variance_update(winner, test_event), 7) == 137.2999769


def test_loser_new_variance():
    assert round(standard_variance_update(loser, test_event), 7) == 39.7686963


def test_winner_new_mean_for_half_weight_event():
    assert round(standard_mean_update(winner, test_event_half_weight), 7) == round(1200 + (standard_mean_update(winner, test_event) - 1200)/2, 7)


def test_loser_new_mean_for_half_weight_event():
    assert round(standard_mean_update(loser, test_event_half_weight), 7) == round(1400 - (1400 - (standard_mean_update(loser, test_event)))/2, 7)
    loser_copy = copy.copy(loser)
    loser_copy.update_mean(test_event_half_weight)
    assert round(loser_copy.mean, 7) == round(1400 - (1400 - (standard_mean_update(loser, test_event)))/2, 7)


def test_winner_new_variance_for_half_weight_event():
    """
    From equation for sigma**2 on pg11 (except since we are looking for sigma itself we'll sqrt the answer)
    \sqrt{\left(u^{2}+t^{2}\right)\left(1-W\cdot w\frac{u^{2}+t^{2}}{c^{2}}\right)}
    from https://uwaterloo.ca/computational-mathematics/sites/ca.computational-mathematics/files/uploads/files/justin_dastous_research_paper.pdf

    Paste in to https://www.desmos.com/scientific to see calculation
    \sqrt{150^{2}\left(1-.5\cdot0.75028418897755\frac{150^{2}}{322.64531609803356^{2}}\right)}
    """
    assert round(standard_variance_update(winner, test_event_half_weight), 7) == 143.7902703


def test_loser_new_variance_for_half_weight_event():
    """
    Paste in to https://www.desmos.com/scientific to see calculation
    \sqrt{40^{2}\left(1-.5\cdot0.75028418897755\frac{40^{2}}{322.64531609803356^{2}}\right)}
    """
    assert round(standard_variance_update(loser, test_event_half_weight), 7) == 39.8845158
