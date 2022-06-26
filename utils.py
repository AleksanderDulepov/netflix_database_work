import sqlite3

from werkzeug.exceptions import abort


# функция анализирует результат запроса в зависимости от кол-ва полученных результатов
def get_result_from_cursor(cursor):
    list = [dict(i) for i in cursor]
    if len(list) == 1:
        return list[0]
    elif len(list) < 1:
        return None
    else:
        return list


# запрос по названию фильма
def get_by_title(title_):
    with sqlite3.connect("netflix.db") as connection:
        # результат запроса в виде обьекта класса Row, который можно преобразовать в словарь
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        query = f"SELECT * " \
                f"FROM netflix " \
                f"WHERE title='{title_}' AND type='Movie' " \
                f"ORDER BY release_year DESC " \
                f"LIMIT 1"

        cursor.execute(query)
        data = get_result_from_cursor(cursor)
        if data is None:
            abort(404, f'Фильмы с названием {title_} не найдены.')
        return data


# запрос по диапазону лет
def get_by_range_years(year_previous, year_last):
    with sqlite3.connect("netflix.db") as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        query = f"SELECT title, release_year " \
                f"FROM netflix " \
                f"WHERE type='Movie' AND release_year BETWEEN {year_previous} AND {year_last}  " \
                f"ORDER BY release_year DESC " \
                f"LIMIT 100"

        cursor.execute(query)
        data = get_result_from_cursor(cursor)
        if data is None:
            abort(404, f'Фильмы, выпущенные между годами {year_previous} и {year_last} не найдены.')
        return data


# запрос по рейтингу
def get_by_rating(groups):
    with sqlite3.connect("netflix.db") as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        query = f"SELECT title, rating, description " \
                f"FROM netflix " \
                f"WHERE rating in ({groups}) " \
                f"ORDER BY release_year DESC " \
                f"LIMIT 100"

        cursor.execute(query)
        data = get_result_from_cursor(cursor)
        if data is None:
            abort(404, f'Фильмы, с рейтингом {groups} не найдены.')
        return data


# запрос по жанру фильма
def get_by_genre(genre_):
    with sqlite3.connect("netflix.db") as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        query = f"SELECT title, description " \
                f"FROM netflix " \
                f"WHERE listed_in LIKE '%{genre_}%' " \
                f"ORDER BY release_year DESC " \
                f"LIMIT 10"

        cursor.execute(query)
        data = get_result_from_cursor(cursor)
        if data is None:
            abort(404, f'Фильмы жанра {genre_} не найдены.')
        return data


# запрос по 2-м актерам
def get_by_actors(actor_first, actor_second):
    with sqlite3.connect("netflix.db") as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        query = f"SELECT `cast` " \
                f"FROM netflix " \
                f"WHERE `cast` LIKE '%{actor_first}%' AND `cast` LIKE '%{actor_second}%'"

        cursor.execute(query)
        data = get_result_from_cursor(cursor)
        if data is None:
            abort(404, f'Актеры {actor_first} и {actor_second} вместе не играли.')

        list_of_actors = []  # список всех актеров из выборки
        for j in data:
            devided_list = (j['cast']).split(", ")  # так как в базе перечень актеров это строка, делаем список
            for k in devided_list:
                if k.lower() not in (actor_first.lower(), actor_second.lower()):
                    list_of_actors.append(k)

        result_list = set()  # список актеров, удовлетворяющих условию
        for actor in list_of_actors:
            if list_of_actors.count(actor) > 2:
                result_list.add(actor)

        if not result_list:
            abort(404, f'Нет актеров, которые играли бы вместе {actor_first} и {actor_second} более 2-х раз')

        return list(result_list)


# запрос по типу, году выпуска и жанру
def get_by_complex_request(type, release_year, genre):
    with sqlite3.connect("netflix.db") as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        query = f"SELECT *" \
                f"FROM netflix " \
                f"WHERE listed_in LIKE '%{genre}%' " \
                f"AND type='{type.capitalize()}' " \
                f"AND release_year={release_year}"

        cursor.execute(query)
        data = get_result_from_cursor(cursor)
        if data is None:
            abort(404, f'Фильмы типа {type}, жанра {genre}, {release_year} года не найдены.')
        return data


# вывод по названию фильма
def output_by_title(title):
    all_results_dict = get_by_title(title)
    output_dict = {
        "title": all_results_dict['title'],
        "country": all_results_dict['country'],
        "release_year": all_results_dict['release_year'],
        "genre": all_results_dict['listed_in'],
        "description": all_results_dict['description'],
    }
    return output_dict


# вывод по типу, году выпуска и жанру
def output_by_complex_request(type_, release_year, genre):
    all_results_list = get_by_complex_request(type_, release_year, genre)
    output_list = []
    # если результат всего одна строка
    if type(all_results_list) != list:
        all_results_list = [all_results_list]

    for i in all_results_list:
        output_list.append({i['title']: i})
    return output_list
