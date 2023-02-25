from flask_login import UserMixin
from apps import db, login_manager


@login_manager.user_loader
def load_user(id):
    """get the user id when user sign in"""
    return Account.query.get(id)


class Account(db.Model, UserMixin):
    """
    User object: id, username, email_address, password
    """
    __tablename__ = 'gooddreamer_user_data'

    id = db.Column('id', db.Integer, primary_key=True)
    fullname = db.Column('fullname', db.String)
    email = db.Column('email', db.String)
    is_guest = db.Column('is_guest', db.Integer)
    password_hash = db.Column('password', db.String)

    @property
    def password(self):
        """User password property"""
        return self.password

    @password.setter
    def password(self, plain_text_password):
        """
        change plain text password into hash password into databse
        """
        self.password_hash = plain_text_password


class GooddreamerNovel(db.Model, UserMixin):
    """ Novel obejct """
    __tablename__ = 'gooddreamer_novel'
    __table_args__ = (
        db.ForeignKeyConstraint(['author_id'], ['gooddreamer_user_data.id']),
        db.ForeignKeyConstraint(
            ['published_by'], ['gooddreamer_user_data.id']),
        {'schema': None}
    )
    __mapper_args__ = {
        'polymorphic_identity': 'gooddreamer_novel'
    }

    id = db.Column('id', db.Integer, primary_key=True)
    author_id = db.Column('author_id', db.Integer)
    published_by = db.Column('published_by', db.Integer)
    novel_title = db.Column('novel_title', db.String)
    publication = db.Column('publication', db.Integer)


class GooddreamerNovelChapter(db.Model, UserMixin):
    """gooddreamer novel chapter object"""
    __tablename__ = 'gooddreamer_novel_chapter'
    __table_args__ = (
        db.ForeignKeyConstraint(['novel_id'], ['gooddreamer_novel.id']),
        {'schema': None}
    )
    __mapper_args__ = {
        'polymorphic_identity': 'gooddreamer_novel_chapter'
    }

    id = db.Column('id', db.Integer, primary_key=True)
    novel_id = db.Column('novel_id', db.Integer)
    chapter_title = db.Column('chapter_title', db.String)
    word_count = db.Column('word_count', db.Integer)
    publication = db.Column('publication', db.Integer)


class GooddreamerUserNovelProgression(db.Model, UserMixin):
    """gooddreamer user novel progression object"""
    __tablename__ = 'gooddreamer_user_novel_progression'
    __table_args__ = (
        db.ForeignKeyConstraint(['user_id'], ['gooddreamer_user_data.id']),
        db.ForeignKeyConstraint(['novel_id'], ['gooddreamer_novel.id']),
        db.ForeignKeyConstraint(['curr_chapter_id'], [
                                'gooddreamer_novel_chapter.id']),
        {'schema': None}
    )
    __mapper_args__ = {
        'polymorphic_identity': 'gooddreamer_user_novel_progression'
    }

    id = db.Column('id', db.Integer, primary_key=True)
    user_id = db.Column('user_id', db.Integer)
    novel_id = db.Column('novel_id', db.Integer)
    curr_chapter_id = db.Column(
        'curr_chapter_id', db.Integer)
    create_at = db.Column('created_at', db.DateTime)


class GooddreamerUserChapterProgression(db.Model, UserMixin):
    """gooddreamer user chapter progression object"""
    __tablename__ = 'gooddreamer_user_chapter_progression'
    __table_args__ = (
        db.ForeignKeyConstraint(
            ['np_id'], ['gooddreamer_user_novel_progression.id']),
        db.ForeignKeyConstraint(['user_id'], ['gooddreamer_user_data.id']),
        db.ForeignKeyConstraint(
            ['chapter_id'], ['gooddreamer_novel_chapter.id']),
        {'schema': None}
    )
    __mapper_args__ = {
        'polymorphic_identity': 'gooddreamer_user_chapter_progression'
    }

    id = db.Column('id', db.Integer, primary_key=True)
    np_id = db.Column('np_id', db.Integer)
    user_id = db.Column('user_id', db.Integer)
    chapter_id = db.Column('chapter_id', db.Integer)


