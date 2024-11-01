# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from modsec_manager import list_rules, toggle_rule, save_rule, get_current_mode, set_mode
from config import ACCESS_LOG_PATH, ERROR_LOG_PATH, AUDIT_LOG_PATH
import tailer  # Ensure the `tailer` package is installed with `pip install tailer`
import subprocess

app = Flask(__name__)
app.secret_key = 'a3f0b8c42fa67a5de4e0b8f21d7b3a76'

#@app.route('/')
#def home():
#    return render_template('home.html')

@app.route('/', methods=['GET', 'POST'])
def home():
    current_mode = get_current_mode()

    if request.method == 'POST':
        selected_mode = request.form.get('mode')
        if set_mode(selected_mode):
            flash(f"ModSecurity mode updated to '{selected_mode}'.")
        else:
            flash("Failed to update ModSecurity mode.")
        return redirect(url_for('home'))

    return render_template('home.html', current_mode=current_mode)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Helper function to tail logs
def tail_log(file_path, lines=50):
    try:
        output = subprocess.check_output(['tail', '-n', str(lines), file_path], text=True)
        return output.splitlines()
    except Exception as e:
        return [f"Error reading log file: {e}"]

# Routes for logs
@app.route('/logs')
def logs_home():
    return render_template('logs.html')

@app.route('/logs/access')
def access_logs():
    lines = request.args.get('lines', default=50, type=int)
    log_content = tail_log(ACCESS_LOG_PATH, lines)
    return render_template('log_viewer.html', log_content=log_content, log_type="Access", lines=lines)

@app.route('/logs/error')
def error_logs():
    lines = request.args.get('lines', default=50, type=int)
    log_content = tail_log(ERROR_LOG_PATH, lines)
    return render_template('log_viewer.html', log_content=log_content, log_type="Error", lines=lines)

@app.route('/logs/audit')
def audit_logs():
    lines = request.args.get('lines', default=50, type=int)
    log_content = tail_log(AUDIT_LOG_PATH, lines)
    return render_template('log_viewer.html', log_content=log_content, log_type="Audit", lines=lines)

@app.route('/rules')
def rules():
    enabled_rules, disabled_rules = list_rules()
    return render_template('rules.html', enabled_rules=enabled_rules, disabled_rules=disabled_rules)

@app.route('/configuration', methods=['GET', 'POST'])
def configuration():
    modsecurity_conf_path = '/etc/nginx/modsec/modsecurity.conf'
    crs_conf_path = '/etc/nginx/modsec/crs/crs-setup.conf'

    if request.method == 'POST':
        # Save updated contents from the form
        modsecurity_conf_content = request.form['modsecurity_conf']
        crs_conf_content = request.form['crs_conf']

        with open(modsecurity_conf_path, 'w') as f:
            f.write(modsecurity_conf_content)
        with open(crs_conf_path, 'w') as f:
            f.write(crs_conf_content)

        flash("Configurations updated successfully.")
        return redirect(url_for('configuration'))

    # Load current configuration contents
    with open(modsecurity_conf_path) as f:
        modsecurity_conf_content = f.read()
    with open(crs_conf_path) as f:
        crs_conf_content = f.read()

    return render_template(
        'configuration.html',
        modsecurity_conf=modsecurity_conf_content,
        crs_conf=crs_conf_content
    )

@app.route('/toggle_rule/<filename>')
def toggle_rule_view(filename):
    enabled_rules, disabled_rules = list_rules()  # Unpack the two lists properly
    all_rules = enabled_rules + disabled_rules      # Combine them to search for the rule
    
    rule = next((rule for rule in all_rules if rule['filename'] == filename), None)
    if rule:
        toggle_rule(filename, not rule['enabled'])
        flash(f"Rule '{filename}' {'enabled' if not rule['enabled'] else 'disabled'} successful!")
    return redirect(url_for('rules'))

@app.route('/edit_rule/<filename>', methods=['GET', 'POST'])
def edit_rule(filename):
    enabled_rules, disabled_rules = list_rules()  # Unpack the two lists properly
    all_rules = enabled_rules + disabled_rules      # Combine them to search for the rule

    rule = next((rule for rule in all_rules if rule['filename'] == filename), None)
    if not rule:
        flash("Rule not found.")
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        content = request.form['content']
        save_rule(filename, content)
        flash(f"Rule '{filename}' updated successfully.")
        return redirect(url_for('dashboard'))
    
    return render_template('rule_editor.html', rule=rule)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
