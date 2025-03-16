from sqlalchemy.orm import joinedload

from app import FormCategory
from app.models import Form, Submission, db
from app.helpers.exceptions import LogicException
from app.helpers.decorators import transaction


def get_form_by_id(form_id):
    form = Form.query.filter_by(id=form_id, deleted_at=None).first()
    if not form:
        raise LogicException("Форма не найдена", 404)
    return form


def get_forms():
    return Form.query.filter_by(deleted_at=None).all()


def get_form_categories():
    return FormCategory.query.filter_by(deleted_at=None).all()


def get_category_by_id(category_id):
    category = FormCategory.query.filter_by(id=category_id, deleted_at=None).first()

    if not category:
        raise LogicException("Категория не найдена", 404)

    return category


@transaction
def create_form(user, category, data):
    new_form = Form(
        name=data["name"],
        available_params=data.get("available_params", []),
        fields=data.get("fields", []),
        creator_id=user.id,
        category_id=category.id
    )
    db.session.add(new_form)
    return new_form


@transaction
def update_form(form, data):
    form.name = data.get("name", form.name)
    form.available_params = data.get("available_params", form.available_params)
    form.fields = data.get("fields", form.fields)
    return form


@transaction
def delete_form(user, form):
    form.deleted_at = db.func.now()
    form.deleter_id = user.id


def get_submission_by_id(sub_id):
    sub = Submission.query.filter_by(id=sub_id, deleted_at=None).first()
    if not sub:
        raise LogicException("Ответ не найден", 404)
    return sub


def get_object_submissions(object):
    return (
        db.session.query(Submission)
        # Подгружаем связанные данные:
        .options(
            joinedload(Submission.form).joinedload(Form.category)
        )
        .filter(
            Submission.object_id == object.id,
            Submission.deleted_at.is_(None)
        )
        .all()
    )


@transaction
def create_submission(user, form, object, data):
    new_submission = Submission(
        form_id=form.id,
        object_id=object.id,
        params=data.get("params", {}),
        fields=data.get("fields", {}),
        showoff_attributes=data.get("showoff_attributes", {}),
        creator_id=user.id,
        form_name=form.name,
        form_category_name=form.category.name,
        is_approved=user.role != 'student'
    )
    db.session.add(new_submission)

    if not new_submission.is_approved:
        object.has_unapproved_submissions = True
        print("set unapproved")

    return new_submission


@transaction
def update_submission(submission, data):
    submission.params = data.get("params", submission.params)
    submission.fields = data.get("fields", submission.fields)
    submission.showoff_attributes = data.get("showoff_attributes", submission.showoff_attributes)
    return submission


@transaction
def delete_submission(user, submission):
    submission.deleted_at = db.func.now()
    submission.deleter_id = user.id

    if all(submission.is_approved for submission in submission.object.submissions):
        submission.object.has_unapproved_submissions = False


@transaction
def approve_submission(user, submission):
    submission.is_approved = True
    submission.approved_by = user

    if all(submission.is_approved for submission in submission.object.submissions):
        submission.object.has_unapproved_submissions = False

    return submission