class GooddreamerNovelTransaction(db.Model, UserMixin):
    """gooddreamer novel transaction object"""
    __tablename__ = 'gooddreamer_novel_transaction'
    __table_args__ = (
        db.ForeignKeyConstraint(['user_id'], ['gooddreamer_user_data.id']),
        db.ForeignKeyConstraint(['novel_id'], ['gooddreamer_novel.id']),
        {'schema': None}
    )
    __mapper_args__ = {
        'polymorphic_identity': 'gooddreamer_novel_transaction'
    }

    id = db.Column('id', db.Integer, primary_key=True)
    user_id = db.Column('user_id', db.Integer)
    novel_id = db.Column('novel_id', db.Integer)
    created_at = db.Column('created_at', db.DateTime)


class DataCategory(db.Model, UserMixin):
    """data catgory object"""
    __tablename__ = 'data_category'
    __mapper_args__ = {
        'polymorphic_identity': 'data_category'
    }

    id = db.Column('id', db.Integer, primary_key=True)
    category_name = db.Column('category_name', db.String)


class PivotNovelCategory(db.Model, UserMixin):
    """gooddreamer novel catrgory object"""
    __tablename__ = 'pivot_novel_category'
    __table_args__ = (
        db.ForeignKeyConstraint(['novel_id'], ['gooddreamer_novel.id']),
        db.ForeignKeyConstraint(['category_id'], ['data_category.id']),
        {'schema': None}
    )
    __mapper_args__ = {
        'polymorphic_identity': 'pivot_novel_category'
    }

    novel_id = db.Column('novel_id', db.Integer, primary_key=True)
    category_id = db.Column('category_id', db.Integer)


class GooddreamerTransaction(db.Model, UserMixin):
    """Gooddreamer transaction coin object"""

    __tablename__ = 'gooddreamer_transaction'
    __table_args__ = (
        db.ForeignKeyConstraint(['user_id'], ['gooddreamer_user_data.id']),
        {'schema': None}
    )
    __mapper_args__ = {
        'polymorphic_identity': 'gooddreamer_transaction'
    }

    id = db.Column('id', db.Integer, primary_key=True)
    user_id = db.Column('user_id', db.Integer)
    transaction_status = db.Column('transaction_status', db.Integer)
    transaction_coin_value = db.Column('transaction_coin_value', db.Integer)
    created_at = db.Column('created_at', db.DateTime)


class GooddreamerTransactionDetails(db.Model, UserMixin):
    """gooddreamer transaction detail object"""

    __tablename__ = 'gooddreamer_transaction_details'
    __table_args__ = (
        db.ForeignKeyConstraint(['transaction_id'], [
                                'gooddreamer_transaction.id']),
        {'schema': None}
    )
    __mapper_args__ = {
        'polymorphic_identity': 'gooddreamer_transacion_details'
    }

    id = db.Column('id', db.Integer, primary_key=True)
    transaction_id = db.Column('transaction_id', db.Integer)
    package_price = db.Column('package_price', db.Integer)
    package_fee = db.Column('package_fee', db.Integer)


class AppsflyerAggregatedData(db.Model, UserMixin):
    """appsflyer aggregated data"""

    __tablename__ = 'appsflyer_aggregated_data'
    __mapper_args__ = {
        'polymorphic_identity': 'appsflyer_aggregated_data'
    }

    date = db.Column('date', db.Date, primary_key=True)
    installs = db.Column('installs', db.Integer)
    af_preview_novel_counter = db.Column(
        'af_preview_novel_counter', db.Integer)
    af_register_unique = db.Column('af_register_unique', db.Integer)
    af_topup_coin_unique = db.Column('af_topup_coin_unique', db.Integer)
    af_coin_purchase_counter = db.Column('af_coin_purchase_counter', db.Integer)
    media_source = db.Column('media_source', db.String)
    campaign = db.Column('campaign', db.String)
