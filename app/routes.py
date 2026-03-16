from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, jsonify, flash, current_app,
)
from functools import wraps
from app.data_manager import DataManager
from app.email_service import send_notification_email

main_bp = Blueprint('main', __name__)


# ------------------------------------------------------------------
# Navigation Structure: Country → Business Unit → Chapter
# ------------------------------------------------------------------

COUNTRIES = ['IN', 'DE']

BUSINESS_UNITS = {
    'IN': [
        ('EBA', 'Automotive Aftermarket'),
        ('EBB', 'Bosch Diagnostics'),
        ('EBD', 'Bosch Security'),
        ('ECP', 'Connected Mobility'),
        ('ECT', 'Drive Systems'),
        ('EMT', 'Engineering & Technology'),
        ('ETA', 'Mobility Solutions'),
        ('ETE', 'Power Tools'),
        ('EXP', 'Research & Advance Engineering'),
    ],
    'DE': [
        ('EBA', 'Automotive Aftermarket'),
        ('EBB', 'Bosch Diagnostics'),
        ('EBD', 'Bosch Security'),
        ('ECP', 'Connected Mobility'),
        ('ECT', 'Drive Systems'),
        ('EMT', 'Engineering & Technology'),
        ('ETA', 'Mobility Solutions'),
        ('ETE', 'Power Tools'),
        ('EXP', 'Research & Advance Engineering'),
    ],
}

CHAPTERS = {
    'EBA': [
        'EBA Chapter 1',
        'EBA Chapter 2',
        'EBA Chapter 3',
        'EBA Chapter 4',
        'EBA Chapter 5',
    ],
    'EBB': [
        'EBB1',
        'EBB2',
        'EBB3',
        'EBB4',
        'EBB5',
    ],
    'EBD': [
        'EBD Chapter 1',
        'EBD Chapter 2',
        'EBD Chapter 3',
        'EBD Chapter 4',
        'EBD Chapter 5',
    ],
    'ECP': [
        'ECP Chapter 1',
        'ECP Chapter 2',
        'ECP Chapter 3',
        'ECP Chapter 4',
        'ECP Chapter 5',
    ],
    'ECT': [
        'ECT Chapter 1',
        'ECT Chapter 2',
        'ECT Chapter 3',
        'ECT Chapter 4',
        'ECT Chapter 5',
    ],
    'EMT': [
        'EMT Chapter 1',
        'EMT Chapter 2',
        'EMT Chapter 3',
        'EMT Chapter 4',
        'EMT Chapter 5',
    ],
    'ETA': [
        'ETA Chapter 1',
        'ETA Chapter 2',
        'ETA Chapter 3',
        'ETA Chapter 4',
        'ETA Chapter 5',
    ],
    'ETE': [
        'ETE Chapter 1',
        'ETE Chapter 2',
        'ETE Chapter 3',
        'ETE Chapter 4',
        'ETE Chapter 5',
    ],
    'EXP': [
        'EXP Chapter 1',
        'EXP Chapter 2',
        'EXP Chapter 3',
        'EXP Chapter 4',
        'EXP Chapter 5',
    ],
}


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _dm():
    """Get a DataManager instance for the current app."""
    return DataManager(current_app.config['DATA_FILE'])


def login_required(f):
    """Decorator: redirect to login if not authenticated."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'nt_id' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    """Decorator: only allow admin users."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'nt_id' not in session:
            return redirect(url_for('main.login'))
        if session.get('role') != 'admin':
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return wrapper


# ------------------------------------------------------------------
# Authentication routes
# ------------------------------------------------------------------

@main_bp.route('/')
def index():
    if 'nt_id' in session:
        if not session.get('country'):
            return redirect(url_for('main.select_country'))
        if not session.get('business_unit'):
            return redirect(url_for('main.select_bu'))
        if not session.get('chapter'):
            return redirect(url_for('main.select_chapter'))
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nt_id = request.form.get('nt_id', '').strip().upper()
        is_admin = request.form.get('is_admin') == 'on'
        password = request.form.get('password', '')

        if not nt_id:
            flash('Please enter your NT ID.', 'danger')
            return render_template('login.html')

        if is_admin:
            admin_pw = current_app.config['ADMIN_PASSWORD']
            if password == admin_pw:
                session.permanent = True
                session['nt_id'] = nt_id
                session['role'] = 'admin'
                flash(f'Welcome Admin ({nt_id})!', 'success')
                return redirect(url_for('main.select_country'))
            else:
                flash('Invalid admin password.', 'danger')
                return render_template('login.html')
        else:
            session.permanent = True
            session['nt_id'] = nt_id
            session['role'] = 'user'
            flash(f'Welcome {nt_id}!', 'success')
            return redirect(url_for('main.select_country'))

    return render_template('login.html')


