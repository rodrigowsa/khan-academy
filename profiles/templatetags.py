import os
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from webapp2_extras import jinja2

from profiles import focus_graph, activity_graph, exercises_over_time_graph, exercise_problems_graph, exercise_progress_graph, recent_activity
from profiles import class_exercises_over_time_graph, class_progress_report_graph, class_energy_points_per_minute_graph, class_time_graph

from urlparse import urlunparse
from urllib import urlencode

import template_cached
register = template_cached.create_template_register()

@register.inclusion_tag("profiles/graph_control.html")
def profile_graph_control():
    return {}

def render_graph_html_and_context(filename, context):
    path = os.path.join(os.path.dirname(__file__), filename)
    return {"html": template.render(path, context), "context": context}

# Profile Graph Types
@register.simple_tag
def profile_activity_graph(user_data_student, dt_start, dt_end, tz_offset):
    return render_graph_html_and_context("activity_graph.html", activity_graph.activity_graph_context(user_data_student, dt_start, dt_end, tz_offset))
@register.simple_tag
def profile_focus_graph(user_data_student, dt_start, dt_end):
    return render_graph_html_and_context("focus_graph.html", focus_graph.focus_graph_context(user_data_student, dt_start, dt_end))
@register.simple_tag
def profile_exercises_over_time_graph(user_data_student):
    return render_graph_html_and_context("exercises_over_time_graph.html", exercises_over_time_graph.exercises_over_time_graph_context(user_data_student))
@register.simple_tag
def profile_exercise_problems_graph(user_data_student, exid):
    return render_graph_html_and_context("exercise_problems_graph.html", exercise_problems_graph.exercise_problems_graph_context(user_data_student, exid))
@register.simple_tag
def profile_exercise_progress_graph(user_data_student):
    return render_graph_html_and_context("exercise_progress_graph.html", exercise_progress_graph.exercise_progress_graph_context(user_data_student))
# End profile graph types

# Class profile graph types
@register.simple_tag
def class_profile_exercises_over_time_graph(user_data_coach, student_list):
    return render_graph_html_and_context("class_exercises_over_time_graph.html", class_exercises_over_time_graph.class_exercises_over_time_graph_context(user_data_coach, student_list))
@register.simple_tag
def class_profile_progress_report_graph(user_data_coach, student_list):
    return render_graph_html_and_context("class_progress_report_graph.html", class_progress_report_graph.class_progress_report_graph_context(user_data_coach, student_list))
@register.simple_tag
def class_profile_energy_points_per_minute_graph(user_data_coach, student_list):
    return render_graph_html_and_context("class_energy_points_per_minute_graph.html", class_energy_points_per_minute_graph.class_energy_points_per_minute_graph_context(user_data_coach, student_list))
@register.simple_tag
def class_profile_energy_points_per_minute_update(user_data_coach, student_list):
    return class_energy_points_per_minute_graph.class_energy_points_per_minute_update(user_data_coach, student_list)
@register.simple_tag
def class_profile_time_graph(user_data_coach, dt, tz_offset, student_list):
    return render_graph_html_and_context("class_time_graph.html", class_time_graph.class_time_graph_context(user_data_coach, dt, tz_offset, student_list))
# End class profile graph types

def get_graph_url(graph_type, student, coach, list_id):
    qs = {}
    if student:
        qs['student_email'] = student.email
    if coach:
        qs['coach_email'] = coach.email
    if list_id:
        qs['list_id'] = list_id

    urlpath = "/profile/graph/%s" % graph_type
    return urlunparse(('', '', urlpath, '', urlencode(qs), ''))

@register.inclusion_tag("profiles/graph_link.html")
def profile_graph_link(user_data, graph_name, graph_type, selected_graph_type):
    selected = (graph_type == selected_graph_type)
    return {
        "url": get_graph_url(graph_type, user_data, None, None),
        "user_data_student": user_data,
        "graph_name": graph_name,
        "selected": selected
    }

@register.inclusion_tag("profiles/graph_link.html")
def profile_class_graph_link(user_data_coach, graph_name, graph_type, selected_graph_type, list_id):
    selected = (graph_type == selected_graph_type)
    return {
        "url": get_graph_url(graph_type, None, user_data_coach, list_id),
        "graph_name": graph_name,
        "selected": selected,
    }

@register.inclusion_tag("profiles/graph_date_picker.html")
def profile_graph_date_picker(user_data, graph_type):
    return {
        "user_data": user_data,
        "graph_type": graph_type
    }

@register.inclusion_tag("profiles/graph_calendar_picker.html")
def profile_graph_calendar_picker(user_data, graph_type):
    return {
        "user_data": user_data,
        "graph_type": graph_type
    }

@register.inclusion_tag("profiles/exercise_progress_block.html")
def profile_exercise_progress_block(exercise_data, exercise):
    return {
        'chart_link': exercise_data[exercise.name]["chart_link"],
        'ex_link': exercise_data[exercise.name]["ex_link"],
        'hover': exercise_data[exercise.name]["hover"],
        'color': exercise_data[exercise.name]["color"],
        'short_name': exercise_data[exercise.name]["short_name"]
    }

@register.simple_tag
def profile_recent_activity(user_data, view="standard"):
    context = recent_activity.recent_activity_context(user_data)
    context["view"] = view

    # TODO: nicer way to do these inclusion tag thingies for jinja
    return jinja2.get_jinja2().render_template("profiles/recent_activity.html", **context)

@register.inclusion_tag("profiles/recent_activity_entry_badge.html")
def profile_recent_activity_entry_badge(user_data_student, recent_activity_entry, view="standard"):
    return {
        "recent_activity": recent_activity_entry,
        "student_email": user_data_student.email,
        "view": view
    }
@register.inclusion_tag("profiles/recent_activity_entry_exercise.html")
def profile_recent_activity_entry_exercise(user_data_student, recent_activity_entry, view="standard"):
    return {
        "recent_activity": recent_activity_entry,
        "student_email": user_data_student.email,
        "view": view
    }
@register.inclusion_tag("profiles/recent_activity_entry_video.html")
def profile_recent_activity_entry_video(user_data_student, recent_activity_entry, view="standard"):
    return {
        "recent_activity": recent_activity_entry,
        "student_email": user_data_student.email,
        "view": view
    }
