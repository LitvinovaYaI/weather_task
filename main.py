import requests
import geocoder
import json
from datetime import datetime, timezone, timedelta


API_KEY = "2f3c65a229bc4a4d4d1b34b5404c9f5b"
URL = "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}"

MAIN_MENU_TEXT = """
1. Определить погоду по названию города
2. Определить погоду по текущем местоположению
3. Узнать историю запросов
4. Очистить историю запросов

0. Выход
"""


def receiving_data_from_api(city_name: str) -> dict:
    """
    Эта функция получает данные с openweathermap API openweathermap по переданному названию города

    Возвращает словарь со множеством данных о погоде

    Проверка на исключения отлавливает проблемы с соединением и остальные, пока неизвестные мне исключения

    """

    try:
        with requests.Session() as session:
            response = session.get(
                URL.format(city_name, API_KEY),
                params={"units": "metric", "lang": "ru"},
                timeout=4,
            )

        if response.ok:
            return response.json()
        elif response.json().get("cod") == "404":
            print("\nГород не найден, попробуйте снова.")
        else:
            return "Произошла ошибка при получении данных."

    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        print("\n_____Проблема с соединением_____")
    except Exception as exp:
        print(exp)


def data_processing(data_from_api: dict) -> dict:
    """
    Данная функция обрабатывает полученные данные из API openweathermap и достает только нужные нам.

    Возвращает словарь необходимых данных для вывода пользователю. Если данные не были получены, то функция
    ничего не вернет.

    Ошибка может быть только в случае, если возникла ошибка при получении данных с API.
    Поэтому при обнаружении ошибки ничего не выводится в данной функции.
    """
    if data_from_api == None:
        return None
    try:
        unix_timestamp = int(data_from_api["dt"])
        unix_timestamp_shift = int(data_from_api["timezone"])

        our_shift_hours = datetime.utcfromtimestamp(unix_timestamp_shift).hour
        our_shift_minutes = datetime.utcfromtimestamp(unix_timestamp_shift).minute

        our_time = datetime.fromtimestamp(
            unix_timestamp - unix_timestamp_shift,
            tz=timezone(timedelta(hours=our_shift_hours, minutes=our_shift_minutes)),
        )

        processed_data = {
            "current_time": str(our_time),
            "city_name": str(data_from_api["name"]),
            "weather": str(data_from_api["weather"][0]["description"]),
            "temp_current": data_from_api["main"]["temp"],
            "temp_feels_like": data_from_api["main"]["feels_like"],
            "wind_speed": data_from_api["wind"]["speed"],
        }

        return processed_data
    except Exception:
        pass


def display_weather_history_list(list_history: list):
    """
    Данная функция выводит в консоль историю прогноза погоды.
    """
    for weather_data in list_history:
        weather_string_output(weather_data)


def weather_string_output(data_from_api: dict):
    """
    Функция получает словарь с нужными данными и составляет строку для вывода пользователю,
    после чего выводит в консоль

    Ничего не возвращает.

    Ошибка может выйти только в случае пустых входных данных.
    Поэтому при обнаружении ошибки ничего не выводится в данной функции.
    """

    if data_from_api == None:
        return None

    try:
        weather_output_format = f"""
        Текущее время: {data_from_api.get("current_time")}
        Название города: {data_from_api.get("city_name")}
        Погодные условия: {data_from_api.get("weather")}
        Текущая температура: {data_from_api.get("temp_current")} градусов по цельсию
        Ощущается как: {data_from_api.get("temp_feels_like")} градусов по цельсию
        Скорость ветра: {data_from_api.get("wind_speed")} м/c
        """
        print(weather_output_format)

    except Exception as exp:
        pass


def getting_weather_by_city_name(city_name: str):
    """
    Вызывается во время того, когда пользователь хочет узнать погоду по названию города.
    Функция объединяет в себе получение данных с API, отбор нужных данных, составление
    необходимого формата вывода и сам вывод информации.

    """
    data_from_api = receiving_data_from_api(city_name)
    necessary_data_from_api = data_processing(data_from_api)
    weather_string_output(necessary_data_from_api)
    recording_history_to_file(necessary_data_from_api)
    input("\nВведите что-нибудь, чтобы продолжить...")


def find_out_location() -> str:
    """
    Функция определяет текущее местоположение по айпи и возвращает название города,
    в котором находится пользователь

    """
    try:
        return geocoder.ip("me").city
    except Exception:
        print("Не удалось определить ваше местоположение, попробуйте позже")


def reading_history_from_file() -> list:
    """
    Функция считывает данные из json, возвращает список словарей(в таком формате сохраняются данные)
    """
    try:
        with open("data.json", "r+") as file:
            data_from_file = json.load(file)
        return data_from_file
    except Exception:
        pass


def clearing_history_from_file():
    """
    Функция перезаписывает файл пустым списком
    """
    with open("data.json", "w") as file:
        file.write(json.dumps([], indent=4, ensure_ascii=False))
    print("\nИстория успешно очищена!")
    input("\nВведите что-нибудь, чтобы продолжить...")


def recording_history_to_file(data: dict):
    """
    Функция получает данные для записи, и если они существуют, то записывает
    Сначала читает сущетвующие данные в файле json, потом к ним добавляет новые из data

    """
    list_to_recorrding = reading_history_from_file()

    if data != None:
        with open("data.json", "w+") as file:
            if list_to_recorrding == "" or list_to_recorrding == None:
                list_to_recorrding = []

            if data != None:
                list_to_recorrding.append(data)
                file.write(json.dumps(list_to_recorrding, indent=4, ensure_ascii=True))


if __name__ == "__main__":
    while True:
        print(MAIN_MENU_TEXT)

        user_action = input("Выберите действие: ").strip()

        if user_action == "0":
            break
        elif user_action == "1":
            city_name = input("\nВведите название города: ").strip()
            getting_weather_by_city_name(city_name)
        elif user_action == "2":
            city_name = find_out_location()
            getting_weather_by_city_name(city_name)
        elif user_action == "3":
            while True:
                count_of_records_to_display = input(
                    "Введите желаемое количество записей для просмотра: "
                ).strip()

                if count_of_records_to_display.isdigit():
                    list_of_data_from_file = reading_history_from_file()

                    if type(list_of_data_from_file) == type(None):
                        print("Записей не было")
                        break

                    list_of_data_from_file.reverse()
                    len_list_of_data = len(list_of_data_from_file)

                    if int(count_of_records_to_display) >= len_list_of_data:
                        display_weather_history_list(list_of_data_from_file)
                    else:
                        display_weather_history_list(
                            list_of_data_from_file[: int(count_of_records_to_display)]
                        )
                    print(f"\nВсего {len_list_of_data} записей.")
                    print(
                        f"Показано {min(len_list_of_data, int(count_of_records_to_display))} записей."
                    )

                    break
                else:
                    print("Вы ввели не корректную запись, попробуйте снова")
            input("\nВведите что-нибудь, чтобы продолжить...")

        elif user_action == "4":
            clearing_history_from_file()
