"""
Seed script — remplit la BD avec des données réalistes.

Usage (depuis la racine du projet) :
    python scripts/seed.py
    python scripts/seed.py --users 30 --reviews 15 --clear

Architecture :
  1. Données réalistes hardcodées pour directors / actors / films célèbres.
  2. Faker pour les utilisateurs et les reviews.
  3. Phases séquentielles qui respectent les FK.
  4. Un seul commit à la fin (flush intermédiaires pour les IDs).
"""

import argparse
import asyncio
import random
import sys
import time
from datetime import date
from pathlib import Path

from faker import Faker

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import select

from app.core.config.database import AsyncSessionLocal
from app.core.security.hash_lib import hash_password
from app.modules.actors.model import ActorModel
from app.modules.directors.model import DirectorModel
from app.modules.genres.model import GenreModel
from app.modules.movie_cast.model import MovieCastModel
from app.modules.movie_details.model import MovieDetailModel
from app.modules.movies.enums import MovieStatus
from app.modules.movies.model import MovieModel
from app.modules.reviews.model import ReviewModel
from app.modules.users.model import UserModel

fake = Faker("en_US")

# ─────────────────────────────────────────────────────────────────────────────
#  Static data
# ─────────────────────────────────────────────────────────────────────────────

DIRECTORS = [
    {
        "full_name": "Christopher Nolan",
        "nationality": "British-American",
        "birth_date": date(1970, 7, 30),
    },
    {"full_name": "Quentin Tarantino", "nationality": "American", "birth_date": date(1963, 3, 27)},
    {
        "full_name": "Francis Ford Coppola",
        "nationality": "American",
        "birth_date": date(1939, 4, 7),
    },
    {"full_name": "Martin Scorsese", "nationality": "American", "birth_date": date(1942, 11, 17)},
    {"full_name": "Steven Spielberg", "nationality": "American", "birth_date": date(1946, 12, 18)},
    {"full_name": "David Fincher", "nationality": "American", "birth_date": date(1962, 8, 28)},
    {"full_name": "Ridley Scott", "nationality": "British", "birth_date": date(1937, 11, 30)},
    {"full_name": "James Cameron", "nationality": "Canadian", "birth_date": date(1954, 8, 16)},
    {"full_name": "Frank Darabont", "nationality": "American", "birth_date": date(1959, 1, 28)},
    {"full_name": "Robert Zemeckis", "nationality": "American", "birth_date": date(1952, 5, 14)},
    {"full_name": "Bong Joon-ho", "nationality": "South Korean", "birth_date": date(1969, 9, 14)},
    {
        "full_name": "Alejandro G. Iñárritu",
        "nationality": "Mexican",
        "birth_date": date(1963, 8, 15),
    },
    {"full_name": "Todd Phillips", "nationality": "American", "birth_date": date(1970, 12, 20)},
    {"full_name": "George Miller", "nationality": "Australian", "birth_date": date(1945, 3, 3)},
    {"full_name": "Lana Wachowski", "nationality": "American", "birth_date": date(1965, 6, 21)},
]

