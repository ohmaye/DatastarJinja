"""
Menu data configuration for the application navigation.
This module defines the navigation structure that will be passed to templates.
"""

MENU_DATA = [
    {
        'title': 'EF Tokyo School',
        'menu_var': 'school_menu',
        'menu_items': [
            {'icon': 'book-open', 'text': 'Courses', 'url': '/school/courses'},
            {'icon': 'user', 'text': 'Teachers', 'url': '/school/teachers'},
            {'icon': 'star', 'text': 'Teacher Preferences', 'url': '/'},
            {'icon': 'home', 'text': 'Rooms', 'url': '/school/rooms'},
            {'icon': 'clock', 'text': 'Timeslots', 'url': '/school/timeslots'}
        ]
    },
    {
        'title': 'Survey Creation',
        'menu_var': 'survey_menu',
        'menu_items': [
            {'icon': 'activity', 'text': 'Survey Levels', 'url': '/survey/levels'},
            {'icon': 'activity', 'text': 'Survey Course Groups', 'url': '/survey/groups'},
            {'icon': 'activity', 'text': 'Survey Tables', 'url': '/survey/tables'},
            {'icon': 'activity', 'text': 'Survey Images', 'url': '/survey/images'},
            {'icon': 'activity', 'text': 'Config Survey', 'url': '/survey/surveys'}
        ]
    },
    {
        'title': 'SPIN Cycle',
        'menu_var': 'spin_menu',
        'menu_items': [
            {'icon': 'monitor', 'text': 'SPIN Classes', 'url': '/spin/spin_classes'},
            {'icon': 'users', 'text': 'Students', 'url': '/spin/students'},
            {'icon': 'users', 'text': 'Selections', 'url': '/spin/selections'},
            {'icon': 'file-text', 'text': 'by Course', 'url': '/spin/by_course'},
            {'icon': 'bar-chart', 'text': 'by Level', 'url': '/spin/by_level'},
            {'icon': 'user-check', 'text': 'Assign Students', 'url': '/spin/assign_students/'},
            {'icon': 'calendar', 'text': 'Assign Classes', 'url': '/spin/assign_classes/'},
            {'icon': 'layout-dashboard', 'text': 'Dashboard', 'url': '/'}
        ]
    },
    {
        'title': 'Student',
        'menu_var': 'student_menu',
        'menu_items': [
            {'icon': 'file-text', 'text': 'Survey', 'url': '/student/survey', 'target': '_blank'},
            {'icon': 'award', 'text': 'YuTA Teaching Assistant', 'url': '/'}
        ]
    },
    {
        'title': 'Teacher',
        'menu_var': 'teacher_menu',
        'menu_items': [
            {'icon': 'help-circle', 'text': 'Ask Kozue', 'url': '/'}
        ]
    }
] 