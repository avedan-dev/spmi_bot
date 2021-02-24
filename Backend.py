import json
import requests
import psycopg2
import re

con = psycopg2.connect(
    database="#",
    user="#",
    password="#",
    host="#",
    port="5432"
)

sol = ['', '', '']

weekdays = {
    1: 'Понедельник',
    2: 'Вторник',
    3: 'Среда',
    4: 'Четверг',
    5: 'Пятница',
    6: 'Суббота',
    7: 'Воскресенье',
}


# Вносит в базу данных группу и ее id
def izm(ids, groups):
    cur = con.cursor()
    sol[0] = str(ids)
    sol[1] = "'" + groups + "'"
    sol[2] = str(get_group_id(groups))
    cur.execute('SELECT "id" FROM id WHERE id=' + sol[0])
    if not cur.fetchall():
        cur.execute(
            f'INSERT into id (id, группа, "Group_Id") VALUES ({sol[0]} , {str(sol[1])}, {str(sol[1])})')
    else:
        cur.execute(
            'UPDATE id SET (группа, "Group_Id")=({str(sol[1])}, {str(sol[2])}) WHERE id={sol[0]}')
    con.commit()


# Возвращает group_id из базы данных по id
def output(ids):
    try:
        cur = con.cursor()
    except Exception as e:
        con = psycopg2.connect(
            database="d1ktnr7kc3j3m6",
            user="nxbilgtcbjjkuk",
            password="376e9fed7cc201d23a218688299a4858836406b6811327d1d340443ed38e49f8",
            host="ec2-54-246-84-100.eu-west-1.compute.amazonaws.com",
            port="5432"
        )
        cur = con.cursor()
    ids = str(ids)
    cur.execute(f'SELECT ("Group_Id") FROM id WHERE id={ids}')
    con.commit()
    s = str(cur.fetchall())
    s = re.sub(r'[^A-zА-я0-9-]', '', s)
    s = s.replace(']', '')
    s = s.replace('[', '')
    return s


# Получает расписание с сайта со start_date по finish_date
def get_schedule(group_id, start_date, finish_date):
    url = "http://raspisanie.spmi.ru/api/schedule/group/" + group_id + '?start=' + start_date + '&finish=' + finish_date
    response = requests.get(url)
    todos = json.loads(response.text)
    s = ''
    s_old = ''
    if todos:
        day = todos[0]['dayOfWeek']
        s += weekdays[todos[0]['dayOfWeek']] + '\n'
        for todo in todos:
            if day == todo['dayOfWeek']:
                # не пишем день
                pass
            else:
                # пишем
                s += '\n' + (weekdays[todo['dayOfWeek']])+'\n'
                day = todo['dayOfWeek']
            if todo['auditorium'] == 'D0':
                todo['auditorium'] = ''
            else:
                todo['auditorium'] = '№' + todo['auditorium']
            if todo["lecturer"] == '!Вакансия':
                todo["lecturer"] = ''
            if todo["subGroup"] is None:
                todo["subGroup"] = ''
            new_les = (todo["beginLesson"] + '-' + todo["endLesson"] + ' ' + ' ' + todo[
                "discipline"] + ' ' + todo["kindOfWork"] + ' ' + todo['auditorium'] + '\n' + todo[
                "lecturer"] + todo["subGroup"] + '\n')
            if s_old != new_les:
                s += new_les
            s_old = new_les
        return s
    else:
        return 'Пар нет'


# Получает group_id с сайта горного по названию группы
def get_group_id(group):
    s = 'http://raspisanie.spmi.ru/api/search?term=' + group + '&type=group'
    response = requests.get(s)
    todo = json.loads(response.text)
    if todo:
        return todo[0]['id']
    else:
        return 'Ошибка, такой группы нет'


# Возвращает list id всех пользователей бота
def messages_id():
    ids = []
    cur = con.cursor()
    cur.execute('SELECT "id" FROM id')
    con.commit()
    s = cur.fetchall()
    for i in range(len(s)):
        ids.append(s[i][0])
    return ids