ACTORS = [
    {"full_name": "Leonardo DiCaprio", "nationality": "American", "birth_date": date(1974, 11, 11)},
    {"full_name": "Christian Bale", "nationality": "British", "birth_date": date(1974, 1, 30)},
    {"full_name": "Heath Ledger", "nationality": "Australian", "birth_date": date(1979, 4, 4)},
    {
        "full_name": "Joseph Gordon-Levitt",
        "nationality": "American",
        "birth_date": date(1981, 2, 17),
    },
    {"full_name": "Ellen Page", "nationality": "Canadian", "birth_date": date(1987, 2, 21)},
    {
        "full_name": "Matthew McConaughey",
        "nationality": "American",
        "birth_date": date(1969, 11, 4),
    },
    {"full_name": "Anne Hathaway", "nationality": "American", "birth_date": date(1982, 11, 12)},
    {"full_name": "Tom Hanks", "nationality": "American", "birth_date": date(1956, 7, 9)},
    {"full_name": "Morgan Freeman", "nationality": "American", "birth_date": date(1937, 6, 1)},
    {"full_name": "Tim Robbins", "nationality": "American", "birth_date": date(1958, 10, 16)},
    {"full_name": "Marlon Brando", "nationality": "American", "birth_date": date(1924, 4, 3)},
    {"full_name": "Al Pacino", "nationality": "American", "birth_date": date(1940, 4, 25)},
    {"full_name": "Robert De Niro", "nationality": "American", "birth_date": date(1943, 8, 17)},
    {"full_name": "Ray Liotta", "nationality": "American", "birth_date": date(1954, 12, 18)},
    {"full_name": "Brad Pitt", "nationality": "American", "birth_date": date(1963, 12, 18)},
    {"full_name": "Edward Norton", "nationality": "American", "birth_date": date(1969, 8, 18)},
    {"full_name": "John Travolta", "nationality": "American", "birth_date": date(1954, 2, 18)},
    {"full_name": "Uma Thurman", "nationality": "American", "birth_date": date(1970, 4, 29)},
    {"full_name": "Keanu Reeves", "nationality": "Canadian", "birth_date": date(1964, 9, 2)},
    {"full_name": "Laurence Fishburne", "nationality": "American", "birth_date": date(1961, 7, 30)},
    {"full_name": "Carrie-Anne Moss", "nationality": "Canadian", "birth_date": date(1967, 8, 21)},
    {"full_name": "Russell Crowe", "nationality": "Australian", "birth_date": date(1964, 4, 7)},
    {"full_name": "Joaquin Phoenix", "nationality": "American", "birth_date": date(1974, 10, 28)},
    {"full_name": "Jodie Foster", "nationality": "American", "birth_date": date(1962, 11, 19)},
    {"full_name": "Anthony Hopkins", "nationality": "British", "birth_date": date(1937, 12, 31)},
    {"full_name": "Kate Winslet", "nationality": "British", "birth_date": date(1975, 10, 5)},
    {"full_name": "Song Kang-ho", "nationality": "South Korean", "birth_date": date(1967, 1, 17)},
    {"full_name": "Liam Neeson", "nationality": "Irish", "birth_date": date(1952, 6, 7)},
    {"full_name": "Tom Hardy", "nationality": "British", "birth_date": date(1977, 9, 15)},
    {
        "full_name": "Charlize Theron",
        "nationality": "South African",
        "birth_date": date(1975, 8, 7),
    },
    {"full_name": "Cillian Murphy", "nationality": "Irish", "birth_date": date(1976, 5, 25)},
    {"full_name": "Gary Oldman", "nationality": "British", "birth_date": date(1958, 3, 21)},
    {"full_name": "Samuel L. Jackson", "nationality": "American", "birth_date": date(1948, 12, 21)},
]

