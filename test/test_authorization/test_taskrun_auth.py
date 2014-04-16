# -*- coding: utf8 -*-
# This file is part of PyBossa.
#
# Copyright (C) 2013 SF Isle of Man Limited
#
# PyBossa is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyBossa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with PyBossa.  If not, see <http://www.gnu.org/licenses/>.

from base import web, model, Fixtures, db, redis_flushall, assert_not_raises
from pybossa.auth import require
from nose.tools import assert_raises
from werkzeug.exceptions import Forbidden, Unauthorized
from mock import patch
from test_authorization import mock_current_user




class TestTaskrunAuthorization:

    mock_anonymous = mock_current_user()
    mock_authenticated = mock_current_user(anonymous=False, admin=False, id=2)
    mock_admin = mock_current_user(anonymous=False, admin=True, id=1)


    def setUp(self):
        model.rebuild_db()
        self.root, self.user1, self.user2 = Fixtures.create_users()
        db.session.add_all([self.root, self.user1, self.user2])
        self.app = Fixtures.create_app('')
        self.app.owner = self.root
        db.session.add(self.app)
        db.session.commit()
        self.task = model.task.Task(app_id=self.app.id, state='0', n_answers=10)
        self.task.app = self.app
        db.session.add(self.task)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        redis_flushall()



    @patch('pybossa.auth.current_user', new=mock_anonymous)
    @patch('pybossa.auth.taskrun.current_user', new=mock_anonymous)
    def test_anonymous_user_create_first_taskrun(self):
        """Test anonymous user can create a taskrun for a given task if he
        hasn't already done it"""

        with web.app.test_request_context('/'):
            taskrun = model.task_run.TaskRun(app_id=self.app.id,
                                    task_id=self.task.id,
                                    user_ip='127.0.0.0',
                                    info="some taskrun info")
            assert_not_raises(Exception,
                          getattr(require, 'taskrun').create,
                          taskrun)


    @patch('pybossa.auth.current_user', new=mock_anonymous)
    @patch('pybossa.auth.taskrun.current_user', new=mock_anonymous)
    def test_anonymous_user_create_repeated_taskrun(self):
        """Test anonymous user cannot create a taskrun for a task to which
        he has previously posted a taskrun"""

        with web.app.test_request_context('/'):
            taskrun1 = model.task_run.TaskRun(app_id=self.app.id,
                                    task_id=self.task.id,
                                    user_ip='127.0.0.0',
                                    info="some taskrun info")
            db.session.add(taskrun1)
            db.session.commit()
            taskrun2 = model.task_run.TaskRun(app_id=self.app.id,
                                    task_id=self.task.id,
                                    user_ip='127.0.0.0',
                                    info="a different taskrun info")
            assert_raises(Forbidden,
                        getattr(require, 'taskrun').create,
                        taskrun2)

            # But the user can still create taskruns for different tasks
            task2 = model.task.Task(app_id=self.app.id, state='0', n_answers=10)
            task2.app = self.app
            db.session.add(task2)
            db.session.commit()
            taskrun3 = model.task_run.TaskRun(app_id=self.app.id,
                                    task_id=task2.id,
                                    user_ip='127.0.0.0',
                                    info="some taskrun info")
            assert_not_raises(Exception,
                          getattr(require, 'taskrun').create,
                          taskrun3)


    @patch('pybossa.auth.current_user', new=mock_authenticated)
    @patch('pybossa.auth.taskrun.current_user', new=mock_authenticated)
    def test_authenticated_user_create_first_taskrun(self):
        """Test authenticated user can create a taskrun for a given task if he
        hasn't already done it"""

        with web.app.test_request_context('/'):
            taskrun = model.task_run.TaskRun(app_id=self.app.id,
                                    task_id=self.task.id,
                                    user_id=self.mock_authenticated.id,
                                    info="some taskrun info")
            assert_not_raises(Exception,
                          getattr(require, 'taskrun').create,
                          taskrun)


    @patch('pybossa.auth.current_user', new=mock_authenticated)
    @patch('pybossa.auth.taskrun.current_user', new=mock_authenticated)
    def test_authenticated_user_create_repeated_taskrun(self):
        """Test authenticated user cannot create a taskrun for a task to which
        he has previously posted a taskrun"""

        with web.app.test_request_context('/'):
            taskrun1 = model.task_run.TaskRun(app_id=self.app.id,
                                    task_id=self.task.id,
                                    user=self.user1,
                                    info="some taskrun info")
            db.session.add(taskrun1)
            db.session.commit()
            taskrun2 = model.task_run.TaskRun(app_id=self.app.id,
                                    task_id=self.task.id,
                                    user=self.user1,
                                    info="a different taskrun info")
            assert_raises(Forbidden, getattr(require, 'taskrun').create, taskrun2)

            # But the user can still create taskruns for different tasks
            task2 = model.task.Task(app_id=self.app.id, state='0', n_answers=10)
            task2.app = self.app
            db.session.add(task2)
            db.session.commit()
            taskrun3 = model.task_run.TaskRun(app_id=self.app.id,
                                    task_id=task2.id,
                                    user_id=self.mock_authenticated.id,
                                    info="some taskrun info")
            assert_not_raises(Exception,
                          getattr(require, 'taskrun').create,
                          taskrun3)


    @patch('pybossa.auth.current_user', new=mock_anonymous)
    @patch('pybossa.auth.taskrun.current_user', new=mock_anonymous)
    def test_anonymous_user_read(self):
        """Test anonymous user can read any taskrun"""

        with web.app.test_request_context('/'):
            anonymous_taskrun = model.task_run.TaskRun(app_id=self.app.id,
                                    task_id=self.task.id,
                                    user_ip='127.0.0.0',
                                    info="some taskrun info")
            user_taskrun = model.task_run.TaskRun(app_id=self.app.id,
                                    task_id=self.task.id,
                                    user_id=self.root.id,
                                    info="another taskrun info")

            assert_not_raises(Exception,
                          getattr(require, 'taskrun').read,
                          anonymous_taskrun)
            assert_not_raises(Exception,
                          getattr(require, 'taskrun').read,
                          user_taskrun)


    @patch('pybossa.auth.current_user', new=mock_authenticated)
    @patch('pybossa.auth.taskrun.current_user', new=mock_authenticated)
    def test_authenticated_user_read(self):
        """Test authenticated user can read any taskrun"""

        with web.app.test_request_context('/'):
            anonymous_taskrun = model.task_run.TaskRun(app_id=self.app.id,
                                    task_id=self.task.id,
                                    user_ip='127.0.0.0',
                                    info="some taskrun info")
            other_users_taskrun = model.task_run.TaskRun(app_id=self.app.id,
                                    task_id=self.task.id,
                                    user_id=self.root.id,
                                    info="a different taskrun info")
            own_taskrun = model.task_run.TaskRun(app_id=self.app.id,
                                    task_id=self.task.id,
                                    user_id=self.mock_authenticated.id,
                                    info="another taskrun info")

            assert_not_raises(Exception,
                          getattr(require, 'taskrun').read,
                          anonymous_taskrun)
            assert_not_raises(Exception,
                          getattr(require, 'taskrun').read,
                          other_users_taskrun)
            assert_not_raises(Exception,
                          getattr(require, 'taskrun').read,
                          own_taskrun)


    @patch('pybossa.auth.current_user', new=mock_anonymous)
    @patch('pybossa.auth.taskrun.current_user', new=mock_anonymous)
    def test_anonymous_user_update_anoymous_taskrun(self):
        """Test anonymous users cannot update an anonymously posted taskrun"""

        with web.app.test_request_context('/'):
            anonymous_taskrun = model.task_run.TaskRun(app_id=self.app.id,
                                    task_id=self.task.id,
                                    user_ip='127.0.0.0',
                                    info="some taskrun info")

            assert_raises(Unauthorized,
                          getattr(require, 'taskrun').update,
                          anonymous_taskrun)


    @patch('pybossa.auth.current_user', new=mock_authenticated)
    @patch('pybossa.auth.taskrun.current_user', new=mock_authenticated)
    def test_authenticated_user_update_anonymous_taskrun(self):
        """Test authenticated users cannot update an anonymously posted taskrun"""

        with web.app.test_request_context('/'):
            anonymous_taskrun = model.task_run.TaskRun(app_id=self.app.id,
                                    task_id=self.task.id,
                                    user_ip='127.0.0.0',
                                    info="some taskrun info")

            assert_raises(Forbidden,
                          getattr(require, 'taskrun').update,
                          anonymous_taskrun)


    @patch('pybossa.auth.current_user', new=mock_admin)
    @patch('pybossa.auth.taskrun.current_user', new=mock_admin)
    def test_admin_update_anonymous_taskrun(self):
        """Test admins cannot update anonymously posted taskruns"""

        with web.app.test_request_context('/'):
            anonymous_taskrun = model.task_run.TaskRun(app_id=self.app.id,
                                    task_id=self.task.id,
                                    user_ip='127.0.0.0',
                                    info="some taskrun info")

            assert_raises(Forbidden,
                          getattr(require, 'taskrun').update,
                          anonymous_taskrun)


    @patch('pybossa.auth.current_user', new=mock_anonymous)
    @patch('pybossa.auth.taskrun.current_user', new=mock_anonymous)
    def test_anonymous_user_update_user_taskrun(self):
        """Test anonymous user cannot update taskruns posted by authenticated users"""
        with web.app.test_request_context('/'):
            user_taskrun = model.task_run.TaskRun(app_id=self.app.id,
                                    task_id=self.task.id,
                                    user_id=self.root.id,
                                    info="some taskrun info")

            assert_raises(Unauthorized,
                          getattr(require, 'taskrun').update,
                          user_taskrun)


    @patch('pybossa.auth.current_user', new=mock_authenticated)
    @patch('pybossa.auth.taskrun.current_user', new=mock_authenticated)
    def test_authenticated_user_update_other_users_taskrun(self):
        """Test authenticated user cannot update any taskrun"""

        with web.app.test_request_context('/'):
            own_taskrun = model.task_run.TaskRun(app_id=self.app.id,
                                    task_id=self.task.id,
                                    user_id=self.mock_authenticated.id,
                                    info="some taskrun info")
            other_users_taskrun = model.task_run.TaskRun(app_id=self.app.id,
                                    task_id=self.task.id,
                                    user_id=self.root.id,
                                    info="a different taskrun info")

            assert_raises(Forbidden,
                          getattr(require, 'taskrun').update,
                          own_taskrun)
            assert_raises(Forbidden,
                          getattr(require, 'taskrun').update,
                          other_users_taskrun)


    @patch('pybossa.auth.current_user', new=mock_admin)
    @patch('pybossa.auth.taskrun.current_user', new=mock_admin)
    def test_admin_update_user_taskrun(self):
        """Test admins cannot update taskruns posted by authenticated users"""

        with web.app.test_request_context('/'):
                user_taskrun = model.task_run.TaskRun(app_id=self.app.id,
                                        task_id=self.task.id,
                                        user_id=self.user1.id,
                                        info="some taskrun info")

                assert_raises(Forbidden,
                              getattr(require, 'taskrun').update,
                              user_taskrun)


    @patch('pybossa.auth.current_user', new=mock_anonymous)
    @patch('pybossa.auth.taskrun.current_user', new=mock_anonymous)
    def test_anonymous_user_delete_anonymous_taskrun(self):
        """Test anonymous users cannot delete an anonymously posted taskrun"""

        with web.app.test_request_context('/'):
            anonymous_taskrun = model.task_run.TaskRun(app_id=self.app.id,
                                    task_id=self.task.id,
                                    user_ip='127.0.0.0',
                                    info="some taskrun info")

            assert_raises(Unauthorized,
                          getattr(require, 'taskrun').delete,
                          anonymous_taskrun)


    @patch('pybossa.auth.current_user', new=mock_authenticated)
    @patch('pybossa.auth.taskrun.current_user', new=mock_authenticated)
    def test_authenticated_user_delete_anonymous_taskrun(self):
        """Test authenticated users cannot delete an anonymously posted taskrun"""

        with web.app.test_request_context('/'):
                    anonymous_taskrun = model.task_run.TaskRun(app_id=self.app.id,
                                            task_id=self.task.id,
                                            user_ip='127.0.0.0',
                                            info="some taskrun info")

                    assert_raises(Forbidden,
                                  getattr(require, 'taskrun').delete,
                                  anonymous_taskrun)


    @patch('pybossa.auth.current_user', new=mock_admin)
    @patch('pybossa.auth.taskrun.current_user', new=mock_admin)
    def test_admin_delete_anonymous_taskrun(self):
        """Test admins can delete anonymously posted taskruns"""

        with web.app.test_request_context('/'):
            anonymous_taskrun = model.task_run.TaskRun(app_id=self.app.id,
                                    task_id=self.task.id,
                                    user_ip='127.0.0.0',
                                    info="some taskrun info")

            assert_not_raises(Exception,
                          getattr(require, 'taskrun').delete,
                          anonymous_taskrun)

    @patch('pybossa.auth.current_user', new=mock_anonymous)
    @patch('pybossa.auth.taskrun.current_user', new=mock_anonymous)
    def test_anonymous_user_delete_user_taskrun(self):
        """Test anonymous user cannot delete taskruns posted by authenticated users"""

        with web.app.test_request_context('/'):
            user_taskrun = model.task_run.TaskRun(app_id=self.app.id,
                                    task_id=self.task.id,
                                    user_id=self.root.id,
                                    info="some taskrun info")

            assert_raises(Unauthorized,
                      getattr(require, 'taskrun').delete,
                      user_taskrun)

    @patch('pybossa.auth.current_user', new=mock_authenticated)
    @patch('pybossa.auth.taskrun.current_user', new=mock_authenticated)
    def test_authenticated_user_delete_other_users_taskrun(self):
        """Test authenticated user cannot delete a taskrun if it was created
        by another authenticated user, but can delete his own taskruns"""

        with web.app.test_request_context('/'):
            own_taskrun = model.task_run.TaskRun(app_id=self.app.id,
                                    task_id=self.task.id,
                                    user_id=self.mock_authenticated.id,
                                    info="some taskrun info")
            other_users_taskrun = model.task_run.TaskRun(app_id=self.app.id,
                                    task_id=self.task.id,
                                    user_id=self.root.id,
                                    info="a different taskrun info")

            assert_not_raises(Exception,
                      getattr(require, 'taskrun').delete,
                      own_taskrun)
            assert_raises(Forbidden,
                      getattr(require, 'taskrun').delete,
                      other_users_taskrun)


    @patch('pybossa.auth.current_user', new=mock_admin)
    @patch('pybossa.auth.taskrun.current_user', new=mock_admin)
    def test_admin_delete_user_taskrun(self):
        """Test admins can delete taskruns posted by authenticated users"""

        with web.app.test_request_context('/'):
            user_taskrun = model.task_run.TaskRun(app_id=self.app.id,
                                    task_id=self.task.id,
                                    user_id=self.user1.id,
                                    info="some taskrun info")

            assert_not_raises(Exception,
                      getattr(require, 'taskrun').delete,
                      user_taskrun)