@main_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))


# ------------------------------------------------------------------
# Dashboard
# ------------------------------------------------------------------

@main_bp.route('/dashboard')
@login_required
def dashboard():
    if not session.get('country'):
        return redirect(url_for('main.select_country'))
    if not session.get('business_unit'):
        return redirect(url_for('main.select_bu'))
    if not session.get('chapter'):
        return redirect(url_for('main.select_chapter'))
    cupboards = _dm().get_all_cupboards()
    return render_template(
        'dashboard.html',
        cupboards=cupboards,
        country=session['country'],
        business_unit=session['business_unit'],
        chapter=session['chapter'],
    )


# ------------------------------------------------------------------
# Selection Flow: Country → Business Unit → Chapter
# ------------------------------------------------------------------

@main_bp.route('/select-country', methods=['GET', 'POST'])
@login_required
def select_country():
    if request.method == 'POST':
        country = request.form.get('country', '').strip()
        if country in COUNTRIES:
            session['country'] = country
            session.pop('business_unit', None)
            session.pop('chapter', None)
            return redirect(url_for('main.select_bu'))
        flash('Invalid country selection.', 'danger')
    return render_template('select_country.html', countries=COUNTRIES)


@main_bp.route('/select-bu', methods=['GET', 'POST'])
@login_required
def select_bu():
    country = session.get('country')
    if not country:
        return redirect(url_for('main.select_country'))
    bus = BUSINESS_UNITS.get(country, [])
    if request.method == 'POST':
        bu = request.form.get('business_unit', '').strip()
        bu_codes = [code for code, _ in bus]
        if bu in bu_codes:
            session['business_unit'] = bu
            session.pop('chapter', None)
            return redirect(url_for('main.select_chapter'))
        flash('Invalid business unit selection.', 'danger')
    return render_template('select_bu.html', country=country, business_units=bus)


@main_bp.route('/select-chapter', methods=['GET', 'POST'])
@login_required
def select_chapter():
    country = session.get('country')
    bu = session.get('business_unit')
    if not country:
        return redirect(url_for('main.select_country'))
    if not bu:
        return redirect(url_for('main.select_bu'))
    chapters = CHAPTERS.get(bu, [])
    if request.method == 'POST':
        chapter = request.form.get('chapter', '').strip()
        if chapter in chapters:
            session['chapter'] = chapter
            return redirect(url_for('main.dashboard'))
        flash('Invalid chapter selection.', 'danger')
    return render_template(
        'select_chapter.html',
        country=country,
        bu=bu,
        chapters=chapters,
    )


# ------------------------------------------------------------------
# Lock / Unlock API (AJAX)
# ------------------------------------------------------------------

