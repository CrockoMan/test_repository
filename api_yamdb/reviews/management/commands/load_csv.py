import csv

from django.apps import apps
from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404

from reviews.models import (User, Category, Genre, Title,
                            Review, Comment)


class Command(BaseCommand):
    def handle(self, **options):
        ErrorsCount = 0
        User.objects.all().delete()
        print('Загрузка пользователей')
        with open(r'static\data\users.csv', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                print(row)
                try:
                    User.objects.get_or_create(id=row[0],
                                               username=row[1],
                                               email=row[2],
                                               role=row[3])
                except Exception as err:
                    print(f'Ошибка загрузки {err}')
                    ErrorsCount = ErrorsCount + 1

        Category.objects.all().delete()
        print('Загрузка категорий')
        with open(r'static\data\category.csv', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                print(row)
                try:
                    Category.objects.get_or_create(id=row[0],
                                                   name=row[1],
                                                   slug=row[2])
                except Exception as err:
                    print(f'Ошибка загрузки {err}')
                    ErrorsCount = ErrorsCount + 1

        Genre.objects.all().delete()
        print('Загрузка жанров')
        with open(r'static\data\genre.csv', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                print(row)
                try:
                    Genre.objects.get_or_create(id=row[0],
                                                name=row[1],
                                                slug=row[2])
                except Exception as err:
                    print(f'Ошибка загрузки {err}')
                    ErrorsCount = ErrorsCount + 1

        Title.objects.all().delete()
        print('Загрузка наименований')
        with open(r'static\data\titles.csv', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                print(row)
                # print(f'Title_Genre = {title_genre[row[0]]}')
                try:
                    category = get_object_or_404(Category, pk=row[3])
                    # genre = get_object_or_404(Genre, pk=title_genre[row[0]])
                    Title.objects.get_or_create(id=row[0],
                                                name=row[1],
                                                year=row[2],
                                                category=category)
                except Exception as err:
                    print(f'Ошибка загрузки {err}')
                    print(f'Category={category}')
                    ErrorsCount = ErrorsCount + 1
                    # print(f'Genre={genre}')
                    # exit()

        Title_Genre = apps.get_model('reviews', 'title_genre')
        Title_Genre.objects.all().delete()
        print('Загрузка связей')
        with open(r'static\data\genre_title.csv', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                print(row)
                try:
                    Title_Genre.objects.get_or_create(id=row[0],
                                                      title_id=row[1],
                                                      genre_id=row[2])
                except Exception as err:
                    print(f'Ошибка загрузки {err}')
                    ErrorsCount = ErrorsCount + 1

        # TitleGenre.objects.all().delete()
        # with open(r'static\data\genre_title.csv', encoding='utf-8') as file:
        #     reader = csv.reader(file)
        #     next(reader)
        #     for row in reader:
        #         TitleGenre.objects.get_or_create(
        #             id=row[0],
        #             title=get_object_or_404(Title, pk=row[1]),
        #             genre=get_object_or_404(Genre, pk=row[2]),
        #         )

        Review.objects.all().delete()
        print('Загрузка отзывов')
        with open(r'static\data\review.csv', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                print(f'\n{row}')
                try:
                    Review.objects.get_or_create(
                        id=row[0],
                        title=get_object_or_404(Title, pk=row[1]),
                        text=row[2],
                        author=get_object_or_404(User, pk=row[3]),
                        score=row[4],
                        pub_date=row[5],
                    )
                except Exception as err:
                    print(f'Ошибка {err}')
                    ErrorsCount = ErrorsCount + 1

        Comment.objects.all().delete()
        print('Загрузка комментариев')
        with open(r'static\data\comments.csv', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                print(row)
                try:
                    Comment.objects.get_or_create(
                        id=row[0],
                        review=get_object_or_404(Review, pk=row[1]),
                        text=row[2],
                        author=get_object_or_404(User, pk=row[3]),
                        pub_date=row[4],
                    )
                except Exception as err:
                    print(f'Ошибка {err}')
                    ErrorsCount = ErrorsCount + 1
        if ErrorsCount:
            print(f'\n Ошибок загруки :{ErrorsCount}')
        else:
            print(f'\n Загрузка завершена, ошибок нет')
