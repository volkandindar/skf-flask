import logging.config, os, datetime
from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from shutil import copyfile
from skf.database import db
from skf.database.users import User
from skf.database.groups import Group
from skf.database.privileges import Privilege
from skf.database.kb_items import KBItem
from skf.database.code_items import CodeItem
from skf.database.checklist_types import ChecklistType
from skf.database.checklist_category import ChecklistCategory
from skf.initial_data import load_initial_data

logging.config.fileConfig('logging.conf')
log = logging.getLogger(__name__)

def clear_db():
    log.info("Clearing the database")
    try:
        db.drop_all()
        db.session.commit()
    except:
        log.info("Error occurred clearing the database")
        db.session.rollback()
        raise


def init_db(testing=False):
    """Initializes the database.""" 
    try:
        log.info("Initializing the database")
        db.create_all()
        prerequisits()
        init_md_code_examples()
        init_md_testing_examples()
        init_md_knowledge_base()
        load_initial_data()
    except:
        db.session.remove()
        log.info("Database is already existsing, nothing to do")


def clean_db(testing=False):
    """Clean and Initializes the database.""" 
    log.info("Clean and Initializing the database")
    clear_db()
    db.create_all()
    prerequisits()
    init_md_code_examples()
    init_md_testing_examples()
    init_md_knowledge_base()
    load_initial_data()
    db.session.commit()


def update_db():
    """Update the database."""
    log.info("Update the database")
    KBItem.query.delete()
    CodeItem.query.delete()
    db.session.commit()
    init_md_code_examples()
    init_md_knowledge_base()


def init_md_knowledge_base():
    """Converts markdown knowledge-base items to DB."""
    kb_dir = os.path.join(current_app.root_path, 'markdown/knowledge_base/')
    #kb_dir_types = ['web', 'mobile']
    kb_dir_types = ['web']

    try:
        checklist_category_id = 0
        for kb_type in kb_dir_types:
            checklist_category_id += 1
            for filename in os.listdir(kb_dir+kb_type):
                if filename.endswith(".md"):
                    name_raw = filename.split("-")
                    kb_id = name_raw[0].replace("_", " ")
                    title = name_raw[3].replace("_", " ")
                    file = os.path.join(kb_dir+kb_type, filename)
                    data = open(file, 'r')
                    file_content = data.read()
                    data.close()
                    content = file_content.translate(str.maketrans({"'":  r"''"}))
                    try:
                        item = KBItem(title, content, kb_id)
                        item.checklist_category_id = checklist_category_id
                        if (kb_id == "1"):
                            item.checklist_category_id = None
                        db.session.add(item)
                        db.session.commit()
                    except IntegrityError as e:
                        raise
        log.info("Initialized the markdown knowledge-base.")
        return True
    except:
        raise


def init_md_code_examples():
    """Converts markdown code-example items to DB."""
    kb_dir = os.path.join(current_app.root_path, 'markdown/code_examples/web/')
    code_langs = ['asp-needs-reviewing', 'java-needs-reviewing', 'php-needs-reviewing', 'flask', 'django-needs-reviewing', 'go-needs-reviewing', 'ruby-needs-reviewing', 'nodejs-express-needs-reviewing']
    try:
        for lang in code_langs:
            for filename in os.listdir(kb_dir+lang):
                if filename.endswith(".md"):
                    name_raw = filename.split("-")
                    title = name_raw[3].replace("_", " ")
                    file = os.path.join(kb_dir+lang, filename)
                    data = open(file, 'r')
                    file_content = data.read()
                    data.close()
                    content_escaped = file_content.translate(str.maketrans({"'":  r"''", "-":  r"", "#":  r""}))
                    try:
                        item = CodeItem(content_escaped, title, lang)
                        item.checklist_category_id = 1
                        db.session.add(item)
                        db.session.commit()
                    except IntegrityError as e:
                        print(e)
                        pass
        log.info("Initialized the markdown code-examples.")
        return True
    except:
        raise


def init_md_testing_examples():
    """Converts markdown testing code-example items to DB."""
    kb_dir = os.path.join(current_app.root_path, 'markdown/code_examples/web/')
    code_langs = ['testing']
    try:
        for lang in code_langs:
            for filename in sorted(os.listdir(kb_dir+lang)):
                if filename.endswith(".md"):
                    name_raw = filename.split("-")
                    title = name_raw[3].replace("_", " ")
                    file = os.path.join(kb_dir+lang, filename)
                    data = open(file, 'r')
                    file_content = data.read()
                    data.close()
                    content_escaped = file_content.translate(str.maketrans({"'":  r"''", "-":  r"", "#":  r""}))
                    try:
                        item = CodeItem(content_escaped, title, lang)
                        item.checklist_category_id = 1
                        db.session.add(item)
                        db.session.commit()
                    except IntegrityError as e:
                        print(e)
                        pass
        log.info("Initialized the markdown testing-examples.")
        return True
    except:
        raise


def prerequisits():
    try:
        category = ChecklistCategory("Web applications", "category for web collection")
        db.session.add(category)
        db.session.commit()
        category = ChecklistCategory("Mobile applications", "category for mobile collection")
        db.session.add(category)
        db.session.commit()
        category = ChecklistCategory("Custom checklist", "category for custom checklist collection")
        db.session.add(category)
        db.session.commit()
        log.info("Initialized the prerequisits.")
        return True
    except:
        raise
