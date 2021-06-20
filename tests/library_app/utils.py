def load_user():
    from django.contrib.auth import get_user_model

    User = get_user_model()
    User.objects.create_superuser("admin", "admin@example.com", "admin")


def clear_books():
    from library_app.models import Book

    Book.objects.all().delete()


def load_books():
    from library_app.models import Book

    """
    Before you try to point it out, yes you are technically correct
    that Dewey Decimal Codes aren't actually numbers. Technically
    speaking, they are string codes that happen to be made of digits.

    You are very clever for pointing this out, but to test that our
    JSON lookups for translatables don't overload built in ones these
    are added in as decimals to help test this, and they thematically fit.

    Also, these examples are purposefully left with blanks or use inconsistent
    assignment to fields, because real world data is messy.
    Completing these so that all books are loaded uniformly should not be done.
    """

    books = [
        {
            "title": {
                "en": "The Princess Bride",
                "de": "Die Prinzessin Braut",
                "fr": "La Princesse à Marier",
                "es": "La Novia Princesa",
            },
            "author": "S. Morgenstern",
            "description": "A gripping (but sometimes boring) tale of adventure! There is a much better abridged version published by W. Goldman",
            "category": {"dewey": 859},
            "number_of_pages": 240,
        },
        {
            "title": {
                "en": "The Grasshopper Lies Heavy",
                "de": "Die Heuschrecke liegt schwer",
            },
            "author": "Hawthorne Abendsen",
            "description": "A tale of an alternate universe where the Allies won World War 2.",
            "category": {"dewey": 837},
            "number_of_pages": 122,
        },
        {
            "title": {
                "en": "Hamster Huey and the Gooey Kablooie",
            },
            "author": "Mabel Barr",
            "description": "Do you think the townsfolk will ever find Hamster Huey's head?",
            "category": {"dewey": 817},
            "number_of_pages": 101,
        },
        {
            "title": {"en": "The Hitchhiker's Guide to the Galaxy"},
            "author": "Megadodo Publications",
            "description": "The standard repository for all knowledge and wisdom",
            "category": {"dewey": 39},  # It should be 039
            "number_of_pages": 2147483647,  # But its probably more
        },
        {
            "title": {
                "tlh": "The Tragedy of Khamlet, Son of the Emperor of Qo'noS",
                "en": "The Tragedy of Hamlet, Prince of Denmark",
            },
            "author": "Wil'yam Sheq'spir",
            "description": {
                "tlh": """qaDelmeH bov tuj pem vIlo'choHQo'.
                    SoH 'IH 'ej belmoH law', 'oH belmoH puS.
                    jar vagh tIpuq DIHo'bogh Sang SuS ro'.
                    'ej ratlhtaHmeH bov tuj leSpoH luvuS.

                    rut tujqu' bochtaHvIS chal mIn Dun qu'.
                    rut DotlhDaj SuD wov HurghmoHmeH, HuvHa'.
                    'ej reH Hoch 'IHvo' Sab Hoch 'IH, net tu'.
                    'u' He choHmo', San jochmo' joq quvHa'.
                """,
                "en": "A thoroughly inferior translation of the Klingon playwrights finest work.",
            },
            "category": {"dewey": 822.33},
            "number_of_pages": 104,
        },
    ]

    # I feel like I'm about to lay an egg.
    # Book, book books, book book boookoook!!
    book_books = []
    for book in books:
        # title = str(book['title'])
        # print(f"Making {title}")
        # b = Book(**book)
        # print(b)

        # import pdb; pdb.set_trace()
        # b.save()
        book_books += [Book(**book)]
    return Book.objects.bulk_create(book_books)


def load_test_books():
    from library_app.models import Book

    books = [
        {
            "title": {
                "en": "A Guide to Python",
                "de": "Eine Anleitung zu Python",
            },
            "author": "G. van Rossum",
            "description": "A good book on learning Python",
            "category": {"dewey": 222},
            "number_of_pages": 100,
        },
        {
            "title": {
                "en": "A Guide to Django",
                "de": "Ein Leitfaden für Django",
            },
            "author": "A. Holovaty & S. Willison",
            "description": "A good book for learning about Django, a very good web framework written in Python.",
            "category": {"dewey": 222},
            "number_of_pages": 100,
        },
        {
            "title": {
                "en": "The Dummies Guide to building some usable Django apps.",
                "de": "Der Dummies-Leitfaden zum Erstellen einiger verwendbarer Django-Apps",
            },
            "author": "S. Spencer",
            "description": "A book on how to cobble together functional apps in Django that work, and aren't terrible.",
            "category": {"dewey": 222},
            "number_of_pages": 100,
        },
    ]

    return Book.objects.bulk_create(Book(**book) for book in books)
