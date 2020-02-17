from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask import request, url_for, redirect


class BaseModelView(ModelView):
    can_delete = False  # disable model deletion
    page_size = 50  # the number of entries to display on the list view
    can_view_details = True

    # @expose('/')
    # def index(self):
    #     return self.render('admin/myindex.html')
    #
    # @expose('/test/')
    # def test(self):
    #     return self.render('admin/test.html')

    def is_accessible(self):
        return login.current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))