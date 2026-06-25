from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, jsonify, flash, current_app,
)
from functools import wraps
from app.auth_manager import AuthManager
from app.data_manager import DataManager
from app.email_service import send_notification_email

main_bp = Blueprint('main', __name__)


# ------------------------------------------------------------------
# Navigation Structure: Country → Department → Group
# ------------------------------------------------------------------

COUNTRIES = ['IN', 'DE']

DEPARTMENTS = {
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

GROUPS = {
    'EBA': [
        'EBA1',
        'EBA2',
        'EBA3',
        'EBA6',
    ],
    'EBB': [
        'EBB2',
        'EBB4',
        'EBB5',
        'EBB6',
        'EBB7',
    ],
    'EBD': [
        'EBD1',
        'EBD2',
        'EBD3',
        'EBD4',
        'EBD5',
        'EBD6',
    ],
    'ECP': [
        'ECP1',
        'ECP2',
        'ECP3',
        'ECP5',
    ],
    'ECT': [
        'ECT1',
        'ECT2',
        'ECT3',
    ],
    'EMT': [
        'EMT1',
        'EMT2',
        'EMT3',
    ],
    'ETA': [
        'ETA1',
        'ETA2',
        'ETA3',
        'ETA4',
        'ETA5',
        'ETA6',
        'ETA7',
        'ETA8',
        'ETA9',
    ],
    'ETE': [
        'ETE1',
        'ETE2',
    ],
    'EXP': [
        'EXP1',
        'EXP2',
        'EXP3',
        'EXP4',
        'EXP5',
    ],
}


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _dm():
    """Get a DataManager instance for the current app."""
    return DataManager(current_app.config['DATA_FILE'])


def _auth():
    """Get an AuthManager instance for the current app."""
    return AuthManager(current_app.config['USERS_FILE'])


def _current_scope():
    """Return the currently selected Country/Department/Group scope."""
    return {
        'country': session.get('country'),
        'department': session.get('department'),
        'group': session.get('group'),
    }


def _scope_selected():
    """Return True when Country, Department, and Group are selected."""
    scope = _current_scope()
    if scope.get('country') == 'DE':
        return True
    return all(scope.values())


def _scope_label():
    """Return a user-friendly label for the currently selected scope."""
    return DataManager.scope_label(_current_scope())


def _parse_int(value):
    """Parse an integer form or JSON value safely."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


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
        if session.get('country') != 'DE' and not session.get('department'):
            return redirect(url_for('main.select_department'))
        if session.get('country') != 'DE' and not session.get('group'):
            return redirect(url_for('main.select_group'))
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'nt_id' in session:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        nt_id = AuthManager.normalize_nt_id(request.form.get('nt_id'))
        password = request.form.get('password', '')

        if not nt_id:
            flash('Please enter your NT ID.', 'danger')
            return render_template('login.html', entered_nt_id=nt_id)

        if not password:
            flash('Please enter your password.', 'danger')
            return render_template('login.html', entered_nt_id=nt_id)

        admin_nt_id = AuthManager.normalize_nt_id(
            current_app.config['ADMIN_NT_ID']
        )
        if nt_id == admin_nt_id:
            if password == current_app.config['ADMIN_PASSWORD']:
                session.clear()
                session.permanent = True
                session['nt_id'] = nt_id
                session['display_name'] = 'Administrator'
                session['role'] = 'admin'
                flash(f'Welcome Admin ({nt_id})!', 'success')
                return redirect(url_for('main.select_country'))

            flash('Invalid admin password.', 'danger')
            return render_template('login.html', entered_nt_id=nt_id)

        if not AuthManager.is_valid_nt_id(nt_id):
            flash('NT ID must follow the format MPI2COB.', 'danger')
            return render_template('login.html', entered_nt_id=nt_id)

        user = _auth().authenticate_user(nt_id, password)
        if not user:
            flash('Invalid NT ID or password.', 'danger')
            return render_template('login.html', entered_nt_id=nt_id)

        session.clear()
        session.permanent = True
        session['nt_id'] = user['nt_id']
        session['display_name'] = user['name']
        session['email'] = user['email']
        session['phone'] = user['phone']
        session['role'] = 'user'
        flash(f"Welcome {user['name']} ({user['nt_id']})!", 'success')
        return redirect(url_for('main.select_country'))

    return render_template('login.html')


@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'nt_id' in session:
        return redirect(url_for('main.index'))

    form_data = {
        'nt_id': '',
        'name': '',
        'email': '',
        'phone': '',
    }

    if request.method == 'POST':
        form_data = {
            'nt_id': AuthManager.normalize_nt_id(request.form.get('nt_id')),
            'name': (request.form.get('name') or '').strip(),
            'email': (request.form.get('email') or '').strip(),
            'phone': (request.form.get('phone') or '').strip(),
        }
        password = request.form.get('password', '')
        admin_nt_id = AuthManager.normalize_nt_id(
            current_app.config['ADMIN_NT_ID']
        )

        if not AuthManager.is_valid_nt_id(form_data['nt_id']):
            flash('NT ID must follow the format KNA1COB.', 'danger')
            return render_template('register.html', form_data=form_data)

        if form_data['nt_id'] == admin_nt_id:
            flash('This NT ID is reserved for the admin account.', 'danger')
            return render_template('register.html', form_data=form_data)

        if not form_data['name']:
            flash('Name is required.', 'danger')
            return render_template('register.html', form_data=form_data)

        if not AuthManager.is_valid_email(form_data['email']):
            flash('Enter a valid email address.', 'danger')
            return render_template('register.html', form_data=form_data)

        if not AuthManager.is_valid_phone(form_data['phone']):
            flash('Enter a valid phone number.', 'danger')
            return render_template('register.html', form_data=form_data)

        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('register.html', form_data=form_data)

        if _auth().user_exists(form_data['nt_id']):
            flash('This NT ID is already registered.', 'danger')
            return render_template('register.html', form_data=form_data)

        _auth().register_user(
            form_data['nt_id'],
            form_data['name'],
            form_data['email'],
            form_data['phone'],
            password,
        )
        flash('Registration successful. Please log in with your NT ID and password.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html', form_data=form_data)


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
    if session.get('country') != 'DE' and not session.get('department'):
        return redirect(url_for('main.select_department'))
    if session.get('country') != 'DE' and not session.get('group'):
        return redirect(url_for('main.select_group'))
    cupboards = _dm().get_all_cupboards(_current_scope())
    return render_template(
        'dashboard.html',
        cupboards=cupboards,
        country=session['country'],
        department=session.get('department'),
        group=session.get('group'),
    )


# ------------------------------------------------------------------
# Selection Flow: Country → Department → Group
# ------------------------------------------------------------------

@main_bp.route('/select-country', methods=['GET', 'POST'])
@login_required
def select_country():
    if request.method == 'POST':
        country = request.form.get('country', '').strip()
        if country in COUNTRIES:
            session['country'] = country
            session.pop('department', None)
            session.pop('group', None)
            if country == 'DE':
                return redirect(url_for('main.dashboard'))
            return redirect(url_for('main.select_department'))
        flash('Invalid country selection.', 'danger')
    return render_template('select_country.html', countries=COUNTRIES)


@main_bp.route('/select-department', methods=['GET', 'POST'])
@login_required
def select_department():
    country = session.get('country')
    if not country:
        return redirect(url_for('main.select_country'))
    if country == 'DE':
        return redirect(url_for('main.dashboard'))
    depts = DEPARTMENTS.get(country, [])
    if request.method == 'POST':
        dept = request.form.get('department', '').strip()
        dept_codes = [code for code, _ in depts]
        if dept in dept_codes:
            session['department'] = dept
            session.pop('group', None)
            return redirect(url_for('main.select_group'))
        flash('Invalid department selection.', 'danger')
    return render_template('select_department.html', country=country, departments=depts)


@main_bp.route('/select-group', methods=['GET', 'POST'])
@login_required
def select_group():
    country = session.get('country')
    dept = session.get('department')
    if not country:
        return redirect(url_for('main.select_country'))
    if country == 'DE':
        return redirect(url_for('main.dashboard'))
    if not dept:
        return redirect(url_for('main.select_department'))
    groups = GROUPS.get(dept, [])
    if request.method == 'POST':
        group = request.form.get('group', '').strip()
        if group in groups:
            session['group'] = group
            return redirect(url_for('main.dashboard'))
        flash('Invalid group selection.', 'danger')
    return render_template(
        'select_group.html',
        country=country,
        dept=dept,
        groups=groups,
    )


# ------------------------------------------------------------------
# Lock / Unlock API (AJAX)
# ------------------------------------------------------------------

@main_bp.route('/api/toggle-lock', methods=['POST'])
@login_required
def toggle_lock():
    if not _scope_selected():
        return jsonify({'success': False,
                        'message': 'Select country, department, and group first.'}), 400

    data = request.get_json()
    cupboard_id = data.get('cupboard_id')
    item_id = data.get('item_id')
    nt_id = session.get('nt_id')
    cupboard_id = _parse_int(cupboard_id)

    if cupboard_id is None or not item_id:
        return jsonify({'success': False,
                        'message': 'Missing required fields'}), 400

    is_admin = session.get('role') == 'admin'
    result = _dm().toggle_lock(
        _current_scope(),
        cupboard_id,
        item_id,
        nt_id,
        is_admin,
    )

    if result is None:
        return jsonify({'success': False, 'message': 'Item not found'}), 404

    action, item_name, cupboard_name = result

    if action == 'admin_only_lock':
        return jsonify({
            'success': False,
            'message': (f'Only admin can return (lock) "{item_name}". '
                        'Users can only borrow (unlock) items.'),
        }), 403

    # --- Log to audit history ---
    _dm().log_action(action, item_name, cupboard_name, nt_id, _current_scope())

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
    if not _scope_selected():
        flash('Select country, department, and group before using the admin panel.', 'warning')
        return redirect(url_for('main.select_country'))

    cupboards = _dm().get_all_cupboards(_current_scope())
    return render_template(
        'admin.html',
        cupboards=cupboards,
        countries=COUNTRIES,
        country=session.get('country'),
        department=session.get('department'),
        departments_by_country=DEPARTMENTS,
        group=session.get('group'),
        groups_by_department=GROUPS,
        scope_label=_scope_label(),
    )


@main_bp.route('/admin/update-scope', methods=['POST'])
@admin_required
def update_admin_scope():
    country = request.form.get('country', '').strip().upper()
    if country not in COUNTRIES:
        flash('Select a valid country.', 'danger')
        return redirect(url_for('main.admin'))

    session['country'] = country

    if country == 'DE':
        session.pop('department', None)
        session.pop('group', None)
        flash('Admin scope updated to DE.', 'success')
        return redirect(url_for('main.admin'))

    department = request.form.get('department', '').strip().upper()
    department_codes = [code for code, _ in DEPARTMENTS.get(country, [])]
    if department not in department_codes:
        flash('Select a valid department for the chosen country.', 'danger')
        return redirect(url_for('main.admin'))

    group = request.form.get('group', '').strip().upper()
    if group not in GROUPS.get(department, []):
        flash('Select a valid group for the chosen department.', 'danger')
        return redirect(url_for('main.admin'))

    session['department'] = department
    session['group'] = group
    flash(f'Admin scope updated to {country} / {department} / {group}.', 'success')
    return redirect(url_for('main.admin'))


@main_bp.route('/admin/add-item', methods=['POST'])
@admin_required
def add_item():
    if not _scope_selected():
        flash('Select country, department, and group before creating materials.', 'warning')
        return redirect(url_for('main.select_country'))

    cupboard_id = _parse_int(request.form.get('cupboard_id'))
    item_name = request.form.get('item_name', '').strip()

    if cupboard_id is None:
        flash('Select a cupboard before creating a material or equipment item.', 'danger')
        return redirect(url_for('main.admin'))

    if not item_name:
        flash('Item name is required.', 'danger')
        return redirect(url_for('main.admin'))

    if _dm().add_item(_current_scope(), cupboard_id, item_name):
        flash(f'Item "{item_name}" added successfully.', 'success')
    else:
        flash('Failed to add item. Cupboard not found.', 'danger')
    return redirect(url_for('main.admin'))


@main_bp.route('/admin/remove-item', methods=['POST'])
@admin_required
def remove_item():
    if not _scope_selected():
        flash('Select country, department, and group before removing materials.', 'warning')
        return redirect(url_for('main.select_country'))

    cupboard_id = _parse_int(request.form.get('cupboard_id'))
    item_id = request.form.get('item_id')

    if cupboard_id is None or not item_id:
        flash('Invalid item removal request.', 'danger')
        return redirect(url_for('main.admin'))

    if _dm().remove_item(_current_scope(), cupboard_id, item_id):
        flash('Item removed successfully.', 'success')
    else:
        flash('Failed to remove item.', 'danger')
    return redirect(url_for('main.admin'))


@main_bp.route('/admin/add-cupboard', methods=['POST'])
@admin_required
def add_cupboard():
    if not _scope_selected():
        flash('Select country, department, and group before creating cupboards.', 'warning')
        return redirect(url_for('main.select_country'))

    cupboard_name = request.form.get('cupboard_name', '').strip()

    if not cupboard_name:
        flash('Cupboard name is required.', 'danger')
        return redirect(url_for('main.admin'))

    if _dm().add_cupboard(_current_scope(), cupboard_name):
        flash(f'Cupboard "{cupboard_name}" added successfully.', 'success')
    else:
        flash('Failed to add cupboard.', 'danger')
    return redirect(url_for('main.admin'))


@main_bp.route('/admin/remove-cupboard', methods=['POST'])
@admin_required
def remove_cupboard():
    if not _scope_selected():
        flash('Select country, department, and group before removing cupboards.', 'warning')
        return redirect(url_for('main.select_country'))

    cupboard_id = _parse_int(request.form.get('cupboard_id'))

    if cupboard_id is None:
        flash('Invalid cupboard removal request.', 'danger')
        return redirect(url_for('main.admin'))

    if _dm().remove_cupboard(_current_scope(), cupboard_id):
        flash('Cupboard removed successfully.', 'success')
    else:
        flash('Failed to remove cupboard.', 'danger')
    return redirect(url_for('main.admin'))
