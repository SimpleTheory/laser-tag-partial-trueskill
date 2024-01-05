.. These are examples of badges you might want to add to your README:
   please update the URLs accordingly

    .. image:: https://api.cirrus-ci.com/github/<USER>/laser_tag_partial_trueskill.svg?branch=main
        :alt: Built Status
        :target: https://cirrus-ci.com/github/<USER>/laser_tag_partial_trueskill
    .. image:: https://readthedocs.org/projects/laser_tag_partial_trueskill/badge/?version=latest
        :alt: ReadTheDocs
        :target: https://laser_tag_partial_trueskill.readthedocs.io/en/stable/
    .. image:: https://img.shields.io/coveralls/github/<USER>/laser_tag_partial_trueskill/main.svg
        :alt: Coveralls
        :target: https://coveralls.io/r/<USER>/laser_tag_partial_trueskill
    .. image:: https://img.shields.io/pypi/v/laser_tag_partial_trueskill.svg
        :alt: PyPI-Server
        :target: https://pypi.org/project/laser_tag_partial_trueskill/
    .. image:: https://img.shields.io/conda/vn/conda-forge/laser_tag_partial_trueskill.svg
        :alt: Conda-Forge
        :target: https://anaconda.org/conda-forge/laser_tag_partial_trueskill
    .. image:: https://pepy.tech/badge/laser_tag_partial_trueskill/month
        :alt: Monthly Downloads
        :target: https://pepy.tech/project/laser_tag_partial_trueskill
    .. image:: https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter
        :alt: Twitter
        :target: https://twitter.com/laser_tag_partial_trueskill

.. image:: https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold
    :alt: Project generated with PyScaffold
    :target: https://pyscaffold.org/

|

===========================
Partial Trueskill
===========================


    Open source python implementation of Justin Dastous, `Expanding the TrueSkill Algorithm Using In-Game Events`.

Philosophy of the Paper
------------------------

The idea of the paper is to amend the TrueSkill rating system primarily by doing 2 things:

1. Instead of wins and losses use game events as partial wins and losses to record skill in games with many player substitutions.
2. Create ghost players that amend the ELO difference given certain circumstances to more accurately reflect skill, or to reflect skill given specific circumstances.

   - For example a ghost player can be used to represent the amount of "win probability" added with a home field advantage. This player can be trained over time until they reach a consistent
     rating after which they can be set and added to all relevant games to the home team.

   - A second example would be identifying a player's skill given different playing conditions, like a tennis player playing on clay vs cement.
     In this case the player can have a general rating and a clay rating when they play on clay to track both separately and predict the win/matchmake more accurately.

More detail can be found in the `paper <https://uwaterloo.ca/computational-mathematics/sites/ca.computational-mathematics/files/uploads/files/justin_dastous_research_paper.pdf>`_.

Implementation
---------------
This repo implements the paper using ``Rating`` and ``Event`` objects. The rating objects are anything that could have a
rating (following a Rating interface), whereas the event objects are the specific events used to determine the ratings for these objects.

The different kinds of Rating objects in this module are:

- ``SkillBasedRating``: A simple rating like a player, or a player on clay.
- ``ConstantRating``: A rating that can be set if desired and no longer change, like `home field advantage`.
- ``RateableTotality``: A rating that is made up of other ratings, like a `team`.

You could of course elect to make your own Rating objects with the ``Rating Interface`` if none of these suit your needs.
As for events there is only a single event class, of which if you wish to see the detail please head over to the
`docs <https://laser-tag-partial-trueskill.readthedocs.io/en/latest/index.html>`_,
the `source <https://github.com/SimpleTheory/laser-tag-partial-trueskill/tree/master/src/partial_trueskill>`_,
or the `tests <https://github.com/SimpleTheory/laser-tag-partial-trueskill/tree/master/tests/partial_trueskill>`_.

Usage
------
Please keep in mind that these numbers are made up please calibrate the system to your needs. Additionally, though not shown in the example,
you can include these objects into your own classes for even more versatility.
::

   winner = RateableTotality(
       'winner',
       [
           SkillBasedRating(mean=1100, variance=120),
           SkillBasedRating(mean=1600, variance=150),
           ConstantRating(mean=1400, variance=40, is_set=False),
           ConstantRating(mean=1200, variance=40, is_set=True),
           ConstantRating(mean=1000, variance=0, is_set=True),
       ]
   )
   loser = RateableTotality(
       'loser',
       [
           SkillBasedRating(mean=1000, variance=110),
           SkillBasedRating(mean=1300, variance=130),
           ConstantRating(mean=1100, variance=40, is_set=False),
           ConstantRating(mean=1300, variance=40, is_set=True),
           ConstantRating(mean=1500, variance=0, is_set=True),
       ]
   )
   game_parameters = Parameters(200, 20)
   game_event = Event(1/3, winner, loser, game_parameters, 'shot attempt')

   winner.update_mean_and_variance(game_event)
   loser.update_mean_and_variance(game_event)

Note
====

This project has been set up using PyScaffold 4.4. For details and usage
information on PyScaffold see https://pyscaffold.org/.
