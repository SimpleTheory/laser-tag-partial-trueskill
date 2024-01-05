from partial_trueskill.domain import *


winner = RateableTotality(
    'winner',
    [
        SkillBasedRating(mean=1100, variance=120),
        SkillBasedRating(mean=1600, variance=150),
        SkillBasedRating(mean=1400, variance=40),
    ]
)
loser = RateableTotality(
    'loser',
    [
        SkillBasedRating(mean=1000, variance=110),
        SkillBasedRating(mean=1300, variance=130),
        SkillBasedRating(mean=1100, variance=40),
    ]
)
test_parameters = Parameters(200, 20)
test_event = Event(1,  winner, loser, test_parameters, 'test event')
test_half_weight_event = Event(1 / 2, winner, loser, test_parameters, 'test event 1/2')


def test_delta():
    """
    winner - loser
    """
    assert test_event.delta == 1100 + 1600 + 1400 - (1000 + 1300 + 1100)


def test_RateableTotality_sigma_for_std_dev():
    assert winner.sigma_variance_for_std_dev() == sum([rating.variance ** 2 for rating in winner.ratings])


def test_RateableTotality_beta_count_no_context():
    assert winner.beta_count == len(winner.ratings)
    assert loser.beta_count == len(loser.ratings)

def test_std_dev_of_performances():
    """
    sqrt((beta_cnt + beta_cnt)B**2 + sum(all variances**2))
    """
    assert round(test_event.std_dev_of_performances, 7) == \
           round(
               math.sqrt(
                   (winner.beta_count + loser.beta_count) * test_parameters.beta ** 2 +
                   winner.sigma_variance_for_std_dev() + loser.sigma_variance_for_std_dev()), 7)


def test_z_factor():
    assert round(test_event.z_factor, 7) == round(test_event.delta / test_event.std_dev_of_performances, 7)


def test_mean_scale():
    normal_dist = statistics.NormalDist()
    expected = normal_dist.pdf(test_event.z_factor) / normal_dist.cdf(test_event.z_factor)
    assert round(test_event.mean_scale, 7) == round(expected, 7)


def test_variance_scale():
    expected = test_event.mean_scale * (test_event.mean_scale + test_event.z_factor)
    assert round(test_event.variance_scale, 7) == round(expected, 7)


# <editor-fold desc="New Mean Full Event">
def test_winner_0_new_mean():
    winner_0 = winner.ratings[0]
    expected = winner_0.mean + test_event.weight * test_event.mean_scale * ((winner_0.variance**2 + test_event.parameters.tau**2) / test_event.c)
    assert round(standard_mean_update(winner_0, test_event, won_or_lost=1), 7) == round(expected, 7)

def test_winner_1_new_mean():
    winner_1 = winner.ratings[1]
    expected = winner_1.mean + test_event.weight * test_event.mean_scale * ((winner_1.variance**2 + test_event.parameters.tau**2) / test_event.c)
    assert round(standard_mean_update(winner_1, test_event, won_or_lost=1), 7) == round(expected, 7)

def test_winner_2_new_mean():
    winner_2 = winner.ratings[2]
    expected = winner_2.mean + test_event.weight * test_event.mean_scale * ((winner_2.variance**2 + test_event.parameters.tau**2) / test_event.c)
    assert round(standard_mean_update(winner_2, test_event, won_or_lost=1), 7) == round(expected, 7)
def test_loser_0_new_mean():
    loser_0 = loser.ratings[0]
    expected = loser_0.mean - test_event.weight * test_event.mean_scale * ((loser_0.variance**2 + test_event.parameters.tau**2) / test_event.c)
    assert round(standard_mean_update(loser_0, test_event, won_or_lost=-1), 7) == round(expected, 7)
def test_loser_1_new_mean():
    loser_1 = loser.ratings[1]
    expected = loser_1.mean - test_event.weight * test_event.mean_scale * ((loser_1.variance**2 + test_event.parameters.tau**2) / test_event.c)
    assert round(standard_mean_update(loser_1, test_event, won_or_lost=-1), 7) == round(expected, 7)
def test_loser_2_new_mean():
    loser_2 = loser.ratings[2]
    expected = loser_2.mean - test_event.weight * test_event.mean_scale * ((loser_2.variance**2 + test_event.parameters.tau**2) / test_event.c)
    assert round(standard_mean_update(loser_2, test_event, won_or_lost=-1), 7) == round(expected, 7)