# Each entry maps to a MovieModel + MovieDetailModel + cast entries.
# director=None → orphan movie (director_id will be NULL).
MOVIES = [
    {
        "title": "Inception",
        "release_year": 2010,
        "duration_minutes": 148,
        "language": "en",
        "status": MovieStatus.RELEASED,
        "director": "Christopher Nolan",
        "genres": ["Action", "Science Fiction", "Thriller"],
        "detail": {
            "synopsis": "A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea into the mind of a CEO.",
            "budget_usd": 160_000_000,
            "box_office_usd": 836_800_000,
            "awards_count": 4,
            "country": "USA",
        },
        "cast": [
            {
                "actor": "Leonardo DiCaprio",
                "role_name": "Dom Cobb",
                "billing_order": 1,
                "is_lead": True,
            },
            {
                "actor": "Joseph Gordon-Levitt",
                "role_name": "Arthur",
                "billing_order": 2,
                "is_lead": False,
            },
            {"actor": "Ellen Page", "role_name": "Ariadne", "billing_order": 3, "is_lead": False},
            {"actor": "Tom Hardy", "role_name": "Eames", "billing_order": 4, "is_lead": False},
        ],
    },
    {
        "title": "The Dark Knight",
        "release_year": 2008,
        "duration_minutes": 152,
        "language": "en",
        "status": MovieStatus.RELEASED,
        "director": "Christopher Nolan",
        "genres": ["Action", "Crime", "Drama"],
        "detail": {
            "synopsis": "When the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
            "budget_usd": 185_000_000,
            "box_office_usd": 1_004_000_000,
            "awards_count": 2,
            "country": "USA",
        },
        "cast": [
            {
                "actor": "Christian Bale",
                "role_name": "Bruce Wayne / Batman",
                "billing_order": 1,
                "is_lead": True,
            },
            {
                "actor": "Heath Ledger",
                "role_name": "The Joker",
                "billing_order": 2,
                "is_lead": False,
            },
            {
                "actor": "Gary Oldman",
                "role_name": "Jim Gordon",
                "billing_order": 3,
                "is_lead": False,
            },
        ],
    },
    {
        "title": "Interstellar",
        "release_year": 2014,
        "duration_minutes": 169,
        "language": "en",
        "status": MovieStatus.RELEASED,
        "director": "Christopher Nolan",
        "genres": ["Adventure", "Drama", "Science Fiction"],
        "detail": {
            "synopsis": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
            "budget_usd": 165_000_000,
            "box_office_usd": 773_000_000,
            "awards_count": 1,
            "country": "USA",
        },
        "cast": [
            {
                "actor": "Matthew McConaughey",
                "role_name": "Cooper",
                "billing_order": 1,
                "is_lead": True,
            },
            {"actor": "Anne Hathaway", "role_name": "Brand", "billing_order": 2, "is_lead": False},
            {"actor": "Cillian Murphy", "role_name": "Mann", "billing_order": 3, "is_lead": False},
        ],
    },
    {
        "title": "Oppenheimer",
        "release_year": 2023,
        "duration_minutes": 180,
        "language": "en",
        "status": MovieStatus.RELEASED,
        "director": "Christopher Nolan",
        "genres": ["Drama", "Thriller"],
        "detail": {
            "synopsis": "The story of J. Robert Oppenheimer and his role in the development of the atomic bomb during World War II.",
            "budget_usd": 100_000_000,
            "box_office_usd": 952_000_000,
            "awards_count": 7,
            "country": "USA",
        },
        "cast": [
            {
                "actor": "Cillian Murphy",
                "role_name": "J. Robert Oppenheimer",
                "billing_order": 1,
                "is_lead": True,
            },
            {
                "actor": "Gary Oldman",
                "role_name": "Harry Truman",
                "billing_order": 2,
                "is_lead": False,
            },
            {
                "actor": "Tom Hardy",
                "role_name": "Leslie Groves",
                "billing_order": 3,
                "is_lead": False,
            },
        ],
    },
    {
        "title": "Pulp Fiction",
        "release_year": 1994,
        "duration_minutes": 154,
        "language": "en",
        "status": MovieStatus.RELEASED,
        "director": "Quentin Tarantino",
        "genres": ["Crime", "Drama", "Thriller"],
        "detail": {
            "synopsis": "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.",
            "budget_usd": 8_000_000,
            "box_office_usd": 213_900_000,
            "awards_count": 1,
            "country": "USA",
        },
        "cast": [
            {
                "actor": "John Travolta",
                "role_name": "Vincent Vega",
                "billing_order": 1,
                "is_lead": True,
            },
            {
                "actor": "Samuel L. Jackson",
                "role_name": "Jules Winnfield",
                "billing_order": 2,
                "is_lead": True,
            },
            {
                "actor": "Uma Thurman",
                "role_name": "Mia Wallace",
                "billing_order": 3,
                "is_lead": False,
            },
            {"actor": "Brad Pitt", "role_name": "Floyd", "billing_order": 4, "is_lead": False},
        ],
    },
    {
        "title": "Django Unchained",
        "release_year": 2012,
        "duration_minutes": 165,
        "language": "en",
        "status": MovieStatus.RELEASED,
        "director": "Quentin Tarantino",
        "genres": ["Action", "Drama"],
        "detail": {
            "synopsis": "With the help of a German bounty hunter, a freed slave sets out to rescue his wife from a brutal Mississippi plantation owner.",
            "budget_usd": 100_000_000,
            "box_office_usd": 425_000_000,
            "awards_count": 2,
            "country": "USA",
        },
        "cast": [
            {
                "actor": "Leonardo DiCaprio",
                "role_name": "Calvin Candie",
                "billing_order": 2,
                "is_lead": False,
            },
            {
                "actor": "Samuel L. Jackson",
                "role_name": "Stephen",
                "billing_order": 3,
                "is_lead": False,
            },
        ],
    },
    {
        "title": "The Godfather",
        "release_year": 1972,
        "duration_minutes": 175,
        "language": "en",
        "status": MovieStatus.RELEASED,
        "director": "Francis Ford Coppola",
        "genres": ["Crime", "Drama"],
        "detail": {
            "synopsis": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
            "budget_usd": 6_000_000,
            "box_office_usd": 250_000_000,
            "awards_count": 3,
            "country": "USA",
        },
        "cast": [
            {
                "actor": "Marlon Brando",
                "role_name": "Vito Corleone",
                "billing_order": 1,
                "is_lead": True,
            },
            {
                "actor": "Al Pacino",
                "role_name": "Michael Corleone",
                "billing_order": 2,
                "is_lead": True,
            },
            {
                "actor": "Robert De Niro",
                "role_name": "Young Vito",
                "billing_order": 3,
                "is_lead": False,
            },
        ],
    },
    {
        "title": "Goodfellas",
        "release_year": 1990,
        "duration_minutes": 146,
        "language": "en",
        "status": MovieStatus.RELEASED,
        "director": "Martin Scorsese",
        "genres": ["Crime", "Drama"],
        "detail": {
            "synopsis": "The story of Henry Hill and his life in the mob, covering his relationship with his wife Karen Hill and his mob partners.",
            "budget_usd": 25_000_000,
            "box_office_usd": 46_800_000,
            "awards_count": 1,
            "country": "USA",
        },
        "cast": [
            {"actor": "Ray Liotta", "role_name": "Henry Hill", "billing_order": 1, "is_lead": True},
            {
                "actor": "Robert De Niro",
                "role_name": "Jimmy Conway",
                "billing_order": 2,
                "is_lead": False,
            },
            {
                "actor": "Al Pacino",
                "role_name": "Tony Montana",
                "billing_order": 3,
                "is_lead": False,
            },
        ],
    },
    {
        "title": "The Wolf of Wall Street",
        "release_year": 2013,
        "duration_minutes": 180,
        "language": "en",
        "status": MovieStatus.RELEASED,
        "director": "Martin Scorsese",
        "genres": ["Comedy", "Crime", "Drama"],
        "detail": {
            "synopsis": "Based on the true story of Jordan Belfort, from his rise to a wealthy stockbroker to his fall involving crime, corruption and the federal government.",
            "budget_usd": 100_000_000,
            "box_office_usd": 392_000_000,
            "awards_count": 0,
            "country": "USA",
        },
        "cast": [
            {
                "actor": "Leonardo DiCaprio",
                "role_name": "Jordan Belfort",
                "billing_order": 1,
                "is_lead": True,
            },
        ],
    },
    {
        "title": "Schindler's List",
        "release_year": 1993,
        "duration_minutes": 195,
        "language": "en",
        "status": MovieStatus.RELEASED,
        "director": "Steven Spielberg",
        "genres": ["Drama", "History"],
        "detail": {
            "synopsis": "During WWII, industrialist Oskar Schindler gradually becomes concerned for his Jewish workforce after witnessing their persecution by the Nazis.",
            "budget_usd": 22_000_000,
            "box_office_usd": 322_000_000,
            "awards_count": 7,
            "country": "USA",
        },
        "cast": [
            {
                "actor": "Liam Neeson",
                "role_name": "Oskar Schindler",
                "billing_order": 1,
                "is_lead": True,
            },
        ],
    },
    {
        "title": "Saving Private Ryan",
        "release_year": 1998,
        "duration_minutes": 169,
        "language": "en",
        "status": MovieStatus.RELEASED,
        "director": "Steven Spielberg",
        "genres": ["Action", "Drama"],
        "detail": {
            "synopsis": "Following the Normandy Landings, a group of U.S. soldiers go behind enemy lines to retrieve a paratrooper whose brothers have been killed in action.",
            "budget_usd": 70_000_000,
            "box_office_usd": 482_000_000,
            "awards_count": 5,
            "country": "USA",
        },
        "cast": [
            {
                "actor": "Tom Hanks",
                "role_name": "Captain Miller",
                "billing_order": 1,
                "is_lead": True,
            },
        ],
    },
    {
        "title": "Fight Club",
        "release_year": 1999,
        "duration_minutes": 139,
        "language": "en",
        "status": MovieStatus.RELEASED,
        "director": "David Fincher",
        "genres": ["Drama", "Thriller"],
        "detail": {
            "synopsis": "An insomniac office worker and a devil-may-care soapmaker form an underground fight club that evolves into something much, much more.",
            "budget_usd": 63_000_000,
            "box_office_usd": 101_200_000,
            "awards_count": 0,
            "country": "USA",
        },
        "cast": [
            {
                "actor": "Brad Pitt",
                "role_name": "Tyler Durden",
                "billing_order": 1,
                "is_lead": True,
            },
            {
                "actor": "Edward Norton",
                "role_name": "The Narrator",
                "billing_order": 2,
                "is_lead": True,
            },
        ],
    },
    {
        "title": "Gladiator",
        "release_year": 2000,
        "duration_minutes": 155,
        "language": "en",
        "status": MovieStatus.RELEASED,
        "director": "Ridley Scott",
        "genres": ["Action", "Adventure", "Drama"],
        "detail": {
            "synopsis": "A former Roman General sets out to exact vengeance against the corrupt emperor who murdered his family and sent him into slavery.",
            "budget_usd": 103_000_000,
            "box_office_usd": 460_000_000,
            "awards_count": 5,
            "country": "UK",
        },
        "cast": [
            {"actor": "Russell Crowe", "role_name": "Maximus", "billing_order": 1, "is_lead": True},
            {
                "actor": "Joaquin Phoenix",
                "role_name": "Commodus",
                "billing_order": 2,
                "is_lead": False,
            },
        ],
    },
    {
        "title": "Alien: Romulus",
        "release_year": 2024,
        "duration_minutes": 119,
        "language": "en",
        "status": MovieStatus.RELEASED,
        "director": "Ridley Scott",
        "genres": ["Horror", "Science Fiction", "Thriller"],
        "detail": {
            "synopsis": "While scavenging a derelict space station, a group of young colonizers come face to face with the most terrifying life form in the universe.",
            "budget_usd": 65_000_000,
            "box_office_usd": 350_000_000,
            "awards_count": 0,
            "country": "USA",
        },
        "cast": [],
    },
    {
        "title": "Titanic",
        "release_year": 1997,
        "duration_minutes": 194,
        "language": "en",
        "status": MovieStatus.RELEASED,
        "director": "James Cameron",
        "genres": ["Drama", "Romance"],
        "detail": {
            "synopsis": "A seventeen-year-old aristocrat falls in love with a kind but poor artist aboard the luxurious, ill-fated R.M.S. Titanic.",
            "budget_usd": 200_000_000,
            "box_office_usd": 2_187_000_000,
            "awards_count": 11,
            "country": "USA",
        },
        "cast": [
            {
                "actor": "Leonardo DiCaprio",
                "role_name": "Jack Dawson",
                "billing_order": 1,
                "is_lead": True,
            },
            {
                "actor": "Kate Winslet",
                "role_name": "Rose DeWitt",
                "billing_order": 2,
                "is_lead": True,
            },
        ],
    },
    {
        "title": "Avatar",
        "release_year": 2009,
        "duration_minutes": 162,
        "language": "en",
        "status": MovieStatus.RELEASED,
        "director": "James Cameron",
        "genres": ["Action", "Adventure", "Science Fiction"],
        "detail": {
            "synopsis": "A paraplegic Marine dispatched to Pandora on a unique mission becomes torn between following his orders and protecting the world he feels is his home.",
            "budget_usd": 237_000_000,
            "box_office_usd": 2_923_000_000,
            "awards_count": 3,
            "country": "USA",
        },
        "cast": [],
    },
    {
        "title": "The Shawshank Redemption",
        "release_year": 1994,
        "duration_minutes": 142,
        "language": "en",
        "status": MovieStatus.RELEASED,
        "director": "Frank Darabont",
        "genres": ["Drama"],
        "detail": {
            "synopsis": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
            "budget_usd": 25_000_000,
            "box_office_usd": 16_000_000,
            "awards_count": 0,
            "country": "USA",
        },
        "cast": [
            {
                "actor": "Tim Robbins",
                "role_name": "Andy Dufresne",
                "billing_order": 1,
                "is_lead": True,
            },
            {
                "actor": "Morgan Freeman",
                "role_name": "Ellis Boyd Redding",
                "billing_order": 2,
                "is_lead": True,
            },
        ],
    },
    {
        "title": "Forrest Gump",
        "release_year": 1994,
        "duration_minutes": 142,
        "language": "en",
        "status": MovieStatus.RELEASED,
        "director": "Robert Zemeckis",
        "genres": ["Comedy", "Drama", "Romance"],
        "detail": {
            "synopsis": "Historical events unfold from the perspective of an Alabama man with an IQ of 75, who witnesses and influences several defining historical moments.",
            "budget_usd": 55_000_000,
            "box_office_usd": 678_000_000,
            "awards_count": 6,
            "country": "USA",
        },
        "cast": [
            {
                "actor": "Tom Hanks",
                "role_name": "Forrest Gump",
                "billing_order": 1,
                "is_lead": True,
            },
        ],
    },
    {
        "title": "The Matrix",
        "release_year": 1999,
        "duration_minutes": 136,
        "language": "en",
        "status": MovieStatus.RELEASED,
        "director": "Lana Wachowski",
        "genres": ["Action", "Science Fiction"],
        "detail": {
            "synopsis": "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.",
            "budget_usd": 63_000_000,
            "box_office_usd": 467_000_000,
            "awards_count": 4,
            "country": "USA",
        },
        "cast": [
            {"actor": "Keanu Reeves", "role_name": "Neo", "billing_order": 1, "is_lead": True},
            {
                "actor": "Laurence Fishburne",
                "role_name": "Morpheus",
                "billing_order": 2,
                "is_lead": False,
            },
            {
                "actor": "Carrie-Anne Moss",
                "role_name": "Trinity",
                "billing_order": 3,
                "is_lead": False,
            },
        ],
    },
    {
        "title": "The Silence of the Lambs",
        "release_year": 1991,
        "duration_minutes": 118,
        "language": "en",
        "status": MovieStatus.RELEASED,
        "director": None,
        "genres": ["Crime", "Drama", "Thriller"],
        "detail": {
            "synopsis": "A young FBI cadet must receive the help of an incarcerated and manipulative cannibal killer to catch another serial killer.",
            "budget_usd": 19_000_000,
            "box_office_usd": 272_000_000,
            "awards_count": 5,
            "country": "USA",
        },
        "cast": [
            {
                "actor": "Jodie Foster",
                "role_name": "Clarice Starling",
                "billing_order": 1,
                "is_lead": True,
            },
            {
                "actor": "Anthony Hopkins",
                "role_name": "Hannibal Lecter",
                "billing_order": 2,
                "is_lead": False,
            },
        ],
    },
    {
        "title": "Parasite",
        "release_year": 2019,
        "duration_minutes": 132,
        "language": "ko",
        "status": MovieStatus.RELEASED,
        "director": "Bong Joon-ho",
        "genres": ["Comedy", "Drama", "Thriller"],
        "detail": {
            "synopsis": "Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.",
            "budget_usd": 11_400_000,
            "box_office_usd": 263_000_000,
            "awards_count": 4,
            "country": "South Korea",
        },
        "cast": [
            {"actor": "Song Kang-ho", "role_name": "Ki-taek", "billing_order": 1, "is_lead": True},
        ],
    },
    {
        "title": "The Revenant",
        "release_year": 2015,
        "duration_minutes": 156,
        "language": "en",
        "status": MovieStatus.RELEASED,
        "director": "Alejandro G. Iñárritu",
        "genres": ["Action", "Adventure", "Drama"],
        "detail": {
            "synopsis": "A frontiersman on a fur trading expedition in the 1820s fights for survival after being mauled by a bear.",
            "budget_usd": 135_000_000,
            "box_office_usd": 533_000_000,
            "awards_count": 3,
            "country": "USA",
        },
        "cast": [
            {
                "actor": "Leonardo DiCaprio",
                "role_name": "Hugh Glass",
                "billing_order": 1,
                "is_lead": True,
            },
            {
                "actor": "Tom Hardy",
                "role_name": "John Fitzgerald",
                "billing_order": 2,
                "is_lead": False,
            },
        ],
    },
    {
        "title": "Joker",
        "release_year": 2019,
        "duration_minutes": 122,
        "language": "en",
        "status": MovieStatus.RELEASED,
        "director": "Todd Phillips",
        "genres": ["Crime", "Drama", "Thriller"],
        "detail": {
            "synopsis": "A mentally troubled stand-up comedian embarks on a downward spiral that leads to the creation of an iconic villain.",
            "budget_usd": 55_000_000,
            "box_office_usd": 1_079_000_000,
            "awards_count": 2,
            "country": "USA",
        },
        "cast": [
            {
                "actor": "Joaquin Phoenix",
                "role_name": "Arthur Fleck / Joker",
                "billing_order": 1,
                "is_lead": True,
            },
            {
                "actor": "Gary Oldman",
                "role_name": "Thomas Wayne",
                "billing_order": 2,
                "is_lead": False,
            },
        ],
    },
    {
        "title": "Mad Max: Fury Road",
        "release_year": 2015,
        "duration_minutes": 120,
        "language": "en",
        "status": MovieStatus.RELEASED,
        "director": "George Miller",
        "genres": ["Action", "Adventure", "Science Fiction"],
        "detail": {
            "synopsis": "In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler in search for her homeland with the aid of a group of female prisoners.",
            "budget_usd": 150_000_000,
            "box_office_usd": 375_000_000,
            "awards_count": 6,
            "country": "Australia",
        },
        "cast": [
            {
                "actor": "Tom Hardy",
                "role_name": "Max Rockatansky",
                "billing_order": 1,
                "is_lead": True,
            },
            {
                "actor": "Charlize Theron",
                "role_name": "Imperator Furiosa",
                "billing_order": 2,
                "is_lead": True,
            },
        ],
    },
    {
        "title": "Avengers: Endgame",
        "release_year": 2019,
        "duration_minutes": 181,
        "language": "en",
        "status": MovieStatus.RELEASED,
        "director": None,
        "genres": ["Action", "Adventure", "Science Fiction"],
        "detail": {
            "synopsis": "After the devastating events of Infinity War, the Avengers assemble once more in order to reverse Thanos's actions and restore balance to the universe.",
            "budget_usd": 356_000_000,
            "box_office_usd": 2_798_000_000,
            "awards_count": 0,
            "country": "USA",
        },
        "cast": [],
    },
    {
        "title": "Blade Runner 2049",
        "release_year": 2017,
        "duration_minutes": 164,
        "language": "en",
        "status": MovieStatus.RELEASED,
        "director": None,
        "genres": ["Drama", "Mystery", "Science Fiction"],
        "detail": {
            "synopsis": "A young blade runner's discovery of a long-buried secret leads him to track down former blade runner Rick Deckard.",
            "budget_usd": 150_000_000,
            "box_office_usd": 260_000_000,
            "awards_count": 2,
            "country": "USA",
        },
        "cast": [],
    },
    {
        "title": "Dune: Part Two",
        "release_year": 2024,
        "duration_minutes": 166,
        "language": "en",
        "status": MovieStatus.RELEASED,
        "director": None,
        "genres": ["Action", "Adventure", "Science Fiction"],
        "detail": {
            "synopsis": "Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family.",
            "budget_usd": 190_000_000,
            "box_office_usd": 714_000_000,
            "awards_count": 0,
            "country": "USA",
        },
        "cast": [
            {
                "actor": "Cillian Murphy",
                "role_name": "Feyd-Rautha Harkonnen",
                "billing_order": 3,
                "is_lead": False,
            },
        ],
    },
    {
        "title": "The Grand Budapest Hotel",
        "release_year": 2014,
        "duration_minutes": 99,
        "language": "en",
        "status": MovieStatus.RELEASED,
        "director": None,
        "genres": ["Adventure", "Comedy", "Drama"],
        "detail": {
            "synopsis": "A writer encounters the owner of an aging European hotel between the wars, whose concierge has written his memoirs.",
            "budget_usd": 25_000_000,
            "box_office_usd": 174_800_000,
            "awards_count": 4,
            "country": "Germany",
        },
        "cast": [
            {
                "actor": "Edward Norton",
                "role_name": "Inspector Henckels",
                "billing_order": 3,
                "is_lead": False,
            },
        ],
    },
    # Upcoming / cancelled entries to exercise all status values
    {
        "title": "The Winds of Change",
        "release_year": 2026,
        "duration_minutes": None,
        "language": "en",
        "status": MovieStatus.UPCOMING,
        "director": "Christopher Nolan",
        "genres": ["Drama", "Thriller"],
        "detail": {
            "synopsis": "A gripping political thriller set against the backdrop of a global crisis that forces one diplomat to make an impossible choice.",
            "budget_usd": 120_000_000,
            "box_office_usd": None,
            "awards_count": 0,
            "country": "USA",
        },
        "cast": [],
    },
    {
        "title": "Echoes of Tomorrow",
        "release_year": 2026,
        "duration_minutes": None,
        "language": "en",
        "status": MovieStatus.UPCOMING,
        "director": "Bong Joon-ho",
        "genres": ["Mystery", "Science Fiction"],
        "detail": {
            "synopsis": "A scientist discovers that fragments of future memories are bleeding into the present, forcing her to confront a catastrophe only she can prevent.",
            "budget_usd": 80_000_000,
            "box_office_usd": None,
            "awards_count": 0,
            "country": "South Korea",
        },
        "cast": [],
    },
    {
        "title": "The Last Expedition",
        "release_year": 2025,
        "duration_minutes": 140,
        "language": "en",
        "status": MovieStatus.CANCELLED,
        "director": "George Miller",
        "genres": ["Adventure", "Drama"],
        "detail": {
            "synopsis": "Production halted after on-location accidents and budget overruns made completion infeasible.",
            "budget_usd": 90_000_000,
            "box_office_usd": None,
            "awards_count": 0,
            "country": "Australia",
        },
        "cast": [],
    },
]

