from flask import Flask, jsonify, request, render_template
from werkzeug.exceptions import abort

import utils

app = Flask(__name__)

# json в unicode
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False


# вьюшки запросов:

# главная старница
@app.route("/")
def main_page():
    return render_template("index.html")


# по названию фильма
@app.route("/movie")
def search_by_title():
    title = request.args.get('title', None)
    if title:
        data = utils.output_by_title(title.strip().capitalize())
        return jsonify(data)
    abort(404, 'Параметр не передан.')


# по жанру
@app.route("/genre")
def search_by_genre():
    genre = request.args.get('genre', None)
    if genre:
        data = utils.get_by_genre(genre.strip())
        return jsonify(data)
    abort(404, 'Параметр не передан.')


# по актерам
@app.route("/actors")
def search_by_actors():
    first_actor = request.args.get('first_actor', None)
    second_actor = request.args.get('second_actor', None)
    if first_actor and second_actor:
        data = utils.get_by_actors(first_actor.strip(), second_actor.strip())
        return jsonify(data)
    abort(404, 'Параметры не переданы.')


# по диапазону лет
@app.route("/movie/years_range")
def search_by_years():
    year_begin = request.args.get('year_begin', None)
    year_over = request.args.get('year_over', None)
    if year_begin.isdigit() and year_over.isdigit():
        # на случай ошибки в порядке ввода диапазона лет
        if year_begin < year_over:
            data = utils.get_by_range_years(year_begin, year_over)
        else:
            data = utils.get_by_range_years(year_over, year_begin)
        return jsonify(data)
    abort(404, 'Параметры не переданы или формат введенных данных не соответствует.')


# по типу, году выпуска и жанру
@app.route("/complex")
def search_by_complex():
    type = request.args.get('type', None)
    release_year = request.args.get('release_year', None)
    genre = request.args.get('genre', None)
    if type and release_year.isdigit() and genre:
        data = utils.output_by_complex_request(type, release_year, genre)
        return jsonify(data)
    abort(404, 'Параметры не переданы или формат введенных данных не соответствует.')


# по рейтингу
@app.route("/rating")
def search_by_rating():
    groups = request.args.get('groups', None)
    if groups == "adult":
        choice_groups = "'R','NC-17'"
    elif groups == "children":
        choice_groups = "'G'"
    elif groups == "family":
        choice_groups = "'G', 'PG', 'PG-13'"
    else:
        abort(404, 'Параметр не передан.')

    data = utils.get_by_rating(choice_groups)
    return jsonify(data)


# обработчики ошибок
@app.errorhandler(404)
def empty_request(error):
    return f"{error} Запрос не вернул результатов.", 404


if __name__ == "__main__":
    app.run(debug=True)
