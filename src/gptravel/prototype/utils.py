import datetime
from typing import Dict, List, Tuple, Union

import numpy as np
import openai

from gptravel.core.services.engine import classifier
from gptravel.core.services.geocoder import GeoCoder
from gptravel.core.services.score_builder import ScorerOrchestrator
from gptravel.core.services.scorer import TravelPlanScore
from gptravel.core.travel_planner.travel_engine import TravelPlanJSON


def is_valid_openai_key(openai_key: str) -> bool:
    """
    Checks if the provided OpenAI API key is valid by performing a test request.

    Parameters
    ----------
    openai_key : str
        The OpenAI API key to be tested.

    Returns
    -------
    bool
        True if the OpenAI API key is valid and the test request succeeds,
        False otherwise.

    Raises
    ------
    None

    Examples
    --------
    >>> is_valid_openai_key("<OPENAI_API_KEY>")
    True

    >>> is_valid_openai_key("foo")
    False
    """
    openai.api_key = openai_key

    try:
        openai.Completion.create(engine="davinci", prompt="Hello, World!", max_tokens=5)
    except openai.error.InvalidRequestError:
        return False
    except openai.error.AuthenticationError:
        return False

    return True


def is_departure_before_return(
    departure_date: datetime.date, return_date: datetime.date
) -> bool:
    """
    Parameters
    ----------
    departure_date : np.datetime64
        The date of departure.
    return_date : np.datetime64
        The date of return.

    Returns
    -------
    bool_
        True if the departure date is before or equal to the return date, False otherwise.
    """
    return departure_date <= return_date


def get_score_map(
    travel_plan_json: TravelPlanJSON,
) -> TravelPlanScore:
    """
    Calculates the score map for a given travel plan.

    Parameters
    ----------
    travel_plan_json : TravelPlanJSON
        The JSON representation of the travel plan.

    Returns
    -------
    Dict[str, Dict[str, Union[float, int]]]
        A dictionary containing the score map for the travel plan.
    """
    geo_decoder = GeoCoder()
    zs_classifier = classifier.ZeroShotTextClassifier(True)
    score_container = TravelPlanScore()
    scorers_orchestrator = ScorerOrchestrator(
        geocoder=geo_decoder, text_classifier=zs_classifier
    )
    scorers_orchestrator.run(
        travel_plan_json=travel_plan_json, scores_container=score_container
    )
    return score_container


def get_cities_coordinates(
    cities: Union[List[str], Tuple[str]], destination: str
) -> Dict[str, Tuple]:
    geo_coder = GeoCoder()

    cities_coordinates = {
        city: tuple(coord for coord in geo_coder.location_coordinates(city).values())
        for city in cities
        if geo_coder.country_from_location_name(city).lower() == destination.lower()
    }
    return cities_coordinates


def is_a_country(place: str):
    geo_coder = GeoCoder()
    return geo_coder.is_a_country(place)