REVIEW_TITLES = [
    "An absolute masterpiece",
    "Completely overrated",
    "Solid but not perfect",
    "One of the best films ever made",
    "Disappointing but watchable",
    "A visual feast",
    "Too long, loses steam",
    "Genuinely moving",
    "Entertaining popcorn movie",
    "Changed my perspective",
    "Worth every minute",
    "Fell asleep halfway through",
    "Instant classic",
    "Nothing special",
    "Surprisingly great",
    "Overhyped blockbuster",
    "A quiet gem",
    "Technically brilliant",
    "Emotionally exhausting (in a good way)",
    "Not for everyone",
]


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _ok(label: str, count: int, elapsed: float) -> None:
    print(f"  \033[32m✓\033[0m {label:<26}  {count:>4} rows  ({elapsed:.2f}s)")


# ─────────────────────────────────────────────────────────────────────────────
#  Seed phases
# ─────────────────────────────────────────────────────────────────────────────


async def _load_genres(session) -> dict[str, GenreModel]:
    result = await session.execute(select(GenreModel))
    return {g.name: g for g in result.scalars().all()}


async def _insert_directors(session) -> dict[str, DirectorModel]:
    t = time.perf_counter()
    rows: list[DirectorModel] = []
    for d in DIRECTORS:
        row = DirectorModel(**d)
        session.add(row)
        rows.append(row)
    await session.flush()
    _ok("directors", len(rows), time.perf_counter() - t)
    return {d.full_name: d for d in rows}


