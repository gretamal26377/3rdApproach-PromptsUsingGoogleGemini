from ..shared.models import User, db
import logging
import bleach

def get_users_logic():
    users = User.query.all()
    users_data = [{'id': user.id, 'username': user.username, 'email': user.email, 'is_admin': user.is_admin} for user in users]
    return users_data, 200

def get_user_logic(user_id):
    user = User.query.get_or_404(user_id)
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_admin': user.is_admin
    }
    return user_data, 200

def update_user_logic(user_id, data):
    user = User.query.get_or_404(user_id)
    if not data:
        return {'message': 'No data provided'}, 400
    try:
        if 'username' in data:
            user.username = bleach.clean(data['username'], strip=True)
        if 'email' in data:
            user.email = bleach.clean(data['email'], strip=True)
        if 'is_admin' in data:
            user.is_admin = data['is_admin']
        db.session.commit()
        return {'message': 'User updated successfully'}, 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating user: {e}")
        return {'message': 'Failed to update user'}, 500

def delete_user_logic(user_id):
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        return {'message': 'User deleted successfully'}, 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting user: {e}")
        return {'message': 'Failed to delete user'}, 500
