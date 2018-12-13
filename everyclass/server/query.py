"""
查询相关函数
"""
import elasticapm
from flask import Blueprint, current_app as app, escape, flash, redirect, render_template, request, url_for
from werkzeug.wrappers import Response

from .utils.rpc import HttpRpc

query_blueprint = Blueprint('query', __name__)


@query_blueprint.route('/query', methods=['GET', 'POST'])
def query():
    """
    All in one 搜索入口，可以查询学生、老师、教室，然后跳转到具体资源页面

    正常情况应该是 post 方法，但是也兼容 get 防止意外情况，提高用户体验

    埋点：
    - `query_resource_type`, 查询类型: classroom, single_student, single_teacher, people, or nothing.
    - `query_type`（原 `ec_query_method`）, 查询方式: by_name, by_student_id, by_teacher_id, by_room_name, other
    """

    # if under maintenance, return to maintenance.html
    if app.config["MAINTENANCE"]:
        return render_template("maintenance.html")

    # call api-server to search
    with elasticapm.capture_span('rpc_search'):
        rpc_result = HttpRpc.call_with_error_handle('{}/v1/search/{}'.format(app.config['API_SERVER'],
                                                                             request.values.get('id')))
        if isinstance(rpc_result, Response):
            return rpc_result
        api_response = rpc_result

    # render different template for different resource types
    if len(api_response['room']) >= 1:
        # classroom
        # we will use service name to filter apm document first, so it's not required to add service name prefix here
        elasticapm.tag(query_resource_type='classroom')
        return redirect('/classroom/{}/{}'.format(api_response['room'][0]['rid'],
                                                  api_response['room'][0]['semester'][-1]))
    elif len(api_response['student']) == 1 and len(api_response['teacher']) == 0:
        # only one student
        elasticapm.tag(query_resource_type='single_student')
        if len(api_response['student'][0]['semester']) < 1:
            flash('没有可用学期')
            return redirect(url_for('main.main'))
        return redirect('/student/{}/{}'.format(api_response['student'][0]['sid'],
                                                api_response['student'][0]['semester'][-1]))
    elif len(api_response['teacher']) == 1 and len(api_response['student']) == 0:
        # only one teacher
        elasticapm.tag(query_resource_type='single_teacher')
        if len(api_response['teacher'][0]['semester']) < 1:
            flash('没有可用学期')
            return redirect(url_for('main.main'))
        return redirect('/teacher/{}/{}'.format(api_response['teacher'][0]['tid'],
                                                api_response['teacher'][0]['semester'][-1]))
    elif len(api_response['teacher']) >= 1 or len(api_response['student']) >= 1:
        # multiple students, multiple teachers, or mix of both
        elasticapm.tag(query_resource_type='multiple_people')
        return render_template('people_same_name.html',
                               students_count=len(api_response['student']),
                               students=api_response['student'],
                               teachers_count=len(api_response['teacher']),
                               teachers=api_response['teacher'])
    else:
        elasticapm.tag(query_resource_type='nothing')
        flash('没有找到任何有关 {} 的信息，如果你认为这不应该发生，请联系我们。'.format(escape(request.values.get('id'))))
        return redirect(url_for('main.main'))