async def _insert_actors(session) -> dict[str, ActorModel]:
    t = time.perf_counter()
    rows: list[ActorModel] = []
    for a in ACTORS:
        row = ActorModel(**a)
        session.add(row)
        rows.append(row)
    # Extra Faker actors to pad the roster
    for _ in range(20):
        row = ActorModel(
            full_name=fake.name(),
            nationality=fake.country(),
            birth_date=fake.date_of_birth(minimum_age=20, maximum_age=75),
        )
        session.add(row)
        rows.append(row)
    await session.flush()
    _ok("actors", len(rows), time.perf_counter() - t)
    return {a.full_name: a for a in rows}


async def _insert_users(session, n_users: int) -> list[UserModel]:
    t = time.perf_counter()

    admin = UserModel(
        email="admin@moviedb.com",
        hashed_password=hash_password("Admin1234!"),
        is_active=True,
        is_admin=True,
    )
    session.add(admin)
    rows: list[UserModel] = [admin]

    regular_pw = hash_password("Moviedb1!")
    seen: set[str] = {"admin@moviedb.com"}
    fake.unique.clear()
    for _ in range(n_users):
        email = fake.unique.email()
        while email in seen:
            email = fake.unique.email()
        seen.add(email)
        user = UserModel(email=email, hashed_password=regular_pw, is_active=True, is_admin=False)
        session.add(user)
        rows.append(user)

    await session.flush()
    _ok("users", len(rows), time.perf_counter() - t)
    return rows