@main_bp.route('/api/toggle-lock', methods=['POST'])
@login_required
def toggle_lock():
    data = request.get_json()
    cupboard_id = data.get('cupboard_id')
    item_id = data.get('item_id')
    nt_id = session.get('nt_id')

    if not cupboard_id or not item_id:
        return jsonify({'success': False,
                        'message': 'Missing required fields'}), 400

    is_admin = session.get('role') == 'admin'
    result = _dm().toggle_lock(int(cupboard_id), item_id, nt_id, is_admin)

    if result is None:
        return jsonify({'success': False, 'message': 'Item not found'}), 404

    action, item_name, cupboard_name = result

    if action == 'not_authorized':
        return jsonify({
            'success': False,
            'message': (f'You cannot return "{item_name}" because it was '
                        f'borrowed by another user.'),
        }), 403

    # --- Log to audit history ---
    _dm().log_action(action, item_name, cupboard_name, nt_id)

    # --- Send email notification ---
    # NOTE: Email functionality is disabled until SMTP details are provided.
    # Uncomment the block below once SMTP configuration is ready in config.py.
    email_sent = False
    # try:
    #     user_email = f"{nt_id}{current_app.config['EMAIL_DOMAIN']}"
    #     send_notification_email(
    #         action=action,
    #         item_name=item_name,
    #         cupboard_name=cupboard_name,
    #         nt_id=nt_id,
    #         user_email=user_email,
    #         admin_email=current_app.config['ADMIN_EMAIL'],
    #         manager_email=current_app.config['MANAGER_EMAIL'],
    #         sender_email=current_app.config['SENDER_EMAIL'],
    #         smtp_config={
    #             'server': current_app.config['SMTP_SERVER'],
    #             'port': current_app.config['SMTP_PORT'],
    #             'use_tls': current_app.config['SMTP_USE_TLS'],
    #             'username': current_app.config['SMTP_USERNAME'],
    #             'password': current_app.config['SMTP_PASSWORD'],
    #         },
    #     )
    #     email_sent = True
    # except Exception as e:
    #     print(f"[EMAIL ERROR] {e}")

    if action == 'locked':
        message = f'Item "{item_name}" has been returned (locked) by {nt_id}.'
    else:
        message = f'Item "{item_name}" has been borrowed (unlocked) by {nt_id}.'

    return jsonify({
        'success': True,
        'action': action,
        'message': message,
        'email_sent': email_sent,
        'nt_id': nt_id,
    })


# ------------------------------------------------------------------
# History / Audit Log
# ------------------------------------------------------------------

@main_bp.route('/history')
@admin_required
def history():
    nt_id_filter = request.args.get('nt_id', '').strip()
    action_filter = request.args.get('action', '').strip()
    records = _dm().get_history(
        nt_id_filter=nt_id_filter or None,
        action_filter=action_filter or None,
    )
    return render_template(
        'history.html',
        records=records,
        nt_id_filter=nt_id_filter,
        action_filter=action_filter,
    )


# ------------------------------------------------------------------
# Admin routes
# ------------------------------------------------------------------

@main_bp.route('/admin')
@admin_required
def admin():
    cupboards = _dm().get_all_cupboards()
    return render_template('admin.html', cupboards=cupboards)


@main_bp.route('/admin/add-item', methods=['POST'])
@admin_required
def add_item():
    cupboard_id = int(request.form.get('cupboard_id'))
    item_name = request.form.get('item_name', '').strip()

    if not item_name:
        flash('Item name is required.', 'danger')
        return redirect(url_for('main.admin'))

    if _dm().add_item(cupboard_id, item_name):
        flash(f'Item "{item_name}" added successfully.', 'success')
    else:
        flash('Failed to add item. Cupboard not found.', 'danger')
    return redirect(url_for('main.admin'))


@main_bp.route('/admin/remove-item', methods=['POST'])
@admin_required
def remove_item():
    cupboard_id = int(request.form.get('cupboard_id'))
    item_id = request.form.get('item_id')

    if _dm().remove_item(cupboard_id, item_id):
        flash('Item removed successfully.', 'success')
    else:
        flash('Failed to remove item.', 'danger')
    return redirect(url_for('main.admin'))


@main_bp.route('/admin/add-cupboard', methods=['POST'])
@admin_required
def add_cupboard():
    cupboard_name = request.form.get('cupboard_name', '').strip()

    if not cupboard_name:
        flash('Cupboard name is required.', 'danger')
        return redirect(url_for('main.admin'))

    if _dm().add_cupboard(cupboard_name):
        flash(f'Cupboard "{cupboard_name}" added successfully.', 'success')
    else:
        flash('Failed to add cupboard.', 'danger')
    return redirect(url_for('main.admin'))


@main_bp.route('/admin/remove-cupboard', methods=['POST'])
@admin_required
def remove_cupboard():
    cupboard_id = int(request.form.get('cupboard_id'))

    if _dm().remove_cupboard(cupboard_id):
        flash('Cupboard removed successfully.', 'success')
    else:
        flash('Failed to remove cupboard.', 'danger')
    return redirect(url_for('main.admin'))