@query_blueprint.route('/student/<string:url_sid>/<string:url_semester>')
def get_student(url_sid, url_semester):
    """学生查询"""
    from everyclass.server.db.dao import get_privacy_settings
    from everyclass.server.tools import lesson_string_to_dict

    with elasticapm.capture_span('rpc_query_student'):
        rpc_result = HttpRpc.call_with_error_handle('{}/v1/student/{}/{}'.format(app.config['API_SERVER'],
                                                                                 url_sid,
                                                                                 url_semester),
                                                    params={'week_string': 'true', 'other_semester': 'true'})
        if isinstance(rpc_result, Response):
            return rpc_result
        api_response = rpc_result

    with elasticapm.capture_span('process_rpc_result'):
        courses = dict()
        for each_class in api_response['course']:
            day, time = lesson_string_to_dict(each_class['lesson'])
            if (day, time) not in courses:
                courses[(day, time)] = list()
            courses[(day, time)].append(dict(name=each_class['name'],
                                             teacher=_teacher_list_fix(each_class['teacher']),
                                             week=each_class['week_string'],
                                             classroom=each_class['room'],
                                             classroom_id=each_class['rid'],
                                             cid=each_class['cid']))

    empty_5, empty_6, empty_weekend = _empty_column_check(courses)

    available_semesters = _semester_calculate(url_semester, api_response['semester_list'])

    # 隐私设定
    # Available privacy settings: "show_table_on_page", "import_to_calender", "major"
    with elasticapm.capture_span('get_privacy_settings', span_type='db.mysql'):
        privacy_settings = get_privacy_settings(api_response['sid'])

    # privacy on
    if "show_table_on_page" in privacy_settings:
        return render_template('student_blocked.html',
                               name=api_response['name'],
                               falculty=api_response['deputy'],
                               class_name=api_response['class'],
                               sid=url_sid,
                               available_semesters=available_semesters,
                               no_import_to_calender=True if "import_to_calender" in privacy_settings else False,
                               current_semester=url_semester)

    # privacy off
    return render_template('student.html',
                           name=api_response['name'],
                           falculty=api_response['deputy'],
                           class_name=api_response['class'],
                           sid=url_sid,
                           classes=courses,
                           empty_wkend=empty_weekend,
                           empty_6=empty_6,
                           empty_5=empty_5,
                           available_semesters=available_semesters,
                           current_semester=url_semester)


@query_blueprint.route('/teacher/<string:url_tid>/<string:url_semester>')
def get_teacher(url_tid, url_semester):
    """老师查询"""
    from everyclass.server.tools import lesson_string_to_dict

    with elasticapm.capture_span('rpc_query_student'):
        rpc_result = HttpRpc.call_with_error_handle('{}/v1/teacher/{}/{}'.format(app.config['API_SERVER'],
                                                                                 url_tid,
                                                                                 url_semester),
                                                    params={'week_string': 'true', 'other_semester': 'true'})
        if isinstance(rpc_result, Response):
            return rpc_result
        api_response = rpc_result

    with elasticapm.capture_span('process_rpc_result'):
        courses = dict()
        for each_class in api_response['course']:
            day, time = lesson_string_to_dict(each_class['lesson'])
            if (day, time) not in courses:
                courses[(day, time)] = list()
            courses[(day, time)].append(dict(name=each_class['name'],
                                             week=each_class['week_string'],
                                             classroom=each_class['room'],
                                             classroom_id=each_class['rid'],
                                             cid=each_class['cid']))

    empty_5, empty_6, empty_weekend = _empty_column_check(courses)

    available_semesters = _semester_calculate(url_semester, api_response['semester_list'])

    return render_template('teacher.html',
                           name=api_response['name'],
                           falculty=api_response['unit'],
                           title=api_response['title'],
                           tid=url_tid,
                           classes=courses,
                           empty_wkend=empty_weekend,
                           empty_6=empty_6,
                           empty_5=empty_5,
                           available_semesters=available_semesters,
                           current_semester=url_semester)


@query_blueprint.route('/classroom/<string:url_rid>/<string:url_semester>')
def get_classroom(url_rid, url_semester):
    """教室查询"""
    from everyclass.server.tools import lesson_string_to_dict

    with elasticapm.capture_span('rpc_query_student'):
        rpc_result = HttpRpc.call_with_error_handle('{}/v1/room/{}/{}'.format(app.config['API_SERVER'],
                                                                              url_rid,
                                                                              url_semester),
                                                    params={'week_string': 'true', 'other_semester': 'true'})
        if isinstance(rpc_result, Response):
            return rpc_result
        api_response = rpc_result

    with elasticapm.capture_span('process_rpc_result'):
        courses = dict()
        for each_class in api_response['course']:
            day, time = lesson_string_to_dict(each_class['lesson'])
            if (day, time) not in courses:
                courses[(day, time)] = list()
            courses[(day, time)].append(dict(name=each_class['name'],
                                             week=each_class['week_string'],
                                             teacher=each_class['teacher'],
                                             location=each_class['room'],
                                             cid=each_class['cid']))

    empty_5, empty_6, empty_weekend = _empty_column_check(courses)

    available_semesters = _semester_calculate(url_semester, api_response['semester_list'])

    return render_template('room.html',
                           name=api_response['name'],
                           campus=api_response['campus'],
                           building=api_response['building'],
                           rid=url_rid,
                           classes=courses,
                           empty_wkend=empty_weekend,
                           empty_6=empty_6,
                           empty_5=empty_5,
                           available_semesters=available_semesters,
                           current_semester=url_semester)