async def _insert_movies(
    session,
    directors: dict[str, DirectorModel],
    actors: dict[str, ActorModel],
    genres: dict[str, GenreModel],
) -> list[MovieModel]:
    t = time.perf_counter()
    movie_rows: list[tuple[MovieModel, dict]] = []

    for data in MOVIES:
        director_obj = directors.get(data["director"]) if data.get("director") else None
        movie = MovieModel(
            title=data["title"],
            release_year=data["release_year"],
            duration_minutes=data.get("duration_minutes"),
            language=data.get("language"),
            status=data["status"],
            director_id=director_obj.id if director_obj else None,
        )
        for genre_name in data.get("genres", []):
            g = genres.get(genre_name)
            if g:
                movie.genres.append(g)
        session.add(movie)
        movie_rows.append((movie, data))

    await session.flush()

    # Details + cast require movie.id
    for movie, data in movie_rows:
        if data.get("detail"):
            session.add(MovieDetailModel(movie_id=movie.id, **data["detail"]))

        for c in data.get("cast", []):
            actor = actors.get(c["actor"])
            if actor is None:
                continue
            session.add(
                MovieCastModel(
                    movie_id=movie.id,
                    actor_id=actor.id,
                    role_name=c["role_name"],
                    billing_order=c["billing_order"],
                    is_lead=c["is_lead"],
                )
            )

    await session.flush()
    _ok("movies + details + cast", len(movie_rows), time.perf_counter() - t)
    return [m for m, _ in movie_rows]


