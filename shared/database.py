from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, sessionmaker

db = SQLAlchemy()
db_session = None

def init_db(app):
    global db_session
    db.init_app(app)
    
    # Create tables within app context
    with app.app_context():
        # Import models to ensure they are known to SQLAlchemy
        from shared.models import Users, Birthdays, AuditLogs
        
        # Create all tables
        db.create_all()
        
        # Setup session
        db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=db.engine))
        
    return db_session

def get_db():
    global db_session
    if db_session is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return db_session

def shutdown_session(exception=None):
    global db_session
    if db_session:
        db_session.remove()