@query_blueprint.route('/course/<string:url_cid>/<string:url_semester>')
def get_course(url_cid: str, url_semester: str):
    """课程查询"""

    from everyclass.server.tools import get_time_chinese, get_day_chinese, lesson_string_to_dict, teacher_list_to_str

    with elasticapm.capture_span('rpc_query_course'):
        rpc_result = HttpRpc.call_with_error_handle('{}/v1/course/{}/{}'.format(app.config['API_SERVER'],
                                                                                url_cid,
                                                                                url_semester),
                                                    params={'week_string': 'true'})
        if isinstance(rpc_result, Response):
            return rpc_result
        api_response = rpc_result

    day, time = lesson_string_to_dict(api_response['lesson'])

    # student list
    students = list()
    for each in api_response['student']:
        students.append([each['name'], each['sid'], each['deputy'], each['class']])

    # 给“文化素质类”等加上“课”后缀
    if api_response['type'][-1] != '课':
        api_response['type'] = api_response['type'] + '课'

    # 合班名称为数字时不展示合班名称
    show_heban = True
    if api_response['class'].isdigit():
        show_heban = False

    return render_template('course.html',
                           course_name=api_response['name'],
                           course_day=get_day_chinese(day),
                           course_time=get_time_chinese(time),
                           study_hour=api_response['hour'],
                           show_heban=show_heban,
                           heban_name=api_response['class'],
                           course_type=api_response['type'],
                           week=api_response['week_string'],
                           room=api_response['room'],
                           course_teacher=teacher_list_to_str(api_response['teacher']),
                           students=students,
                           student_count=len(api_response['student']),
                           current_semester=url_semester
                           )


def _empty_column_check(courses: dict) -> (bool, bool, bool):
    """检查是否周末和晚上有课，返回三个布尔值"""
    with elasticapm.capture_span('_empty_column_check'):
        # 空闲周末判断，考虑到大多数人周末都是没有课程的
        empty_weekend = True
        for cls_time in range(1, 7):
            for cls_day in range(6, 8):
                if (cls_day, cls_time) in courses:
                    empty_weekend = False

        # 空闲课程判断，考虑到大多数人11-12节都是没有课程的
        empty_6 = True
        for cls_day in range(1, 8):
            if (cls_day, 6) in courses:
                empty_6 = False
        empty_5 = True
        for cls_day in range(1, 8):
            if (cls_day, 5) in courses:
                empty_5 = False
    return empty_5, empty_6, empty_weekend


def _semester_calculate(current_semester: str, semester_list: list):
    """生成一个列表，每个元素是一个二元组，分别为学期字符串和是否为当前学期的布尔值"""
    with elasticapm.capture_span('semester_calculate'):
        available_semesters = []

        for each_semester in semester_list:
            if current_semester == each_semester:
                available_semesters.append([each_semester, True])
            else:
                available_semesters.append([each_semester, False])
    return available_semesters


def _teacher_list_fix(teachers: list):
    """修复老师职称“未定”，以及修复重复老师
    @:param teachers: api server 返回的教师列表
    @:return: teacher list that has been fixed
    """
    tids = []
    new_teachers = []
    for index, teacher in enumerate(teachers):
        if teacher['title'] == '未定':
            teacher['title'] = ''

        if teacher['tid'] in tids:
            continue
        else:
            tids.append(teacher['tid'])
            new_teachers.append(teacher)
    return new_teachers