async def _insert_reviews(
    session,
    users: list[UserModel],
    movies: list[MovieModel],
    reviews_per_user: int,
) -> None:
    t = time.perf_counter()
    # Only seed reviews for released movies
    released = [m for m in movies if m.status == MovieStatus.RELEASED]
    count = 0
    reviewed: set[tuple] = set()

    for user in users:
        sample = random.sample(released, min(reviews_per_user, len(released)))
        for movie in sample:
            key = (user.id, movie.id)
            if key in reviewed:
                continue
            reviewed.add(key)
            session.add(
                ReviewModel(
                    user_id=user.id,
                    movie_id=movie.id,
                    rating=random.randint(1, 10),
                    title=random.choice(REVIEW_TITLES) if random.random() > 0.3 else None,
                    body=fake.paragraph(nb_sentences=random.randint(2, 5))
                    if random.random() > 0.2
                    else None,
                    contains_spoilers=random.random() < 0.15,
                )
            )
            count += 1

    await session.flush()
    _ok("reviews", count, time.perf_counter() - t)


async def _clear(session) -> None:
    t = time.perf_counter()
    deleted = 0
    for Model in [
        ReviewModel,
        MovieCastModel,
        MovieDetailModel,
        MovieModel,
        ActorModel,
        DirectorModel,
        UserModel,
    ]:
        rows = (await session.execute(select(Model))).scalars().all()
        for row in rows:
            await session.delete(row)
            deleted += 1
    await session.flush()
    _ok("cleared", deleted, time.perf_counter() - t)