def test_mean_update_method_win():
    winner_copy = copy.copy(winner)
    winner_copy.update_mean(test_event)
    new_ratings = []
    for player in winner.ratings:
        current = player.mean + test_event.weight * test_event.mean_scale * ((player.variance**2 + test_event.parameters.tau**2) / test_event.c)
        new_ratings.append(current)
    assert new_ratings == [rating.mean for rating in winner_copy.ratings]

def test_mean_update_method_loss():
    loser_copy = copy.copy(loser)
    loser_copy.update_mean(test_event)
    new_ratings = []
    for player in loser.ratings:
        current = player.mean - test_event.weight * test_event.mean_scale * ((player.variance**2 + test_event.parameters.tau**2) / test_event.c)
        new_ratings.append(current)
    assert new_ratings == [rating.mean for rating in loser_copy.ratings]


# </editor-fold>

# <editor-fold desc="New Mean Full Variance">
def test_winner_0_new_variance():
    player = winner.ratings[0]
    expected = math.sqrt((player.variance**2 + test_parameters.tau**2) * (1 - test_event.weight * (
        test_event.w * (
                (player.variance ** 2 + test_parameters.tau ** 2) / test_event.c**2
            )
        )
    ))
    assert round(standard_variance_update(player, test_event), 7) == round(expected, 7)
def test_winner_1_new_variance():
    player = winner.ratings[1]
    expected = math.sqrt((player.variance**2 + test_parameters.tau**2) * (1 - test_event.weight * (
        test_event.w * (
                (player.variance ** 2 + test_parameters.tau ** 2) / test_event.c**2
            )
        )
    ))
    assert round(standard_variance_update(player, test_event), 7) == round(expected, 7)
def test_winner_2_new_variance():
    player = winner.ratings[2]
    expected = math.sqrt((player.variance**2 + test_parameters.tau**2) * (1 - test_event.weight * (
        test_event.w * (
                (player.variance ** 2 + test_parameters.tau ** 2) / test_event.c**2
            )
        )
    ))
    assert round(standard_variance_update(player, test_event), 7) == round(expected, 7)
def test_loser_0_new_variance():
    player = loser.ratings[0]
    expected = math.sqrt((player.variance**2 + test_parameters.tau**2) * (1 - test_event.weight * (
        test_event.w * (
                (player.variance ** 2 + test_parameters.tau ** 2) / test_event.c**2
            )
        )
    ))
    assert round(standard_variance_update(player, test_event), 7) == round(expected, 7)
def test_loser_1_new_variance():
    player = loser.ratings[0]
    expected = math.sqrt((player.variance**2 + test_parameters.tau**2) * (1 - test_event.weight * (
        test_event.w * (
                (player.variance ** 2 + test_parameters.tau ** 2) / test_event.c**2
            )
        )
    ))
    assert round(standard_variance_update(player, test_event), 7) == round(expected, 7)
def test_loser_2_new_variance():
    player = winner.ratings[0]
    expected = math.sqrt((player.variance**2 + test_parameters.tau**2) * (1 - test_event.weight * (
        test_event.w * (
                (player.variance ** 2 + test_parameters.tau ** 2) / test_event.c**2
            )
        )
    ))
    assert round(standard_variance_update(player, test_event), 7) == round(expected, 7)

def test_winner_variance_update_method():
    new_winner_variances = []
    for player in winner.ratings:
        expected = math.sqrt((player.variance ** 2 + test_parameters.tau ** 2) * (1 - test_event.weight * (
                test_event.w * (
                (player.variance ** 2 + test_parameters.tau ** 2) / test_event.c ** 2
        )
        )
                                                                                  ))
        new_winner_variances.append(expected)
    winner_copy = winner.__copy__()
    winner_copy.update_variance(test_event)
    assert [rating.variance for rating in winner_copy.ratings] == new_winner_variances
def test_loser_variance_update_method():
    new_loser_variances = []
    for player in loser.ratings:
        expected = math.sqrt((player.variance ** 2 + test_parameters.tau ** 2) * (1 - test_event.weight * (
                test_event.w * (
                (player.variance ** 2 + test_parameters.tau ** 2) / test_event.c ** 2
        )
        )
                                                                                  ))
        new_loser_variances.append(expected)
    loser_copy = loser.__copy__()
    loser_copy.update_variance(test_event)
    assert [rating.variance for rating in loser_copy.ratings] == new_loser_variances


# </editor-fold>
