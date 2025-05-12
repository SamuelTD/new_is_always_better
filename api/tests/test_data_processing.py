import pytest
import pandas as pd
from datetime import datetime
from unittest.mock import patch

from app.utils.data_processing import transform_input
from app.schemas import FilmInput

@pytest.fixture
def sample_input():
    return FilmInput(
        actors=["Cillian Murphy", "Clare Dunne", "Emily Watson"],
        date="2025-04-30T00:00:00",
        directors=["Tim Mielants"],
        editor="Condor Distribution",
        genre=["Drame"],
        langage=["Anglais"],
        length=98,
        nationality=["Irlande", "Belgique", "U.S.A."],
        title="Tu ne mentiras point"
    )

@patch("app.utils.data_processing.get_national_affluence")
@patch("app.utils.data_processing.get_max_average_actor")
@patch("app.utils.data_processing.get_target_encoding")
def test_transform_input_shape(mock_target_encoding, mock_max_actor, mock_affluence, sample_input):
    # Mock des retours
    mock_affluence.return_value = 1234567
    mock_max_actor.return_value = [200, 150, 100]
    mock_target_encoding.return_value = {
        "genre_first_target_transform": 1,
        "genre_second_target_transform": 0.5,
        "genre_third_target_transform": 0.1,
        "langage_first_target_transform": 0.8,
        "langage_second_target_transform": 0.4,
        "langage_third_target_transform": 0.2,
        "nationality_first_target_transform": 0.6,
        "nationality_second_target_transform": 0.3,
        "nationality_third_target_transform": 0.1,
        "directors_first_target_transform": 0.9,
        "directors_second_target_transform": 0.5,
        "directors_third_target_transform": 0.2,
        "actors_first_target_transform": 1.0,
        "actors_second_target_transform": 0.6,
        "actors_third_target_transform": 0.3
    }

    df = transform_input(sample_input)

    # Vérifie que c'est bien un DataFrame
    assert isinstance(df, pd.DataFrame)

    # Vérifie qu'il a exactement 1 ligne
    assert df.shape[0] == 1

    # Vérifie les colonnes attendues (optionnel si fragile)
    expected_columns = [
        'french_prod', 'date', 'editor', 'length', 'number_actors', 'usa_prod', 'japan_prod',
        'national_affluence', 'french_langage', 'english_langage', 'max_average_actor',
        'second_max_average_actor', 'third_max_average_actor', 'nationality_count',
        'germany_prod', 'spain_prod', 'italy_prod', 'uk_prod', 'language_count',
        'genre_first_target_transform', 'genre_second_target_transform', 'genre_third_target_transform',
        'langage_first_target_transform', 'langage_second_target_transform', 'langage_third_target_transform',
        'nationality_first_target_transform', 'nationality_second_target_transform', 'nationality_third_target_transform',
        'directors_first_target_transform', 'directors_second_target_transform', 'directors_third_target_transform',
        'actors_first_target_transform', 'actors_second_target_transform', 'actors_third_target_transform'
    ]
    assert list(df.columns) == expected_columns

    # Vérifie quelques valeurs clefs
    row = df.iloc[0]
    assert row["usa_prod"] == 1
    assert row["english_langage"] == 1
    assert row["number_actors"] == 3
    assert row["max_average_actor"] == 200
    assert row["national_affluence"] == 1234567

def test_num_list_col_empty_list_handling():
    from app.utils.data_processing import num_list_col
    assert num_list_col(["no value"]) == 0
    assert num_list_col(["something"]) == 1
    assert num_list_col([]) == 0