# ─────────────────────────────────────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────────────────────────────────────


async def seed(n_users: int, reviews_per_user: int, clear: bool) -> None:
    t0 = time.perf_counter()
    print()
    print("  \033[1mMovieDB seed\033[0m")
    print("  " + "─" * 46)

    async with AsyncSessionLocal() as session:
        if clear:
            print("  [--clear] wiping existing data …")
            await _clear(session)

        genres = await _load_genres(session)
        if not genres:
            print("  \033[33m⚠  No genres found — run 'make migrate' first.\033[0m")
            return

        print(f"  genres loaded  ({len(genres)}): {', '.join(sorted(genres))}")
        print()

        directors = await _insert_directors(session)
        actors = await _insert_actors(session)
        users = await _insert_users(session, n_users)
        movies = await _insert_movies(session, directors, actors, genres)
        await _insert_reviews(session, users, movies, reviews_per_user)

        await session.commit()

    print()
    print("  " + "─" * 46)
    print(f"  Done in \033[1m{time.perf_counter() - t0:.2f}s\033[0m")
    print()
    print("  \033[1mAdmin\033[0m   admin@moviedb.com  /  Admin1234!")
    print("  \033[1mUsers\033[0m   <faker email>       /  Moviedb1!")
    print()


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Seed the MovieDB database with realistic data.")
    p.add_argument("--users", type=int, default=20, help="Number of regular users (default: 20)")
    p.add_argument("--reviews", type=int, default=8, help="Reviews per user (default: 8)")
    p.add_argument(
        "--clear", action="store_true", help="Wipe existing data before seeding (keeps genres)"
    )
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    asyncio.run(seed(n_users=args.users, reviews_per_user=args.reviews, clear=args.clear))
